from flask import Flask
from flask import request

from processor import MeterReader
from metrics import Metrics
from db import MeterReadingDB

from waitress import serve
import prometheus_client
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import asyncio

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
metrics = Metrics()

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})


@app.route('/daily')
def get_daily_consumption():
    reader = MeterReader()
    db = MeterReadingDB()
    async def process_consumption():
        loop = asyncio.get_event_loop()
        consumption = await loop.run_in_executor(None, reader.get_energy_consumption)
        print(consumption)
        await loop.run_in_executor(None, db.insert_readings, consumption)
        db.close()
        return consumption

    return asyncio.run(process_consumption())

def register_prom_metrics():
    metrics.collect()

if __name__ == "__main__":
    register_prom_metrics()
    serve(app, host="0.0.0.0", port=8080)