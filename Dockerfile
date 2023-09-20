FROM python:3.11.3-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin python-gdal python3-gdal
COPY . /code/

CMD gunicorn core.wsgi:application --bind 0.0.0.0:8000
EXPOSE 8000
