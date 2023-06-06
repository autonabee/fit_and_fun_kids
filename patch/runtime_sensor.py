"""
runtime_sensor.py

Contains classes used to manage base program functions.
extension of runtime.py
"""

import asyncio
import logging
import random

from .runtime import Runtime

from . import config
from .events import SPRITES

from mqtt_subscriber import mqtt_subscriber
import threading

class Runtime_sensor(Runtime):
    """
    Container for everything needed to run the project
    Extension of Runtime class adding sensor/mqtt interaction

    Attributes:
        clock: pygame.time.Clock

        running: Controls the main loop
    """
 
    def __init__(self, targets):
 
        Runtime.__init__(self, targets)

        self.sensor=0
        self.sensor_lock=threading.Lock()
        self.sensor_get_lock=threading.Lock()
        # self.sensor_topic='fit_and_fun/rot_speed'
        self.sensor_topic='fit_and_fun/orientation_1'
        self.sensor_emg_topic='fit_and_fun/emg' 
        #self.mqtt_address='10.42.0.1'
        self.mqtt_address='192.168.43.78'

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


    def get_orientation(self, client, userdata, message):
            try:
                # Disable CALCUL_NIVEAU from scratch
                self.util.sprites.stage.var_enable=0 
                orientation_str=str(message.payload.decode("utf-8"))
                orientation = [float(x) for x in orientation_str.split()]
                self.sensor=orientation[1]
                sensor_level=self.sensor
                if sensor_level < 0.0:
                    if self.util.sprites.stage.var_mode > 0:
                        sensor_level=0.0
                scale_level=80/abs(self.util.sprites.stage.var_mode)
                
                self.util.sprites.stage.var_niveau_activite=int(sensor_level/scale_level)
                print('Event Sensor orientation', self.sensor,'->',  self.util.sprites.stage.var_niveau_activite)
                self.sensor_get_lock.release()
            except Exception:
               print('Error in mqtt message')
               self.sensor=0
               self.util.sprites.stage.var_niveau_activite=0


    def get_emg(self, client, userdata, message):
            try:
                # Disable CALCUL_NIVEAU from scratch
                self.util.sprites.stage.var_enable=0 
                self.sensor=float(str(message.payload.decode("utf-8")))
                self.util.sprites.stage.var_niveau_activite=int(self.sensor/10)
                print('Event Sensor emg', self.sensor,'->',  self.util.sprites.stage.var_niveau_activite)
                self.sensor_get_lock.release()
            except Exception:
               print('Error in mqtt message')
               self.sensor=0 
               self.util.sprites.stage.var_niveau_activite=0

    def get_keyboard(self, client, userdata, message):
            try:
                # Disable CALCUL_NIVEAU from scratch
                self.util.sprites.stage.var_enable=0 
                self.sensor=float(str(message.payload.decode("utf-8")))
                self.util.sprites.stage.var_niveau_activite=int(self.sensor/10)
                print('Event Sensor keyboard', self.sensor,'->',  self.util.sprites.stage.var_niveau_activite)
                self.sensor_get_lock.release()
            except Exception:
               print('Error in mqtt message')
               self.sensor=0


    # Redefinition of the method using sensor/mqtt interaction
    async def main_loop(self):
        """Run the main loop"""
        # Setup asyncio debug
        asyncio.get_running_loop().slow_callback_duration = 0.49

        # Start green flag
        self.events.send(self.util, self.sprites, "green_flag")

        subscribes=[self.sensor_topic, self.sensor_emg_topic]
        mqtt_sub=mqtt_subscriber(self.message_callback, self.sensor_lock, subscribes, self.mqtt_address)
        mqtt_sub.run()
        # Main loop
        self.running = True
        count=0
        while self.running:
            # Handle the event queue
            self.handle_events()
            
            if self.sensor_get_lock.acquire() == True:
                #self.events.send(self.util, self.sprites, "key_space_pressed")
                #print("niveau_activite ", self.util.sprites.stage.var_niveau_activite)
                pass

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

