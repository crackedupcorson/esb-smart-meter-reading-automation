import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import os

class MeterReadingDB:
    def __init__(self):
        db_host = os.environ.get("METER_READER_DB_HOST")
        db_user = os.environ.get("METER_READER_DB_USER")
        db_pass = os.environ.get("METER_READER_DB_PASS")
        database = os.environ.get("METER_READER_DATABASE")
        self.conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=database
        )
        self.cursor = self.conn.cursor()

    def insert_readings(self, daily_consumption):
        """
        Expects daily_consumption to be a list of dicts with keys:
        - "Read Date and End Time"
        - "MPRN"
        """
        sql = "INSERT INTO meter_readings (reading_date, mprn) VALUES (%s, %s)"
        for record in daily_consumption:
            today = datetime.now().date()
            read_date_str = record.get("Read Date and End Time")
            mprn_reading = record.get("Read Value")
            if not read_date_str or not mprn_reading:
                continue
            try:
                reading_date = datetime.strptime(read_date_str, "%d-%m-%Y %H:%M").date()
                if reading_date == today or reading_date == today + timedelta(days=1):
                    self.cursor.execute(sql, (reading_date, mprn_reading))
            except Exception as e:
                print(f"Error inserting record: {record} - {e}")
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()