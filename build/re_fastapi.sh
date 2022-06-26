cd app/ && git stash
cd app/ && git pull

source app/venv/bin/activate && pip3 install -r app/requirements.txt

sudo systemctl restart nginx
sudo supervisorctl reread

