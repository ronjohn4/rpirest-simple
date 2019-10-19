# The pin key in the dict is string because jsonify() will convert to string.
# RPi.GPIO expects int.
#
# RPi.GPIO can't be installed on Windows.  To install on the raspberry pi use:
#   pip install RPi.GPIO
# It is in the requirements.txt so you can use pip install on the raspberry pi.
#   pip install -r requirements.txt
#
# Ron Johnson
# 4/21/2018


from flask import Flask, jsonify
import socket
import logging
from logging.handlers import RotatingFileHandler
import os
import RPi.GPIO as GPIO


app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
server_port = 5001

# List of pins, name, direction and pull_up_down.
# Defined static on the server because it's based on the hardware attached to the server.
pins = {
    '16': {'name': 'GPIO 16 - blue LED',
           'state': GPIO.LOW,
           'direction': GPIO.OUT,
           'pull_up_down': None},
    '17': {'name': 'GPIO 17',
           'state': GPIO.HIGH,
           'direction': GPIO.IN,
           'pull_up_down': GPIO.PUD_UP},
    '18': {'name': 'GPIO 18',
           'state': GPIO.HIGH,
           'direction': GPIO.IN,
           'pull_up_down': GPIO.PUD_UP},
    '19': {'name': 'GPIO 19 - yellow LED',
           'state': GPIO.LOW,
           'direction': GPIO.OUT,
           'pull_up_down': None}
}


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def init_pins():
    for pin in pins:
        GPIO.setup(int(pin), pins[pin]['direction'])
        if pins[pin]['direction'] == GPIO.OUT:
            GPIO.setup(int(pin), pins[pin]['direction'])
            GPIO.output(int(pin), pins[pin]['state'])
        else:
            GPIO.setup(int(pin), GPIO.IN, pull_up_down=pins[pin]['pull_up_down'])
            GPIO.add_event_detect(int(pin), GPIO.BOTH, callback=pin_changed, bouncetime=10)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/gpio/api/v1.0/pins/getstate', methods=['GET'])
def get_state():
    global pins

    for pin in pins:
        pins[pin]['state'] = GPIO.input(int(pin))

    app.logger.debug('getstate: {0}'.format(pins))
    return jsonify(pins)


@app.route('/gpio/api/v1.0/pins/<pin_changed>/<value>', methods=['PUT'])
def set_pin(pin_changed, value):
    global pins

    if pin_changed not in list(pins.keys()):
        app.logger.info("pin {0} is not valid".format(pin_changed))
        raise InvalidUsage("pin {0} is not valid".format(pin_changed), status_code=410)
    if pins[pin_changed]['direction'] != GPIO.OUT:
        app.logger.info("pin {0} isn't set for output".format(pin_changed))
        raise InvalidUsage("pin {0} isn't set for output".format(pin_changed), status_code=410)
    if int(value) == GPIO.HIGH or int(value) == GPIO.LOW:
        GPIO.output(int(pin_changed), int(value))
        app.logger.debug('pin {0} changed to {1}'.format(int(pin_changed), int(value)))
    else:
        app.logger.info("pin {0} can't be set to value={1}".format(pin_changed, value))
        raise InvalidUsage("pin {0} can't be set to value={1}".format(pin_changed, value), status_code=410)
    for pin in pins:
        pins[pin]['state'] = GPIO.input(int(pin))
    return jsonify(pins)


if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/rpiserver.log', maxBytes=20480, backupCount=20)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(file_handler.level)

    app.logger.info('RPiServer startup =========================================')

    init_pins()
    app.run(host='10.0.0.132', port=server_port, debug=True)
