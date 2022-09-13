FROM python:3.9.13
FROM node:latest
WORKDIR /opt/AlphaNumericSounds
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get -y update
RUN apt-get -y upgrade
RUN npm install --global yarn --force
RUN npm install react-scripts
RUN npm install -g serve
RUN apt-get install -y ffmpeg

COPY server ./server
COPY ui/public ./ui/public
COPY ui/src ./ui/src
COPY ui/package.json ./ui/package.json
COPY requirements.txt .
COPY startup.sh .

CMD ["./startup.sh"]
