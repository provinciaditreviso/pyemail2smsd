#!/usr/bin/env python
import email
import sys
import tempfile
import os

OUTQUEUEDIR = "/var/spool/sms/outgoing/"


mail = email.message_from_string(sys.stdin.read())
sms = ""
sms += "To: " + mail["X-Original-To"] + "\n"

body = "\n"


for part in mail.walk():
	if part.get_content_type() == 'text/plain':
		content = part.get_payload()
		for row in content.splitlines():
			if len(row) > 0:
				body += row+"\n"
			else:
				break
	else:
		body = ""

body += "-- "+mail["From"]+ "\n"

sms += body

fdsms, fsms = tempfile.mkstemp(prefix="sms-",dir=OUTQUEUEDIR)
outf=os.fdopen(fdsms,'wt')
outf.write(sms)
outf.close()
