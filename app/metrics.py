from datetime import datetime, timedelta
from prometheus_client.core import Gauge

class Metrics(object):
    metrics = {}
    usage_metric = "mprnReading|Daily smart meter reading"

    def __init__(self):
        # Initialize a Gauge for each day of the week
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            self.metrics[f"{day}Reading"] = Gauge(f"{day}Reading", f"{day.capitalize()} smart meter reading")

    def populate_metrics(self, daily_consumption):
        # Get the current week (Monday to Sunday)
        today = datetime.now().date()
        for record in daily_consumption:
            read_date_str = record.get("Read Date and End Time")
            try:
                read_date = datetime.strptime(read_date_str, "%d-%m-%Y %H:%M").date()
            except Exception:
                continue
            day_name = read_date.strftime("%A").lower()  # e.g., 'monday'
            metric_name = f"{day_name}Reading"
            if metric_name in self.metrics:
                try:
                    self.metrics[metric_name].set(float(record.get('Read Value')))
                except Exception:
                    continue

    def collect(self):
        # No changes needed here for now
        pass