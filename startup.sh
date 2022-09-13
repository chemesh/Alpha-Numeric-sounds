pip install --upgrade pip
pip install -r ./requirements.txt
python ./server/manage.py migrate
cd ui
bash -c ./start_ui.sh & disown
cd ..
python ./server/manage.py runserver 0.0.0.0:8080
