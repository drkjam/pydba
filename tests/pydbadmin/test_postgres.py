import pytest

from pydbadmin import Postgres


@pytest.fixture(scope='module')
def pgadmin():
    return Postgres()


def test_postgres_running(pgadmin):
    assert pgadmin.running()


def test_postgres_not_running():
    pgadmin = Postgres(host='pydbadmin_fake_hostname')
    assert not pgadmin.running()


def test_postgres_db_names(pgadmin):
    db_names = pgadmin.db_names()
    assert 'postgres' in db_names


def test_postgres_db_exists(pgadmin):
    assert pgadmin.db_exists('postgres')


def test_postgres_create_rename_and_drop(pgadmin):
    name1 = 'pydbadmin_test1'
    name2 = 'pydbadmin_test2'

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
