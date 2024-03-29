#!/usr/bin/python

import datetime
import time
import jwt
import paho.mqtt.client as mqtt
import random

cur_time = datetime.datetime.utcnow()
ssl_private_key_filepath = '/home/pi/Desktop/SantaFridge/Modulos/demo_private.pem'
ssl_algorithm = 'RS256'  # Either RS256 or ES256
root_cert_filepath = '/home/pi/Desktop/SantaFridge/Modulos/roots.pem'
project_id = 'santa-fridge'
gcp_location = 'us-central1'
registry_id = 'refrigerador'
device_id = 'camara'

def create_jwt():
    token = {
        'iat': cur_time,
        'exp': cur_time + datetime.timedelta(minutes=60),
        'aud': project_id
    }

    with open(ssl_private_key_filepath, 'r') as f:
        private_key = f.read()

    return jwt.encode(token, private_key, ssl_algorithm)

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')

def upload_data(transaction, f):
    # Get current time
    _CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
        project_id, gcp_location, registry_id, device_id)
    _MQTT_TOPIC = '/devices/{}/events'.format(device_id)
    client = mqtt.Client(client_id=_CLIENT_ID)
    # authorization is handled purely with JWT, no user/pass, so username can be whatever
    client.username_pw_set(
        username='unused',
        password=create_jwt())

    client.on_connect = on_connect
    client.on_publish = on_publish

    # Replace this with 3rd party cert if that was used when creating registry
    client.tls_set(ca_certs=root_cert_filepath)
    client.connect('mqtt.googleapis.com', 443)
    client.loop_start()

    edad = f[0]['age']
    genero = f[0]['gender']
    id_sesion = transaction

    payload = '{{ "ts": {}, "edad": {}, "genero": "{}" , "id_sesion": {} }}'.format(
        int(time.time()), edad, genero, id_sesion)

    # Uncomment following line when ready to publish
    client.publish(_MQTT_TOPIC, payload, qos=1)

    print("{}\n".format(payload))

    time.sleep(1)

    client.loop_stop()