from flask import Flask, render_template
import requests


server_url = 'http://10.0.0.132:5001'  #change to match the location of your raspberry pi
api_path = "/gpio/api/v1.0/"
app = Flask(__name__)


@app.route("/")
def main():
    response = requests.get(server_url + api_path + 'pins/getstate')
    pins = response.json()
    pin_data = {
        'pins': pins
    }
    return render_template('RPiClient.html', **pin_data)


@app.route("/pinchange/<change_pin>/<action>")
def pinchange(change_pin, action):
    response = requests.put(server_url + api_path + 'pins/{0}/{1}'.format(change_pin, action))
    pins = response.json()
    pin_data = {
        'pins': pins
    }
    return render_template('RPiClient.html', **pin_data)


if __name__ == '__main__':
    app.run(host='localhost', port=5002, debug=True)
