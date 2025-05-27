from datetime import datetime, timedelta
from prometheus_client.core import Gauge

class Metrics(object):
    metrics = {}
    usage_metric = "mprnReading|Daily smart meter reading"
    def populate_metrics(self, daily_consumption):
        current_date = datetime.now().date()
        for record in daily_consumption:
            read_date_str = record.get("Read Date and End Time")
            read_date = datetime.strptime(read_date_str, "%d-%m-%Y %H:%M").date()
            # get my meter readings for yesterday, collected at midnight
            if read_date == current_date - timedelta(days=1):
                self.metrics['mprnReading'].set(record.get('Read Value'))
                break
         
            
    def collect(self):
        name = self.usage_metric.split("|")[0]
        desc = self.usage_metric.split('|')[1]
        self.metrics['name'] = Gauge(name, desc)