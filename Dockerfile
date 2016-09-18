FROM ioft/armhf-ubuntu:latest

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y python-pip python-dev build-essential 

COPY requirements.txt /usr/src/app/

WORKDIR /usr/src/app

RUN pip install -r requirements.txt

COPY . /usr/src/app

CMD ["python", "app.py"]
