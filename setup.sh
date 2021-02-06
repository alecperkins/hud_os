
# bcm2835
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.64.tar.gz
tar xzvf bcm2835-1.64.tar.gz
cd bcm2835-1.67/
sudo ./configure
sudo make
sudo make check
sudo make install

# WiringPi
sudo apt-get install wiringpi
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v

# Python3 libraries
sudo apt-get update
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt

# Git
sudo apt-get install git
