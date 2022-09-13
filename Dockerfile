FROM python:3.9.13
WORKDIR /opt/AlphaNumericSounds
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN sudo apt install nodejs
RUN sudo apt install npm
RUN npm install --global yarn
RUN npm install react-scripts
RUN npm install -g serve

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

COPY server ./server
COPY ui/public ./ui/public
COPY ui/src ./ui/src
COPY ui/package.json ./ui/package.json
COPY dependencies ./dependencies
COPY requirements.txt .
COPY startup.sh .

RUN python -m venv venv-ans
CMD ["./startup.sh"]
