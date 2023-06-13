"""
Test custom Django managment commands.
"""
# this will be used to mock the behaviour for the database
# we need to be able to simulate when the database is returning response or not
from unittest.mock import patch, MagicMock

# this is one of the possible error that we might get when we try and
# connect to the database
from psycopg2 import OperationalError as Psycopg2Error

# helper function that allow us to call a command
from django.core.management import call_command
# this is another exception error that might get thrown by the database
from django.db.utils import OperationalError
# this is the simple base test case - not simulating the database
from django.test import SimpleTestCase

# this will be the command that we will be mocking, the check method is
# inhertited form BaseCommand that will allow us to check the status of
# the database


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):
    """Test commands."""

    # each function will get an extra argument, the mocked object that we
    # patched in the class
    def test_wait_for_db_ready(self, mock_patched_check: MagicMock) -> None:
        """Test waiting for database if database is ready."""
        # so this what it does is when the check from command is called we just
        # want to return a True value we are mocking so replace how the check
        # funtion will return a value
        mock_patched_check.return_value = True

        # checks also that the command is setup correctly and can be called
        # inside the django project
        call_command('wait_for_db')

        # now we want to check if the check function was actually called once,
        # with the default databse
        mock_patched_check.assert_called_once_with(databases=['default'])
    # adding a mock only for this function to mock the sleep function
    # this way the wait time from sleep method will not be enforced in the test
    # and it wont hold up or test execution
    # By patching time.sleep with a MagicMock object, the sleep function is
    # replaced with a mock implementation that doesn't actually pause the
    # execution for the specified time
    # Since the time.sleep function is mocked, when the code in the handle
    # method calls time.sleep(time_to_sleep), it doesn't actually pause the
    # execution for the specified time. Instead, it immediately continues to
    # the next iteration of the loop.

    @patch('time.sleep')
    def test_wait_for_db_delay(self, mock_patched_sleep: MagicMock,
                               mock_patched_check: MagicMock) -> None:
        """Testing when there is a delay in starting, checking if the database
        is ready. If it is not ready we want to delay a few seconds and try
        again. Test waiting for database when getting OperationalError."""
        # so when we mocking the check function, and we want to raise some
        # exception like whne the database wasent ready, and the way ot mkae it
        # happen with the mock is use the side_effect, if we pass an exception
        # than the mocking library knows we shuold raise the exception, if we
        # pass a boolean value it will return a boolean value If you pass in an
        # iterable, it is used to retrieve an iterator which must yield a
        # value on every call. This value can either be an exception instance
        # to be raised, or a value to be returned from the call to the mock
        # so each time that we call it it will return a diffretn value in the
        # order we dfined it so first we will get two times raised an exception
        # psycopg2Error, then 3 times the operationlError and for the 6th call
        # we will get a True value.

        mock_patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
        # this is bc we want to mimic diffretn stages of postgres starting
        # first stage is when the application itself has not even started yet
        # and this case will yield the Psycopg2Error
        # and after taht the databse will be ready to except connections but
        # it hasent set up the testing database and this will yield
        # OperationalError
        call_command('wait_for_db')

        # so bc the 6th time we call it should return True, we would expect the
        # check method to call 6 times
        self.assertEqual(mock_patched_check.call_count, 6)

        # makign sure the chek method is called with the default database
        mock_patched_check.assert_called_with(databases=['default'])
