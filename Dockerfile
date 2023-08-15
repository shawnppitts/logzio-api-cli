FROM python:3.8-alpine
LABEL Maintainer="Shawn Pitts"
WORKDIR /app/src

COPY ./requirements.txt /app/src
COPY scripts /app/src/scripts
COPY ./script.py /app/src

RUN pip3 install -r requirements.txt

CMD [ "python", "script.py"]