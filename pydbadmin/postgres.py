from contextlib import closing
import socket
import logging

import psycopg2

log = logging.getLogger(__name__)


class Postgres(object):
    """
    Provides an API to a PostgreSQL server allowing the user to perform various database admin tasks.
    """
    def __init__(self, host='localhost', port=5432, database='postgres', user=None, password=None,
                 sslmode=None, sslcert=None, sslkey=None):
        self._connect_args = dict(
            application_name='pydbadmin (psycopg2)',
            database=database, user=user, password=password,
            host=host, port=port,
            sslmode=sslmode, sslcert=sslcert, sslkey=sslkey,
        )

    def db_names(self):
        """Returns a list of all current database names."""
        stmt = """
            select datname
            from pg_database
            where datistemplate = false;
        """
        return [x['datname'] for x in self._iter_results(stmt)]

    def db_exists(self, name):
        """Returns True if the named database exists, False otherwise."""
        return name in self.db_names()

    def _run_stmt(self, stmt):
        with psycopg2.connect(**self._connect_args) as conn:
            conn.set_session(autocommit=True)
            with conn.cursor() as cur:
                try:
                    cur.execute(stmt)
                except psycopg2.ProgrammingError, e:
                    log.exception(e)
        log.info('done')

    def _iter_results(self, stmt):
        with psycopg2.connect(**self._connect_args) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(stmt)
                    header = [col.name for col in cur.description]
                    for row in cur:
                        yield dict(zip(header, row))
                except psycopg2.ProgrammingError, e:
                    log.exception(e)

    def create_db(self, name):
        """Creates a new database."""
        log.info('creating database %s' % name)
        self._run_stmt('create database %s;' % name)

    def rename_db(self, from_name, to_name):
        """Rename an existing database."""
        log.info('renaming database from %s to %s' % (from_name, to_name))
        self._run_stmt('alter database %s rename to %s;' % (from_name, to_name))

    def drop_db(self, name):
        """Drop an existing database."""
        log.info('dropping database %s' % name)
        self._run_stmt('drop database %s;' % name)

    def iter_connections(self, name):
        """An iterator existing the list of existing connections to the specified database."""
        stmt = """
            select *
            from pg_stat_activity
            where datname = %r and pid <> pg_backend_pid()
        """ % name
        return self._iter_results(stmt)

    def kill_connections(self, name):
        """Drops all existing connections to the specified database."""
        log.info('killing all connections to database %s' % name)
        self._run_stmt("""
          select pg_terminate_backend(pid)
          from pg_stat_activity
          where datname = %r and pid <> pg_backend_pid()
        """ % name)

    def running(self):
        """Returns True if server is running, False otherwise."""
        host = self._connect_args['host']
        port = self._connect_args['port']
        with closing(socket.socket()) as sock:
            try:
                sock.connect((host, port))
                return True
            except socket.error, e:
                log.exception(e)
            return False
