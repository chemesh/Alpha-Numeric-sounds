pip install --upgrade pip
pip install -r requirements.txt
pip install dependencies\spleeter-2.3.2-py3-none-any.whl

set PYTHONPATH=%PYTHONPATH%;cd

python server\manage.py migrate
python server\manage.py runserver 0.0.0.0:8080