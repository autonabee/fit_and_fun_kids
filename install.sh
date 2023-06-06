#!/bin/sh

# Patch the possibility to communicate with mqtt fit_and_fun sensor
cp patch/runtime_sensor.py sb3topy/src/engine/
cp patch/__init__.py sb3topy/src/engine/
# Python module required
pip install -r requirements.txt