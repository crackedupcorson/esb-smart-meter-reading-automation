FROM --platform=linux/arm64/v8 arm64v8/python:3.11-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN apt-get -y update; apt-get -y install curl
COPY ./ /app
WORKDIR /app

ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["python", "esb-smart-meter-reader.py"]