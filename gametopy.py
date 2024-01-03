# This file is a part of Fit & Fun Kids
#
# Copyright (C) 2023 Inria
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

import os
import sys
import shutil
import argparse
import sb3topy.src.sb3topy.main

PARSER = argparse.ArgumentParser(
        description='Fit and fun kids game') 
PARSER.add_argument("game", help="name of the game to convert")
ARGS = PARSER.parse_args()

game_dir=os.path.join('games', ARGS.game)
game_sb3=ARGS.game+'.sb3'
game_dir_sb3=os.path.join('games', game_sb3)

if not os.path.isfile(game_dir_sb3):
    print('error: game file does',game_dir_sb3, 'does not exist')
    sys.exit()

if not os.path.exists(game_dir):
    os.mkdir(game_dir)

# Convert
sb3topy.src.sb3topy.main.main([game_dir_sb3, game_dir])
# Patch the generated code
shutil.copy('patch/mqtt_subscriber.py', os.path.join(game_dir, 'mqtt_subscriber.py'))
shutil.copy('patch/__init__.py', os.path.join(game_dir, 'engine', '__init__.py'))
shutil.copy('patch/runtime_sensor.py', os.path.join(game_dir, 'engine', 'runtime_sensor.py'))
cfg_file_name='config_game.yaml'
if os.path.isfile(cfg_file_name):
    shutil.copy(cfg_file_name, os.path.join(game_dir, cfg_file_name))
else:
    shutil.copy(os.path.join('patch',cfg_file_name), os.path.join(game_dir, cfg_file_name))

