from contextlib import contextmanager
import tempfile
import uuid

import pytest

from pydba import PostgresDB


@pytest.fixture(scope='module')
def pg():
    return PostgresDB()


def _temp_db_name():
    #   Generate a globally unique database name.
    return 'db' + str(uuid.uuid4()).replace('-', '')


@contextmanager
def _transient_db(db):
    name = _temp_db_name()
    assert not db.exists(name)
    db.create(name)
    assert db.exists(name)
    try:
        yield name
    finally:
        db.drop(name)
        assert not db.exists(name)


def test_postgres_available(pg):
    assert pg.available()


def test_postgres_is_not_available():
    db = PostgresDB(host='pydbadmin_fake_hostname')
    assert not db.available()


def test_postgres_db_names(pg):
    db_names = pg.names()
    assert 'postgres' in db_names


def test_postgres_db_exists(pg):
    assert pg.exists('postgres')


def test_postgres_create_rename_and_drop(pg):
    name1 = _temp_db_name()
    name2 = _temp_db_name()

    assert not pg.exists(name1)
    assert not pg.exists(name2)

    pg.create(name1)
    assert pg.exists(name1)
    assert not pg.exists(name2)

    pg.rename(name1, name2)

    assert not pg.exists(name1)
    assert pg.exists(name2)

    pg.drop(name2)

    assert not pg.exists(name1)
    assert not pg.exists(name2)


def test_postgres_list_connections(pg):
    pg.kill_connections('postgres')
    assert pg.connections('postgres') == []


def test_backup_and_restore(pg):
    with _transient_db(pg) as db_name:
        fp = tempfile.NamedTemporaryFile()
        pg.dump(db_name, fp.name)

        pg.drop(db_name)
        assert not pg.exists(db_name)

        fp.seek(0)
        pg.restore(db_name, fp.name)
        assert pg.exists(db_name)
