# RPiREST-Simple
Keywords: Raspberry Pi, Flask, GPIO, REST API

There are 2 main components, RPiServer runs on the Raspberry Pi and exposes a set of APIs that allow RPiClient to
get/set the Raspberry Pi pin state.
Both Server and Client are written for Python 3.

![RPiREST Data Flow](https://github.com/ronjohn4/RPiREST/blob/master/RPiREST-Simple.png)

Out of scope for RpiREST-Simple are:
- call back functions for the client to be notified of pin changes
- jquery or other library to dynamically update the html
- Any bus transport between the Server and Client for message - distribution and scaling.

RPi REST - Simple.postman_collection.json is a Postman collection that can be imported and used to test the api endpoints.

# RPiServer
RPiServer runs on the Raspberry Pi and is tightly coupled with the Raspberry Pi hardware.  RPiServer is where you define
the pin settings.
Based on the pin settings, the raspberry pi pins are configured for Input or Output at start up.  The input pins have a REST endpoint
that can be called to set the pin.  The Input and Output pins are included in the response to get the pins state.

## Installing GPIO on the Raspberry Pi
RPiServer depends on the GPIO library to interact with the pins.

sudo apt-get update
sudo apt-get install python-dev
sudo apt-get install python-rpi.gpio

sudo apt-get install python-pip

# RPiClient
RPiClient displays a simple UI (using Flask) which displays the configured pins and their current state.  It
interacts with the Raspberry Pi through the provided REST API endpoints.
