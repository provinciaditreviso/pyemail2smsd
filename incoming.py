#!/usr/bin/env python
from sys import argv
import os
import time
from pprint import pprint
import pyinotify
import logging
import smtplib
import email
import sqlite3
import time


DBPATH = "/var/spool/sms/"

# IN_CLOSE_WRITE event management
class HandleEvents(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        if event.name[:3] != "GSM":
		logging.info("File "+event.name+" is not an inbound message. Skipping...")
		return
        if os.path.isfile(event.path+'/'+event.name):
		message = email.message_from_file(open(event.path+'/'+event.name))
		if message.has_key('From'):
			sender = message['From'][2:]
			sender += "@smsmaker.com"
		else:
			sender = "unknown@smsmaker.com"
		txt = ''
		for part in message.walk():
			txt += str(part).replace(":", " ")
		try:
			session = smtplib.SMTP('posta.provincia.treviso.it')
			destination = get_destinations(sender)
                        smtpresult = session.sendmail(sender, destination, txt)
                        logging.info('Delivered sms to '+str(destination))
			os.remove(event.path+'/'+event.name)
		except Exception as exc:
                            logging.error('Unable to deliver message to destinations: '+exc.__str__())
		
		
		
	else:
		logging.critical("file "+event.name+" disappeared!");

# Placeholder for future extension
def get_destinations(sender):
	discardtime = int(time.time()) - 24*60*60
	svals = (sender,discardtime)
	conn = sqlite3.connect(DBPATH+'return_path.db')
	c = conn.cursor()
	# Do a cleanup on the db to clean entries that are too old
	c.execute("DELETE FROM returnpath WHERE timestamp <= ?",(discardtime, ))
	# Extract emails who has sent to that number in the last 48h
	c.execute("SELECT sender FROM returnpath WHERE number = ? and timestamp > ?",svals)
	res = c.fetchall()
	# Remove that entries, supposing that has been treated
	for r in res:
		rvals = (sender,r,discardtime)
		c.execute("DELETE FROM returnpath WHERE number = ? and sender = ? and timestamp > ?",rvals)
	conn.commit()
	conn.close()
	if len(res) > 0:	
		return res
	else:
		retunr ('ced@provincia.treviso.it',)

if __name__ == "__main__":
	logging.basicConfig(filename='/var/log/smstools/incoming.log',level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
	logging.info('Service started')
	# Inotify Configurations
	wm = pyinotify.WatchManager()  # Watch Manager
	mask = pyinotify.IN_CLOSE_WRITE|pyinotify.IN_CREATE|pyinotify.IN_MOVED_TO
	p = HandleEvents()
	notifier = pyinotify.Notifier(wm, p)
	# Checks all events about messages received
	wdd = wm.add_watch('/var/spool/sms/incoming/', mask, rec=True,auto_add=True)
	notifier.loop()

