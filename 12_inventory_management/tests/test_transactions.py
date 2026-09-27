import unittest
from unittest.mock import Mock, patch

from inventory.database import Database


class TransactionTests(unittest.TestCase):
    def test_success_commits_and_closes_resources(self):
        connection = Mock()
        cursor = connection.cursor.return_value
        database = Database({"database": "unused_test"})
        with patch.object(database, "connect", return_value=connection):
            with database.transaction() as actual_cursor:
                self.assertIs(actual_cursor, cursor)
        connection.commit.assert_called_once()
        connection.rollback.assert_not_called()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    def test_mid_operation_failure_rolls_back_and_closes_resources(self):
        connection = Mock()
        cursor = connection.cursor.return_value
        database = Database({"database": "unused_test"})
        with patch.object(database, "connect", return_value=connection):
            with self.assertRaisesRegex(RuntimeError, "audit insert failed"):
                with database.transaction():
                    raise RuntimeError("audit insert failed")
        connection.commit.assert_not_called()
        connection.rollback.assert_called_once()
        cursor.close.assert_called_once()
        connection.close.assert_called_once()
