# Setting up
sudo apt -qq update -y
sudo apt install npm -y
mkdir app
# Cloning Repo
git clone -q $GIT_REPO app/
# Installing Dependancies
cd app/ && npm i --silent
# Building
cd app/ && npm run build
sudo apt -qq install nginx -y
sudo apt -qq install supervisor -y
sudo rm /etc/nginx/sites-enabled/default
curl -o /etc/nginx/sites-enabled/app.conf --silent https://buildpacks.ap-south-1.linodeobjects.com/nginx_static.conf
# Setting Permissions
gpasswd -a www-data root
chmod g+x /root/
chmod g+x /root/app/
chmod g+x /root/app/build/
nginx -s reload
sudo systemctl restart nginx
curl -o /etc/supervisor/conf.d/app.conf --silent https://buildpacks.ap-south-1.linodeobjects.com/supervisor.conf
# Deploying
sudo mkdir -p /var/log/app
sudo touch /var/log/app/app.err.log
sudo touch /var/log/app/app.out.log
