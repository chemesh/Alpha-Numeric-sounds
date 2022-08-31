FROM python:3.9.13-alpine3.16
WORKDIR /opt/AlphaNumericSounds

COPY AlphaNumericSounds /server
COPY app /server
COPY Source /server
COPY manage.py /
COPY requirements.txt /

RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
CMD ["python", "./manage.py", "runserver", "8080"]


