GIT_REPO=https://github.com/radioactive11/fastapi-sample-app ./app
REPO_NAME=fastapi-sample-app

sudo apt update -y
apt install python3-pip
apt install python3-venv -y

git clone $GIT_REPO
cd $REPO_NAME

python3 -m venv venv
source venv/bin/activate

pip3 install -r requirements.txt

sudo apt install nginx -y
sudo apt install supervisor -y

cd
sudo rm /etc/nginx/sites-enabled/default
curl -o /etc/nginx/sites-enabled/app.conf https://raw.githubusercontent.com/radioactive11/diode-zener/master/build/nginx.conf?token=GHSAT0AAAAAABQBZNC7HR7KILHRYYS3RGYMYVLSTDA

sudo systemctl restart nginx

sudo mkdir -p /var/log/app
sudo touch /var/log/app/app.err.log
sudo touch /var/log/app/app.out.log


