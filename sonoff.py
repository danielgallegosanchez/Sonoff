#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, requests, sqlite3, datetime, smtplib

start_time = 7 # max hour which relay cannot be activated (24h format)
finish_time = 1 # min hour which relay can be activated (24h format)
min_radiation_value_to_turnOn = 200.0 # threshold value to turn on the relay (W/m²)

def sendMail(msg):
	server = smtplib.SMTP()
	server.connect("XXX.XXX.XXX.XXX",25)
	server.sendmail("from", "to@example.com", msg)

def getRelayStatus():
	r = requests.get('http://XXX.XXX.XXX.XXX/control?cmd=status,gpio,12') # Relay in GPIO 12
	json_data = r.json()
	return json_data['state']

def setRelayValue(value):
	r = requests.get('http://XXX.XXX.XXX.XXX/control?cmd=event,switchsonoff'+value)

if __name__ == "__main__":
	now = datetime.datetime.now()
	lastState = getRelayStatus()
	if now.hour > finish_time and now.hour < start_time:
		setRelayValue('Off')
		msg = "Relay turned off cause hour limit"
	else:
		conn = sqlite3.connect('/absolute/path/to/db.sdb')
		radiation = float(conn.execute('SELECT radiation FROM archive ORDER BY dateTime DESC LIMIT 1').fetchone()[0])
		if radiation >= min_radiation_value_to_turnOn:
			setRelayValue('On')
			msg = "Relay turned off cause there isn't enough radiation"
		else:
			setRelayValue('Off')
			msg = "Relay turned off cause there is enough radiation"
		conn.close()
	newState = getRelayStatus()
	if lastState != newState:
		sendMail(msg)
