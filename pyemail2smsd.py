#!/usr/bin/env python
""" 
pyemail2smsd.py - A python pipe from postfix to smstools
Copyright (C) 2013 Luca 'remix_tj' Lorenzetto <lorenzettoluca@provincia.treviso.it>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


"""
import email
import sys
import tempfile
import os
import sqlite3
import time

# Set the path of the outgoing folder for smstools
OUTQUEUEDIR = "/var/spool/sms/outgoing/"

# Extracts the body of a message. 
# in_part is a flag to determine if we're or not analyzing a part, to avoid loops on recursion
def getBody(msg):
	b = ""
	for part in msg.walk():
		if part.is_multipart():
			for subpart in part.walk():
				if subpart.get_content_type() == 'text/plain':
					content = subpart.get_payload()
					# at the first empty line after the text, stops building the message
					found = False
					for row in content.splitlines():
						if len(row) > 0 or not found:
							b += row+"\n"
							if len(row)>0:
								found = True
						else:
							break
					else:
						b += ""
			break
		if part.get_content_type() == 'text/plain':
			content = part.get_payload()
			# at the first empty line after the text, stops building the message
			found = False
			for row in content.splitlines():
				if len(row) > 0 or not found:
					b += row+"\n"
					if len(row)>0:
						found = True
				else:
					break
		else:
			b += ""
	return b


def saveReturnPath(sender,dest):
	conn = sqlite3.connect(DBPATH+'return_path.db')
	r = re.compile(r'(\b[\w.]+@+[\w.]+.+[\w.]\b)')
	results = r.findall(sender)
	elements = (results.pop(), dest, int(time.time()))
	c.execute("INSERT INTO returnpath VALUES (?, ?, ?)",elements)
	c.commit()
	conn.close()	

if __name__=="__main__":
	# Keeps the stdin, since is used as pipe on postfix
	inmsg = sys.stdin.read()
	mail = email.message_from_string(inmsg)
	sms = "To: " + mail["X-Original-To"] + "\n\n"	
	body = "\n"
	body += getBody(mail)
	# adds the sender email as signature
	if mail.has_key('From'):
		sender = mail['From']
	else:
		sender = mail['Return-Path']
	saveReturnPath(sender,mail["X-Original-To"])
	body += "--\n"+sender+ "\n"
	sms += body	
	# Write the sms to the OUTQUEUEDIR
	fdsms, fsms = tempfile.mkstemp(prefix="sms-",dir=OUTQUEUEDIR)
	outf=os.fdopen(fdsms,'wt')
	outf.write(sms)
	outf.close()
