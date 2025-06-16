from datetime import datetime, timedelta
from prometheus_client.core import Gauge

class Metrics(object):
    metrics = {}

    def __init__(self):
        # Initialize a Gauge for each day of the week
        self.metrics = ""

    def populate_metrics(self, db_metrics):
        print(db_metrics)
    
    def collect(self):
        print("hi")
