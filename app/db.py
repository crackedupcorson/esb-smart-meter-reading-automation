import mysql.connector
from mysql.connector import Error
from datetime import datetime
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
        - "Read Type"
        - "Read Value"
        """
        sql = "INSERT INTO meter_readings (reading_date, import_reading, export_reading) VALUES (%s, %s, %s)"
        today = datetime.now().date()
        readings = {}

        for record in daily_consumption:
            read_date_str = record.get("Read Date and End Time")
            read_type = record.get('Read Type')
            read_value = record.get('Read Value')
            if not read_date_str or not read_type or not read_value:
                continue
            try:
                reading_date = datetime.strptime(read_date_str, "%d-%m-%Y %H:%M").date()
                if reading_date == today:
                    if reading_date not in readings:
                        readings[reading_date] = {"import": None, "export": None}
                    if read_type == "24 Hr Active Export Register (kWh)":
                        readings[reading_date]["export"] = read_value
                    if read_type == "24 Hr Active Import Register (kWh)":
                        readings[reading_date]["import"] = read_value
            except Exception as e:
                print(f"Error processing record: {record} - {e}")

        for reading_date, values in readings.items():
            if values["import"] is not None and values["export"] is not None:
                try:
                    self.cursor.execute(sql, (reading_date, values["import"], values["export"]))
                    self.conn.commit()
                except Exception as e:
                    print(f"Error writing readings to Database: {values} with error: \n {e}")
            else:
                print(f"Incomplete readings for {reading_date}: {values}")

    def close(self):
        self.cursor.close()
        self.conn.close()