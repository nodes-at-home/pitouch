#!/usr/bin/python3
# -*- coding: utf-8 -*-

# junand 18.10.2019

import os
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

TOPIC = "nodes@home/display/touchscreen/corridor"
TOPIC_ONOFF = TOPIC + "/screen"
TOPIC_ONOFF_STATE = TOPIC_ONOFF + "/state"
TOPIC_BRIGHTNESS = TOPIC + "/brightness"
TOPIC_BRIGHTNESS_STATE = TOPIC_BRIGHTNESS + "/state"
TOPIC_PING = TOPIC + "/ping"

BROKER = "nodesathome2"

QOS = 1
RETAIN = True

# The callback for when the client receives a CONNACK response from the server.
def on_connect ( client, userdata, flags, rc ):
	print ( "Connected with result code " + str ( rc ) )

	client.subscribe ( TOPIC + "#" )

# The callback for when a PUBLISH message is received from the server.
def on_message ( client, userdata, msg ):

	print ( msg.topic + "->" + str ( msg.payload ) )
	
	if ( msg.topic == TOPIC_ONOFF ):

		if msg.payload == b'ON':
			print ( "screen on" )
			os.system ( 'sudo sh -c "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"' )
			client.publish ( TOPIC_ONOFF_STATE, payload = "ON", qos = QOS, retain = RETAIN )
			
		elif msg.payload == b'OFF':
			print ( "screen off" )
			os.system ( 'sudo sh -c "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"' )
			client.publish ( TOPIC_ONOFF_STATE, payload = "OFF", qos = QOS, retain = RETAIN )
			
	elif ( msg.topic == TOPIC_BRIGHTNESS ):
		ossudo sh -c "echo '200' >> /sys/class/backlight/rpi_backlight/brightness"
	
	elif ( msg.topic == TOPIC_PING ):
	
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
