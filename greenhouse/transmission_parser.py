from ast import literal_eval
from datetime import datetime
from time import sleep
import paho.mqtt.client as mqttClient
from greenhouse.models import ESPTransmission, SensorHCSR04
from django.conf import settings


CONFIG = settings.MQTT_CONFIG
mqtt_connected = False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global mqtt_connected
        mqtt_connected = True
        mqtt_client.subscribe(topic)
    else:
        print("Connection failed")


def on_message(client, userdata, message):
    message_origin = message.topic
    print('********')
    print(message_origin)
    message = str(message.payload.decode("utf-8"))
    print("message received " , message)
    data = literal_eval(message)
    tstp_receive = datetime.now().timestamp()
    if message_origin == settings.LDR_DEVICE:
        device_id, tstp_origin, ldr, temp, pressure, moisture = data
        try:
            tx = ESPTransmission.objects.create(
                timestamp_origin=tstp_origin,
                timestamp_receive=tstp_receive,
                mac_address=device_id,
                ldr_sensor=ldr,
                temperature_sensor=temp,
                pressure=pressure,
                moisture=moisture
            )
            tx.save()
            client.publish('map/icon_update', str(list(data)))
            print('Published ', data)

        except Exception as e:
            print(f'Failed saving transmission with error: {str(e)}')
    elif message_origin == settings.HCSR_DEVICE:
        tstp_receive = datetime.now().timestamp()
        device_id, tstp_origin, distance = data
        try:
            tx = SensorHCSR04.objects.create(
                timestamp_origin=tstp_origin,
                timestamp_receive=tstp_receive,
                mac=device_id,
                distance=distance,
            )
            tx.save()
        except Exception as e:
            print(f'Failed saving transmission with error: {str(e)}')


broker_address= CONFIG['MQTT_HOST']
port = CONFIG['MQTT_PORT']
topic = CONFIG['MQTT_TOPIC']

try:
    topic = literal_eval(topic)
except Exception as e:
    print(e)
    topic = topic

print(topic)
mqtt_client = mqttClient.Client(CONFIG['MQTT_CLIENT'])
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


def subscribe():
    mqtt_client.connect(
        broker_address,
        port=port,
        keepalive=True
    )
    mqtt_client.loop_forever()

    # Wait connection to mqtt roker suceeds
    while not mqtt_connected:    #Wait for connection
        sleep(0.1)
