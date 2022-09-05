FROM python:3.9.13
WORKDIR /opt/AlphaNumericSounds
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg


COPY server ./server
COPY manage.py ./server
COPY dependencies ./dependencies
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
RUN pip install dependencies/spleeter-2.3.1-py3-none-any.whl
RUN python server/manage.py migrate
CMD ["python", "server/manage.py", "runserver", "0.0.0.0:8080"]
