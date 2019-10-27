#!/usr/bin/python3
# -*- coding: utf-8 -*-

# junand 18.10.2019

import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

from rpi_backlight import Backlight;

import threading
import time

from apds9960.const import *
from apds9960 import APDS9960
import RPi.GPIO as GPIO
import smbus

TOPIC = "nodes@home/display/pitouch/corridor"
TOPIC_MQTT = TOPIC + "/state/mqtt"
TOPIC_ONOFF = TOPIC + "/screen"
TOPIC_ONOFF_STATE = TOPIC_ONOFF + "/state"
TOPIC_BRIGHTNESS = TOPIC + "/brightness"
TOPIC_BRIGHTNESS_STATE = TOPIC_BRIGHTNESS + "/state"
TOPIC_PEIODIC = TOPIC + "/value/voltage"
TOPIC_AMBIENT = TOPIC + "/value/ambient"

BROKER = "nodesathome1"

SLEEP_DURATION = 15 * 60

QOS = 1
RETAIN = True

APDS_INT_PIN = 7

apds = APDS9960 ( smbus.SMBus ( 1 ) )

#------------------------------------------------------------------------------------------------------------------------
def periodic ():
    while ( True ):
        print ( "periodic: send to topic=" + TOPIC_PEIODIC )
        client.publish ( TOPIC_PEIODIC, payload = '{"value":1000,"unit":"mV"}', qos = QOS, retain = RETAIN )
        ambient = apds.readAmbientLight ()
        r = apds.readRedLight ()
        g = apds.readGreenLight ()
        b = apds.readBlueLight ()
        json = '{"ambient":%s,"red":%s,"green":%s,"blue":%s,"unit":"Lux"}' % (ambient, r, g, b)
        print ( "periodic: send %s to %s" % (json, TOPIC_AMBIENT) )
        client.publish ( TOPIC_AMBIENT, payload = json, qos = QOS, retain = RETAIN )
        b = int ( 20 + 80 * ambient / 10000 )
        print ( "periodic: set brigthness=" + str ( b ) + " ambient=" + str ( ambient ) )
        backlight.brightness = b
        client.publish ( TOPIC_BRIGHTNESS_STATE, payload = b, qos = QOS, retain = RETAIN )
        print ( "periodic: going sleep" )
        time.sleep ( SLEEP_DURATION )

backlight = Backlight ()

#------------------------------------------------------------------------------------------------------------------------
# The callback for when the client receives a CONNACK response from the server.
def on_connect ( client, userdata, flags, rc ):
    print ( "on_connect: Connected to " + BROKER + " with result code " + str ( rc ) )

    client.publish ( TOPIC_MQTT, payload = "online", qos = QOS, retain = RETAIN )
    client.subscribe ( TOPIC + "/+" )
    threading.Thread ( target = periodic ).start ()
    print ( "on_connect: periodic thread started" )

#------------------------------------------------------------------------------------------------------------------------
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

#------------------------------------------------------------------------------------------------------------------------
# def intH(channel):
    # print("INTERRUPT")

#------------------------------------------------------------------------------------------------------------------------
#
# main
#

GPIO.setmode ( GPIO.BOARD )
#GPIO.setup ( APDS_INT_PIN, GPIO.IN )
#GPIO.add_event_detect ( APDS_INT_PIN, GPIO.FALLING, callback = intH )

apds.enableLightSensor ()

client = mqtt.Client ()
client.on_connect = on_connect
client.on_message = on_message

client.will_set ( TOPIC_MQTT, payload = "offline", qos = QOS, retain = RETAIN )

client.connect ( BROKER, 1883, SLEEP_DURATION )

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever ()
