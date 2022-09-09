pip install --upgrade pip
pip install -r requirements.txt

set PYTHONPATH=%PYTHONPATH%;cd

python server\manage.py migrate
python server\manage.py runserver 0.0.0.0:8080