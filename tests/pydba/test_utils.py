import pytest
from pydba.exc import DatabaseError
from pydba.utils import temp_name, temp_db


def test_temp_name():
    assert temp_name() != temp_name()


def test_temp_db():
    class FakeStatefulDB(object):
        _exists = False

        def create(self, name):
            self._exists = True

        def drop(self, name):
            self._exists = False

        def exists(self, name):
            return self._exists

    db = FakeStatefulDB()
    with temp_db(db, 'foo') as name:
        assert name == 'foo'
        assert db.exists(name)
    assert not db.exists(name)

    with temp_db(db) as name:
        assert name.startswith('db')


def test_temp_db_failed_create():
    class FakeDB(object):
        def create(self, name):
            pass

        def exists(self, name):
            return False

    with pytest.raises(DatabaseError):
        with temp_db(FakeDB()):
            pass


def test_temp_db_failed_drop():
    class FakeDB(object):
        _exists = None

        def create(self, name):
            self._exists = True

        def drop(self, name):
            self._exists = True

        def exists(self, name):
            return self._exists

    with pytest.raises(DatabaseError):
        with temp_db(FakeDB()):
            pass
