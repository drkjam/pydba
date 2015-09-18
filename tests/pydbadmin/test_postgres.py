from contextlib import contextmanager
import tempfile
import uuid

import pytest

from pydbadmin import Postgres


@pytest.fixture(scope='module')
def pgadmin():
    return Postgres()


def temp_db_name():
    #   Generate a globally unique database name.
    return 'a' + str(uuid.uuid4()).replace('-', '')


def test_postgres_running(pgadmin):
    assert pgadmin.running()


def test_postgres_not_running():
    pgadmin = Postgres(host='pydbadmin_fake_hostname')
    assert not pgadmin.running()


def test_postgres_db_names(pgadmin):
    db_names = pgadmin.list_dbs()
    assert 'postgres' in db_names


def test_postgres_db_exists(pgadmin):
    assert pgadmin.db_exists('postgres')


def test_postgres_create_rename_and_drop(pgadmin):
    name1 = temp_db_name()
    name2 = temp_db_name()

    assert not pgadmin.db_exists(name1)
    assert not pgadmin.db_exists(name2)

    pgadmin.create_db(name1)
    assert pgadmin.db_exists(name1)
    assert not pgadmin.db_exists(name2)

    pgadmin.rename_db(name1, name2)

    assert not pgadmin.db_exists(name1)
    assert pgadmin.db_exists(name2)

    pgadmin.drop_db(name2)

    assert not pgadmin.db_exists(name1)
    assert not pgadmin.db_exists(name2)


def test_postgres_list_connections(pgadmin):
    pgadmin.kill_connections('postgres')
    assert list(pgadmin.iter_connections('postgres')) == []


@contextmanager
def transient_db(db):
    name = temp_db_name()
    assert not db.db_exists(name)
    db.create_db(name)
    assert db.db_exists(name)
    try:
        yield name
    finally:
        db.drop_db(name)
        assert not db.db_exists(name)


def test_backup_and_restore(pgadmin):
    with transient_db(pgadmin) as db_name:
        fp = tempfile.NamedTemporaryFile()
        pgadmin.dump_db(db_name, fp.name)

        pgadmin.drop_db(db_name)
        assert not pgadmin.db_exists(db_name)

        fp.seek(0)
        pgadmin.restore_db(db_name, fp.name)
        assert pgadmin.db_exists(db_name)
