cd ui
bash -c ./start_ui.sh & disown
cd ..
pip install --upgrade pip
pip install -r ./requirements.txt
python ./server/manage.py migrate
python ./server/manage.py runserver 0.0.0.0:8080
