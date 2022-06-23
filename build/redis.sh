# Setting up
sudo apt -qq update -y
# Installing Redis
sudo apt install redis-server -y
curl -o /etc/redis/redis.conf --silent https://buildpacks.ap-south-1.linodeobjects.com/redis.conf
# Configuring Redis
sed -i "790s|.*|requirepass $REDIS_PW|" /etc/redis/redis.conf
# Finishing
sudo systemctl restart redis.service
