#!/usr/bin/python3
# -*- coding: utf-8 -*-

# junand 18.10.2019

import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

from rpi_backlight import Backlight;

TOPIC = "nodes@home/display/pitouch/corridor"
TOPIC_ONOFF = TOPIC + "/screen"
TOPIC_ONOFF_STATE = TOPIC_ONOFF + "/state"
TOPIC_BRIGHTNESS = TOPIC + "/brightness"
TOPIC_BRIGHTNESS_STATE = TOPIC_BRIGHTNESS + "/state"
TOPIC_PING = TOPIC + "/ping"

BROKER = "nodesathome1"

QOS = 1
RETAIN = True

backlight = Backlight ()

# The callback for when the client receives a CONNACK response from the server.
def on_connect ( client, userdata, flags, rc ):
    print ( "Connected with result code " + str ( rc ) )

    client.subscribe ( TOPIC + "/+" )

# The callback for when a PUBLISH message is received from the server.
def on_message ( client, userdata, msg ):

    print ( msg.topic + "->" + str ( msg.payload ) )

    if ( msg.topic == TOPIC_ONOFF ):

        if msg.payload == b'ON':
            print ( "screen on" )
            backlight.power = True
            client.publish ( TOPIC_ONOFF_STATE, payload = "ON", qos = QOS, retain = RETAIN )
            print ( "state published" )

        elif msg.payload == b'OFF':
            print ( "screen off" )
            backlight.power = False
            client.publish ( TOPIC_ONOFF_STATE, payload = "OFF", qos = QOS, retain = RETAIN )
            print ( "state published" )

    elif ( msg.topic == TOPIC_BRIGHTNESS ):
        brightness = msg.payload.decode ( 'utf-8' )
        print ( "screen brightness=" + brightness )
        backlight.brightness = int ( brightness )
        client.publish ( TOPIC_BRIGHTNESS_STATE, payload = brightness, qos = QOS, retain = RETAIN )
        print ( "state published" )

    elif ( msg.topic == TOPIC_PING ):
        print ( "ping" )

#
# main
#

client = mqtt.Client ()
client.on_connect = on_connect
client.on_message = on_message

client.connect ( BROKER, 1883, 60 )

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever ()
