FROM python:3.9.13
WORKDIR /opt/AlphaNumericSounds
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg


COPY server ./server
COPY dependencies ./dependencies
COPY requirements.txt .
COPY startup.sh .

RUN python -m venv venv-ans
CMD ["./startup.sh"]
