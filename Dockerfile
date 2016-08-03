FROM resin/raspberrypi-python:2.7

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]

COPY . /usr/src/app
