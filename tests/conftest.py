import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    A fixture that enables database access for all tests.

    Parameters:
    - db: The database fixture provided by pytest.
    """
    pass
