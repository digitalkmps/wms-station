import RPi.GPIO as GPIO # type: ignore
import time
import board # type: ignore
import adafruit_dht # type: ignore
from prometheus_client import start_http_server, Gauge # type: ignore
import requests
import datetime
from settings import WMS_ADDRESS

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

dhtDevice = adafruit_dht.DHT11(board.D4)
LIGHT_PIN = 23
TRIG=22
ECHO=24

GPIO.setup(LIGHT_PIN, GPIO.IN)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

GPIO.output(TRIG,False)

temperature_metric = Gauge('temp_number', 'Temperature generated every 10 sec')
humidity_metric = Gauge('humi_number', 'Humidity generated every 10 sec')
light_metric = Gauge('light_boolean', 'Day/Night generated every 10 sec')
distance_metric = Gauge('distance_number', 'Distance generated every 10 sec')

time.sleep(2)

if __name__ == '__main__':

  start_http_server(8000)

  while True:
    try:
        # Print the values to the serial port
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        light = GPIO.input(LIGHT_PIN)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG,False)

        while GPIO.input(ECHO)==0:
          pulse_start=time.time()

        while GPIO.input(ECHO)==1:
          pulse_end=time.time()

        pulse_duration=pulse_end - pulse_start

        distance = round((pulse_duration * 17150),2)

        print(
            "Temp: {:.1f} C / Humidity: {}% / Distance: {}cm / Light: {}".format(
                temperature, humidity, distance, light
            )
        )

        temperature_metric.set(temperature)
        humidity_metric.set(humidity)
        light_metric.set(light)
        distance_metric.set(distance)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(WMS_ADDRESS, headers=headers, json={'eventTime': int(round(datetime.datetime.now().timestamp())), 'dataType': 'temperature', 'value': temperature})
        print(r.text)
        time.sleep(0.2)
        s = requests.post(WMS_ADDRESS, headers=headers, json={'eventTime': int(round(datetime.datetime.now().timestamp())), 'dataType': 'dewpoint', 'value': humidity})
        print(s.text)
    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(10.0)
