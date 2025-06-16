import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from db import MeterReadingDB

class TestMeterReadingDB(unittest.TestCase):

    @patch('db.mysql.connector.connect')
    def test_insert_readings_no_today(self, mock_connect):
        # Mock the connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = MeterReadingDB()

        # Use a date that is NOT today
        not_today = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y 00:00")
        daily_consumption = [
            {
                "Read Date and End Time": not_today,
                "Read Type": "24 Hr Active Import Register (kWh)",
                "Read Value": 111.11
            },
            {
                "Read Date and End Time": not_today,
                "Read Type": "24 Hr Active Export Register (kWh)",
                "Read Value": 222.22
            }
        ]

        db.insert_readings(daily_consumption)

        # Since there are no readings for today, execute and commit should not be called
        mock_cursor.execute.assert_not_called()
        mock_conn.commit.assert_not_called()

        db.close()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()



    @patch('db.mysql.connector.connect')
    def test_insert_readings_only_export(self, mock_connect):
        # Mock the connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = MeterReadingDB()

        today_str = datetime.now().strftime("%d-%m-%Y 00:00")
        daily_consumption = [
            {
                "Read Date and End Time": today_str,
                "Read Type": "24 Hr Active Export Register (kWh)",
                "Read Value": 88.77
            }
        ]

        db.insert_readings(daily_consumption)

        # Since there is no import value, execute and commit should not be called
        mock_cursor.execute.assert_not_called()
        mock_conn.commit.assert_not_called()

        db.close()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


    @patch('db.mysql.connector.connect')
    def test_insert_readings(self, mock_connect):
        # Mock the connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Create instance
        db = MeterReadingDB()

        #Today's date for test data
        today_str = datetime.now().strftime("%d-%m-%Y 00:00")
        # Sample daily_consumption with both import and export readings
        daily_consumption = [
            {
                "Read Date and End Time": today_str,
                "Read Type": "24 Hr Active Import Register (kWh)",
                "Read Value": 123.45
            },
            {
                "Read Date and End Time": today_str,
                "Read Type": "24 Hr Active Export Register (kWh)",
                "Read Value": 67.89
            }
        ]

        db.insert_readings(daily_consumption)

        # Check that execute was called once with correct SQL and params
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        self.assertIn("INSERT INTO meter_readings", args[0])
        self.assertEqual(args[1][1], 123.45)  # import_reading
        self.assertEqual(args[1][2], 67.89)   # export_reading

        # Check that commit was called
        mock_conn.commit.assert_called_once()

        db.close()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()