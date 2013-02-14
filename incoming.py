#!/usr/bin/env python
from sys import argv
import os
import time
from pprint import pprint
import pyinotify
import logging
import smtplib


# IN_CLOSE_WRITE event management
class HandleEvents(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
                                
        if os.path.isfile(event.path+'/'+event.name):
		message = email.message_from_file(open(event.path+'/'+event.name))
		if message.has_key('From'):
			sender = message['From'][2:]
			sender += "@smsmaker.com"
		else:
			sender = "unknown@smsmaker.com"
		txt = ''
		for part in message.walk():
			txt += str(part)
		try:
			session = smtplib.SMTP('posta.provincia.treviso.it')
			destination = get_destinations(sender)
                        smtpresult = session.sendmail(sender, destination, txt)
                        logger.info('Delivered sms to '+str(destination))
		except Exception as exc:
                            logging.error('Unable to deliver message to destinations: '+exc.__str__())
		
		
		
	else:
		logging.critical("file "+event.name+" disappeared!");

# Placeholder for future extension
def get_destinations(sender):
	return ['ced@provincia.treviso.it']

if __name__ == "__main__":
	logging.basicConfig(filename='/var/log/smsd/incoming.log',level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
	logging.info('Service started')
	# Inotify Configurations
	wm = pyinotify.WatchManager()  # Watch Manager
	mask = pyinotify.IN_CLOSE_WRITE|pyinotify.IN_CREATE|pyinotify.IN_MOVED_TO
	p = HandleEvents()
	notifier = pyinotify.Notifier(wm, p)
	# Checks all events about messages received
	wdd = wm.add_watch('/var/spool/smsd/incoming/', mask, rec=True,auto_add=True)
	notifier.loop()

