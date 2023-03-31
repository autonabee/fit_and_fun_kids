#!/bin/sh

# Get sb3topy project cloned with bug correction
wget https://github.com/autonabee/sb3topy/archive/master.zip
unzip master.zip
mv sb3topy-master sb3topy
# Patch the possibility to communicate with mqtt fit_and_fun sensor
cp patch/runtime_sensor.py sb3topy/src/engine/
cp patch/__init__.py sb3topy/src/engine/
rm -f master.zip
# Python module required
pip install -r requirements.txt