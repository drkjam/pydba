"""Support for PostgreSQL database interactions."""
import os
import socket
import logging
import subprocess
from contextlib import closing
from collections import namedtuple

import psycopg2

from pydba.exc import DatabaseError

log = logging.getLogger(__name__)


class PostgresDB(object):
    """
    An API for performing various database administration tasks on a PostgresDB server.
    """
    _conn_fields = [
        'datname', 'datid', 'pid', 'state', 'application_name', 'query', 'usename',
        'waiting', 'client_hostname', 'client_addr', 'client_port'
    ]

    Connection = namedtuple('Connection', _conn_fields)

    def __init__(self, host='localhost', port=5432, database='postgres', user=None, password=None,
                 sslmode=None, sslcert=None, sslkey=None, bin_path='/usr/local/bin'):
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
        bin_path: str, optional
            path to dir containing client binaries
        """
        self._connect_args = dict(
            application_name='pydba (psycopg2)',
            database=database, user=user, password=password,
            host=host, port=port,
            sslmode=sslmode, sslcert=sslcert, sslkey=sslkey,
        )
        self._bin_path = bin_path

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

    def _run_cmd(self, cmd, *args):
        cmd_line = [os.path.join(self._bin_path, cmd)] + list(args)
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
        """.format(fields=', '.join(self._conn_fields), datname=name)
        return list(self.Connection(**x) for x in self._iter_results(stmt))

    def kill_connections(self, name):
        """Drops all connections to the specified database."""
        log.info('killing all connections to database %s' % name)
        self._run_stmt("""
          select pg_terminate_backend(pid)
          from pg_stat_activity
          where datname = %r and pid <> pg_backend_pid()
        """ % name)

    def available(self):
        """Returns True if database server is running, False otherwise."""
        host = self._connect_args['host']
        port = self._connect_args['port']
        with closing(socket.socket()) as sock:
            try:
                sock.connect((host, port))
                return True
            except socket.error:
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
