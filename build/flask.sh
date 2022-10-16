# Setting up
sudo apt -qq update -y
apt -qq install python3-pip -y
apt -qq install python3-venv -y
mkdir app
# Cloning Repository
git clone -q $GIT_REPO app/
# Installing Python
python3 -m venv app/venv
# Installing requirements
source app/venv/bin/activate && pip3 install -r app/requirements.txt
# Installing tools
sudo apt -qq install nginx -y
sudo apt -qq install supervisor -y
sudo rm /etc/nginx/sites-enabled/default
curl -o /etc/nginx/sites-enabled/app.conf --silent https://buildpacks.ap-south-1.linodeobjects.com/nginx.conf
sudo systemctl restart nginx
curl -o /etc/supervisor/conf.d/app.conf --silent https://buildpacks.ap-south-1.linodeobjects.com/supervisor.conf
# Deploying
sudo mkdir -p /var/log/app
sudo touch /var/log/app/app.err.log
sudo touch /var/log/app/app.out.log