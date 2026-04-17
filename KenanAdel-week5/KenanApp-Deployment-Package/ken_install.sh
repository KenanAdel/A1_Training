#!/bin/bash
echo " welcome to kenanPKG "
echo " please wait for preparing and istalling"
echo "-------------------------------------------"

sudo chmod +x kenanApp/DEBIAN/postinst
sudo chmod +x kenanApp/usr/local/bin/scrap_save.py
sudo chmod +x kenanApp/usr/local/bin/my_api.py

sudo apt update -y
sudo dpkg -b kenanApp kenanApp.deb
sudo apt install -y ./kenanApp.deb

echo "--------------------------------------------"
echo "Thanks for waitting "
echo " API is running on: http://localhost:8000 please open it and read the endPoints"
echo "--------------------------------------------"
