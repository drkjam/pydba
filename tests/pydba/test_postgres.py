import getpass
import tempfile

import pytest

from pydba import PostgresDB
from pydba.utils import temp_name, temp_db


@pytest.fixture(scope='module')
def pg():
    return PostgresDB()


def test_postgres_available(pg):
    assert pg.available()


def test_postgres_is_not_available():
    db = PostgresDB(host='pydbadmin_fake_hostname')
    assert not db.available(timeout=0.25)


def test_postgres_db_names(pg):
    db_names = pg.names()
    assert 'postgres' in db_names


def test_postgres_db_exists(pg):
    assert pg.exists('postgres')


def test_postgres_create_rename_and_drop(pg):
    name1 = temp_name()
    name2 = temp_name()

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
    with temp_db(pg) as db_name:
        fp = tempfile.NamedTemporaryFile()
        pg.dump(db_name, fp.name)

        pg.drop(db_name)
        assert not pg.exists(db_name)

        fp.seek(0)
        pg.restore(db_name, fp.name)
        assert pg.exists(db_name)


class FakeChild(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.password = None

    def expect(self, data):
        pass

    def sendline(self, line):
        self.password = line

    def interact(self):
        pass


class ExpectModule(object):
    def __init__(self):
        self.expect = None

    def spawn(self, cmd):
        self.expect = FakeChild(cmd)
        return self.expect


def test_shell(pg):
    fake_expect = ExpectModule()

    pg.shell(fake_expect)

    assert fake_expect.expect.cmd == 'psql ' \
        '"dbname=postgres user=' + getpass.getuser() + ' host=localhost port=5432"'


def test_shell_with_ssl_and_password_prompt():
    fake_expect = ExpectModule()

    the_password = 'password1234'

    pg = PostgresDB(user='foo', password=the_password,
                    sslmode='require', sslcert='test.pem', sslkey='test.key')
    pg.shell(fake_expect)

    assert fake_expect.expect.password == the_password

    assert fake_expect.expect.cmd == 'psql ' \
        '"dbname=postgres user=foo host=localhost port=5432 ' \
        'sslmode=require sslcert=test.pem sslkey=test.key"'


def test_settings(pg):
    assert [x.setting for x in pg.settings() if x.name == 'port'] == [5432]
