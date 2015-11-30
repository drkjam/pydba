"""Support for PostgreSQL database interactions."""
import getpass
import os
import socket
import logging
import subprocess
from collections import namedtuple

import pexpect
import psycopg2

from pydba.exc import DatabaseError, CommandNotFoundError

log = logging.getLogger(__name__)


CONNECTION_FIELDS = [
    'datname', 'datid', 'pid', 'state', 'application_name', 'query',
    'usename', 'waiting', 'client_hostname', 'client_addr', 'client_port'
]

Connection = namedtuple('Connection', CONNECTION_FIELDS)


SETTINGS_FIELDS = [
    'name', 'setting', 'unit', 'category', 'short_desc', 'extra_desc',
    'context', 'vartype', 'source', 'min_val', 'max_val', 'enumvals',
    'boot_val', 'reset_val', 'sourcefile', 'sourceline'
]

Settings = namedtuple('Settings', SETTINGS_FIELDS)


class PostgresDB(object):
    """
    An API for performing various database administration tasks on a PostgresDB server.
    """
    _vartype_map = {
        'bool': lambda x: True if x == 'on' else False,
        'enum': lambda x: x,
        'integer': lambda x: int(x),
        'real': lambda x: float(x),
        'string': lambda x: x,
    }

    def __init__(self, host='localhost', port=5432, database='postgres', user=None, password=None,
                 sslmode=None, sslcert=None, sslkey=None, application_name='pydba (psycopg2)'):
        """
        Constructor.

        All arguments are optional and sensible defaults. Override using args depending on your needs.

        Parameters
        ----------
        host: str, optional
            remote server IP address or hostname
        port: int, optional
            remote server port
        database: str, optional
            name of database to connect to
        user: str
            name of user (with required admin privileges)
        password:
            password for user
        sslmode: str, optional
            mode for SSL connection
        sslcert: str, optional
            file path to SSL certificate for connection
        sslkey: str, optional
            file path to SSL key for connection
        application_name: str, optional
            allow user to specify the app name in the connection
        """
        if user is None:
            user = getpass.getuser()

        self._connect_args = dict(
            application_name=application_name,
            database=database, user=user, password=password,
            host=host, port=port,
            sslmode=sslmode, sslcert=sslcert, sslkey=sslkey,
        )

        self._bin_paths = {}

    def _run_stmt(self, stmt):
        with psycopg2.connect(**self._connect_args) as conn:
            conn.set_session(autocommit=True)
            with conn.cursor() as cur:
                cur.execute(stmt)
        log.info('done')

    def _iter_results(self, stmt):
        with psycopg2.connect(**self._connect_args) as conn:
            with conn.cursor() as cur:
                cur.execute(stmt)
                header = [col.name for col in cur.description]
                for row in cur:
                    yield dict(zip(header, row))

    def _path_for(self, cmd):
        if cmd in self._bin_paths:
            return self._bin_paths[cmd]
        else:
            path = pexpect.which(cmd)
            if path is None:
                raise CommandNotFoundError('failed to find path of %r' % cmd)
            self._bin_paths[cmd] = path
            return path

    def _run_cmd(self, cmd, *args):
        cmd_line = [self._path_for(cmd)] + list(args)
        log.info('running: %r' % cmd_line)
        proc = subprocess.Popen(cmd_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode:
            log.error(stderr)
        else:
            if stdout:
                log.error('unexpected output: ' + stdout)
            if stderr:
                log.info(stderr)
        log.info('done')

    def names(self):
        """Returns a list of all database names."""
        stmt = """
            select datname
            from pg_database
            where datistemplate = false
        """
        return [x['datname'] for x in self._iter_results(stmt)]

    def exists(self, name):
        """Returns True if named database exists, False otherwise."""
        return name in self.names()

    def create(self, name):
        """Creates a new database."""
        log.info('creating database %s' % name)
        self._run_stmt('create database %s' % name)

    def drop(self, name):
        """Drops an existing database."""
        log.info('dropping database %s' % name)
        self._run_stmt('drop database %s' % name)

    def rename(self, from_name, to_name):
        """Renames an existing database."""
        log.info('renaming database from %s to %s' % (from_name, to_name))
        self._run_stmt('alter database %s rename to %s' % (from_name, to_name))

    def connections(self, name):
        """Returns a list of existing connections to the named database."""
        stmt = """
            select {fields} from pg_stat_activity
            where datname = {datname!r} and pid <> pg_backend_pid()
        """.format(fields=', '.join(CONNECTION_FIELDS), datname=name)
        return list(Connection(**x) for x in self._iter_results(stmt))

    def kill_connections(self, name):
        """Drops all connections to the specified database."""
        log.info('killing all connections to database %s' % name)
        self._run_stmt("""
          select pg_terminate_backend(pid)
          from pg_stat_activity
          where datname = %r and pid <> pg_backend_pid()
        """ % name)

    def available(self, timeout=5):
        """Returns True if database server is running, False otherwise."""
        host = self._connect_args['host']
        port = self._connect_args['port']
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return True
        except socket.error:
            pass
        return False

    def dump(self, name, filename):
        """
        Saves the state of a database to a file.

        Parameters
        ----------
        name: str
            the database to be backed up.
        filename: str
            path to a file where database backup will be written.
        """
        if not self.exists(name):
            raise DatabaseError('database %s does not exist!')
        log.info('dumping %s to %s' % (name, filename))
        self._run_cmd('pg_dump', '--verbose', '--blobs', '--format=custom',
                      '--file=%s' % filename, name)

    def restore(self, name, filename):
        """
        Loads state of a backup file to a database.

        Note
        ----
        If database name does not exist, it will be created.

        Parameters
        ----------
        name: str
            the database to which backup will be restored.
        filename: str
            path to a file contain a postgres database backup.
        """
        if not self.exists(name):
            self.create(name)
        else:
            log.warn('overwriting contents of database %s' % name)
        log.info('restoring %s from %s' % (name, filename))
        self._run_cmd('pg_restore', '--verbose', '--dbname=%s' % name, filename)

    def _connect_options(self, name):
        if name is None:
            db_name = self._connect_args['database']
        else:
            db_name = name

        options = [
            ('dbname', db_name),
            ('user', self._connect_args['user']),
            ('host', self._connect_args['host']),
            ('port', self._connect_args['port']),
        ]

        if self._connect_args['sslmode'] is not None:
            options = options + [
                ('sslmode', self._connect_args['sslmode']),
                ('sslcert', os.path.expanduser(self._connect_args['sslcert'])),
                ('sslkey', os.path.expanduser(self._connect_args['sslkey'])),
            ]

        return options

    def connection_dsn(self, name=None):
        """
        Provides a connection string for database.

        Parameters
        ----------
        name: str, optional
            an override database name for the connection string.

        Returns
        -------
        str: the connection string (e.g. 'dbname=db1 user=user1 host=localhost port=5432')
        """
        return ' '.join("%s=%s" % (param, value) for param, value in self._connect_options(name))

    def connection_url(self, name=None):
        """
        Provides a connection string for database as a sqlalchemy compatible URL.

        NB - this doesn't include special arguments related to SSL connectivity (which are outside the scope
        of the connection URL format).

        Parameters
        ----------
        name: str, optional
            an override database name for the connection string.

        Returns
        -------
        str: the connection URL (e.g. postgresql://user1@localhost:5432/db1)
            """
        return 'postgresql://{user}@{host}:{port}/{dbname}'.format(**{k: v for k, v in self._connect_options(name)})

    def shell(self, expect=pexpect):
        """
        Connects the database client shell to the database.

        Parameters
        ----------
        expect_module: str
            the database to which backup will be restored.
        """
        dsn = self.connection_dsn()
        log.debug('connection string: %s' % dsn)
        child = expect.spawn('psql "%s"' % dsn)
        if self._connect_args['password'] is not None:
            child.expect('Password: ')
            child.sendline(self._connect_args['password'])
        child.interact()

    def settings(self):
        """Returns settings from the server."""
        stmt = "select {fields} from pg_settings".format(fields=', '.join(SETTINGS_FIELDS))
        settings = []
        for row in self._iter_results(stmt):
            row['setting'] = self._vartype_map[row['vartype']](row['setting'])
            settings.append(Settings(**row))
        return settings
