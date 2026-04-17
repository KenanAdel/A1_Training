#!/bin/bash
echo " welcome to kenanPKG "
echo " please wait for preparing and istalling"
echo "-------------------------------------------"

sudo apt update

sudo apt install -y ./kenanApp.deb

echo "--------------------------------------------"
echo "Thanks for waitting "
echo " API is running on: http://localhost:8000 please open it and read the endPoints"
echo "--------------------------------------------"
