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

"""
runtime_sensor.py

Contains classes used to manage base program functions.
extension of runtime.py
"""
# Import des librairie
import asyncio
import logging
import random

from .runtime import Runtime

from . import config
from .events import SPRITES

from mqtt_subscriber import mqtt_subscriber
import threading
import yaml
from yaml.loader import SafeLoader

# Definition de fonctions
class Runtime_sensor(Runtime):
    """
    Container for everything needed to run the project
    Extension of Runtime class adding sensor/mqtt interaction

    Attributes:
        clock: pygame.time.Clock

        running: Controls the main loop
    """
 
    # Initialisation
    def __init__(self, targets):
 
        Runtime.__init__(self, targets)

        self.sensor=0
        self.activite=0
        self.sensor_lock=threading.Lock()
        # Set mqtt_address, sensor_topic, sensor_emg_topic
        self.load_game_config('config_game.yaml')

    # Connection à la commnucation sans fil avec les microcontrolleurs des capteurs
    def load_game_config(self, filename):
        # Default values
        self.mqtt_address='10.42.0.2'
        self.sensor_topic='fit_and_fun/orientation'
        self.sensor_emg_topic='fit_and_fun/emg'
        self.sensor_min=0
        self.sensor_max=100

        try:
            with open(filename) as f:
                data = yaml.load(f, Loader=SafeLoader)
                if 'mqtt_address' in data.keys():
                    self.mqtt_address=data['mqtt_address']
                if 'sensor_topic' in data.keys(): 
                    self.sensor_topic=data['sensor_topic']
                if 'sensor_emg_topic' in data.keys():
                    self.sensor_emg_topic=data['sensor_emg_topic'] 
                if 'sensor_min' in data.keys():
                    self.sensor_min=data['sensor_min']
                if 'sensor_max' in data.keys():
                    self.sensor_max=data['sensor_max']    
        except Exception:
            print('Warning:: load_mqtt_config failed')

    # Récupère l'info capteur
    def message_callback(self, client, userdata, message):
        """ 
        Mqtt callback treating all topics
        """  
        match message.topic:
            case self.sensor_topic:
                #self.get_keyboard(client, userdata, message)
                self.get_orientation(client, userdata, message)
            case self.sensor_emg_topic:
                self.get_emg(client, userdata, message)
            case _:
                print("WARNING: topic " + message.topic + " unknown\n")

    # Récupère l'orientation
    def get_orientation(self, client, userdata, message):
            try:
                # Disable CALCUL_NIVEAU from scratch
                self.util.sprites.stage.var_activite_enable=0 
                orientation_str=str(message.payload.decode("utf-8"))
                orientation = [float(x) for x in orientation_str.split()]
                # Store raw sensor value
                self.sensor=orientation[1]
                
                # 'Normalize'/'Scale the raw sensor value
                if self.sensor < self.sensor_min:
                    self.sensor = self.sensor_min
                elif self.sensor > self.sensor_max:
                    self.sensor = self.sensor_max
                ratio_sensor_activite=self.util.sprites.stage.var_activite_max-self.util.sprites.stage.var_activite_min
                ratio_sensor_activite=ratio_sensor_activite/(self.sensor_max-self.sensor_min)
                
                # Convertion la valeur en commande du jeu (binaire ou 6 niveau)
                if self.util.sprites.stage.var_activite_front==1:
                    # Front detection for mode 2 states
                    offset=self.util.sprites.stage.var_activite_min -ratio_sensor_activite*self.sensor_min
                    value_activite=int(round(ratio_sensor_activite*self.sensor+offset))
                    if  self.activite == 0: 
                        self.activite=value_activite
                        self.util.sprites.stage.var_niveau_activite=self.activite
                    elif value_activite == 0:
                        self.activite = 0
                        self.util.sprites.stage.var_niveau_activite = 0
                else:
                    # Level mode 
                    offset=self.util.sprites.stage.var_activite_min -ratio_sensor_activite*self.sensor_min
                    self.activite=int(round(ratio_sensor_activite*self.sensor+offset))
                    self.util.sprites.stage.var_niveau_activite=self.activite
                print('Event Sensor orientation',  self.sensor, self.activite,'->',  self.util.sprites.stage.var_niveau_activite)
            
            except Exception:
               print('Error in mqtt message')
               self.sensor=0
               self.util.sprites.stage.var_niveau_activite=0

    # Récupère l'activité musculaire
    def get_emg(self, client, userdata, message):
            try:
                # Disable CALCUL_NIVEAU from scratch
                self.util.sprites.stage.var_activite_enable=0 
                # Store raw sensor value
                self.sensor=float(str(message.payload.decode("utf-8")))
                # 'Normalize'/'Scale the raw sensor value 
                if self.sensor < self.sensor_min:
                    self.sensor = self.sensor_min
                elif self.sensor > self.sensor_max:
                    self.sensor = self.sensor_max
                ratio_sensor_activite=self.util.sprites.stage.var_activite_max-self.util.sprites.stage.var_activite_min
                ratio_sensor_activite=ratio_sensor_activite/(self.sensor_max-self.sensor_min)
                offset=self.util.sprites.stage.var_activite_min -ratio_sensor_activite*self.sensor_min
                self.util.sprites.stage.var_niveau_activite=int(ratio_sensor_activite*self.sensor+offset)    
                print('Event Sensor emg', self.sensor,'->',  self.util.sprites.stage.var_niveau_activite)
            except Exception:
               print('Error in mqtt message')
               self.sensor=0 
               self.util.sprites.stage.var_niveau_activite=0

     # Récupère des interactions claviers (barre ESPACE)
    def get_keyboard(self, client, userdata, message):
            try:
                # Disable CALCUL_NIVEAU from scratch
                self.util.sprites.stage.var_activite_enable=0 
                self.sensor=float(str(message.payload.decode("utf-8")))
                self.util.sprites.stage.var_niveau_activite=int(self.sensor/10)
                print('Event Sensor keyboard', self.sensor,'->',  self.util.sprites.stage.var_niveau_activite)
            except Exception:
               print('Error in mqtt message')
               self.sensor=0

    # Gestion de la boucle de récupération des données
    # Redefinition of the method using sensor/mqtt interaction
    async def main_loop(self):
        """Run the main loop"""
        # Setup asyncio debug
        asyncio.get_running_loop().slow_callback_duration = 0.49

        # Start green flag
        self.events.send(self.util, self.sprites, "green_flag")

        subscribes=[self.sensor_topic, self.sensor_emg_topic]
        
        # Récupère les infos capteurs
        mqtt_sub=mqtt_subscriber(self.message_callback, self.sensor_lock, subscribes, self.mqtt_address) 
        mqtt_sub.run()
        
        # Main loop
        self.running = True
        count=0
        while self.running:
            # Handle the event queue
            self.handle_events()
        
            # Allow threads to run
            await self.step_threads()

            # Update targets, draw screen
            self.draw()

            # Limit the frame rate
            if not config.TURBO_MODE:
                self.clock.tick(config.TARGET_FPS)
            else:
                self.clock.tick()
        mqtt_sub.stop()

#############################################"
# Redefinition of start_program
def start_program():
    """Run the program"""
    logging.basicConfig(level=logging.DEBUG)

    if config.RANDOM_SEED is not None:
        random.seed(config.RANDOM_SEED)

    runtime = None
    try:
        runtime = Runtime_sensor(SPRITES) 
        asyncio.run(runtime.main_loop())
    finally:
        if runtime:
            runtime.quit()

