# Git
sudo apt-get install git -y

# bcm2835
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.64.tar.gz
tar xzvf bcm2835-1.64.tar.gz
cd bcm2835-1.64/
sudo ./configure
sudo make
sudo make check
sudo make install
cd ..

# WiringPi
sudo apt-get install wiringpi -y
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v

git clone https://github.com/alecperkins/hud_os
cd hud_os

# Python3 libraries
sudo apt-get update
sudo apt-get install python3-pip -y
# sudo apt-get install libopenjp2-7 -y
# sudo apt-get install libcairo2 -y
# sudo apt-get install python-pil -y
pip3 install -r requirements.txt

