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

shutil.copy('patch/mqtt_subscriber.py', os.path.join(game_dir, 'mqtt_subscriber.py'))

