
pip3 install --upgrade pip
pip3 install -r ./requirements.txt
python3 ./server/manage.py migrate
python3 ./server/manage.py runserver 0.0.0.0:8080