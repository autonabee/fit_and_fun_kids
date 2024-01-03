# fit_and_fun_kids

An interactive device to play with scratch game generated in python

## Installation

### Requirements

* `Ubuntu 22.04`
* `Python > 3.10`
* `git clone --recurse-submodules https://github.com/autonabee/fit_and_fun_kids`

### Import python modules and external project

```bash
> pip install -r requirements.txt
```

### Mqtt broker config

Add at this end of the file: `/etc/mosquitto/mosquitto.conf`

```bash
listener 1883 localhost 
listener 1883 10.42.0.1
allow_anonymous true
```

Restart the service

```bash
> systemctl restart mosquitto
```

Some reminders to debug

* see the log: `sudo tail -f /var/log/mosquitto/mosquitto.log`
* connection to the socket port: `nc -z -v -u 10.42.0.1 1883`
* connection to the topic through the broker:`mosquitto_sub -h 10.42.0.1 -t "fit_and_fun/speed"`
* publish a topic: `mosquitto_pub -h 10.42.0.1 -t "fit_and_fun/speed" -mode "10.0"`

## External projects

Fit_and_Fun_Kids is based on three main open-source projects:

* [scratch](https://scratch.mit.edu/) a support to creative coding for everyone
* [scratch projects](https://scratch.mit.edu/studios/33100170/) example in scratch
* [sb3topy](https://github.com/autonabee/sb3topy/) a Scratch to Python converter
* [fit_and_fun](https://github.com/autonabee/fit_and_fun)

## Getting started

* Import a new game `my_game.sb3` in `games/`
* If necessary set configuration values on file `config_game.yaml` in current path
* Generate python: `python gametopy.py my_game`
* Play: `> play.sh my_game`

Example of `config_game.yaml` file:

```yaml
mqtt_address:  '192.168.43.78' 
sensor_topic: 'fit_and_fun/orientation_1'
sensor_min: 0
sensor_max: 80
```

## Files

* `games/` contains the scratch games and the python code converted
  * `Jeu_du_chat_et_de_la_souris.sb3` and `Jeu_du_chat_et_de_la_souris`
  * `Jeu_de_la_grenouille.sb3` and `Jeu_du_chat_et_de_la_souris`
* `html/` contains the scratch games executable in a web browser
  * `Jeu_du_chat_et_de_la_souris.html`
  * `Jeu_de_la_grenouille.html`
* `patch/` contains python files managing device mqtt interaction
* `sensor_keyboard.py` emulates the speed rotation mqtt sensor (from 0 to 50)
* `install.sh` shell script for installation
* `play.py` generate and launch a game

## Principle

The actor (sprite) in the scratch game is controlled by the scratch variable `niveau_activite` with 6 levels of intensity from 0 to 5. The speed mqtt sensor set this variable in order to control the game actor.

## How to play

* Import the scratch game in `games` (ex: `Jeu_de_la_grenouille.sb3`
* Convert in python with `python gametopy.py Jeu_de_la_grenouille`
* Launch the game `./play.sh Jeu_de_la_grenouille`
* Launch the mqtt sensor or the keyboard emulator (`python sensor_keyboard.py`)

## Games

* `Jeu_du_chat_et_de_la_souris_mode`
* `Jeu_du_chat_et_de_la_souris_mode`
* `Attrape-Moouai_te_by_Tya`
* `Space_dog` (hand-made modification in project.py see Bugs)

## Bugs

With Space_dog:

* generation bug for  @on_backdrop('blue sky') instead @on_backdrop('Blue Sky')  (idem Accueilx)
* Image size, offset and sprites positioning problem
* Arc en Ciel creation (need a tempo to postpone the deletion)
* looks_sayforsecs("arghhhhh !", 2) is not implemented => put a sleep to see the costume switch

## License

The software is under [Ceccil licence](./COPYING)

