#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, requests, mysql.connector, datetime, smtplib

start_time1  = 20 # (24h format)
finish_time1 = 1  # (24h format)
start_time2  = 6  # (24h format)
finish_time2 = 10 # (24h format)
min_radiation_value_to_turnOn = 100.0 # threshold value to turn on the relay (W/m²)

mydb = mysql.connector.connect(host="mydomain.com", user="dbuser", passwd="dbpass", database="dbname")
mycursor = mydb.cursor()

def sendMail(msg):
        server = smtplib.SMTP()
        server.connect("XXX.XXX.XXX.XXX",25)
        server.sendmail("from@domain.com", "to@domain.com", msg)

def getRelayStatus():
        r = requests.get('http://XXX.XXX.XXX.XXX/cm?cmnd=Power') # Relay in GPIO 12
        json_data = r.json()
        return json_data['POWER']

def setRelayValue(value):
        r = requests.get('http://XXX.XXX.XXX.XXX/cm?cmnd=Power%20'+value)

if __name__ == "__main__":
        now = datetime.datetime.now()
        lastState = getRelayStatus()
        if (now.hour > start_time1 and now.hour < finish_time1) or (now.hour > start_time2 and now.hour < finish_time2):
                radiation = float(mycursor.execute('SELECT radiation FROM archive ORDER BY dateTime DESC LIMIT 1').fetchone()[0])
                if radiation >= min_radiation_value_to_turnOn:
                        setRelayValue('On')
                        msg = "Relay turned off because of there isn't enough radiation"
                else:
                        setRelayValue('Off')
                        msg = "Relay turned off because of there is enough radiation"
                conn.close()
        else:
                setRelayValue('Off')
                msg = "Relay turned off because of time"
        newState = getRelayStatus()
        if lastState != newState:
                sendMail(msg)
