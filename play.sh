#!/bin/sh

# Default game
#GAME=Jeu_du_chat_et_de_la_souris
GAME=Jeu_de_la_grenouille

# TODO: add mqtt broker (default localhost)

if [ "$#" -eq 1 ]
then
    GAME=$1
fi

cd games/$GAME
python project.py



