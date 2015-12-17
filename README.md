pyemail2smsd
============

A python pipe from postfix to smstools

Usage
=====
After installing postfix and smstools package, add to master.cf this line:
```
smstools  unix  -       n       n       -       -       pipe
  flags=DORhu user=smsd argv=/path/to/pyemail2smsd.py
```

Then create a file /etc/postfix/mailbox_transport_maps with this content:
```
 smsd@my.host.name smstools:
```

and /etc/postfix/virtual_aliases with this content:
```
 @sms.local  smsd@my.host.name
```

Execute this commands:

```
 postmap /etc/postfix/mailbox_transport_maps
 postmap /etc/postfix/virtual_aliases
```

and add to main.cf this configuration directives:
```
virtual_alias_maps = hash:/etc/postfix/virtual_aliases
transport_maps = hash:/etc/postfix/mailbox_transport_maps
smstools_destination_recipient_limit = 1
```

Restart postfix and the program will pass all the messages sent to *@sms.local to the outgoing directory of smstools
