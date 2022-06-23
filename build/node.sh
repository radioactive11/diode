# Setting up
sudo apt -qq update -y
sudo apt install nodejs -y
sudo apt install npm -y
mkdir app
# Cloning Repo
git clone -q $GIT_REPO app/
# Installing Dependancies
cd app/ && npm i --silent
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
