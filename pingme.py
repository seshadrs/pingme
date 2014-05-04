# !/usr/bin/env python

"""pingme.py: A utility that sends an email when a shell command completes executing."""

__author__      = "Seshadri Sridharan"


import datetime
from email.mime.text import MIMEText
import smtplib
import sys


SUBJECT_PREFIX='PingMe : '


def sendMail(server, address, uname, pwd, subject,content):

	msg = MIMEText(content)
	msg['Subject'] = subject
	msg['From'] = address
	msg['To'] = address

	server = smtplib.SMTP(server)
	server.starttls()
	server.login(uname,pwd)
	server.sendmail(address, [address], msg.as_string())
	server.quit()


server=sys.argv[1]
address=sys.argv[2]
uname=sys.argv[3]
pwd=sys.argv[4]
title=sys.argv[5]


startTime=datetime.datetime.now()

pipedOutput=""
for line in sys.stdin:
	pipedOutput+=line

endTime=datetime.datetime.now()
executionTime = endTime - startTime

content='EXECUTION_TIME : '+str(executionTime)+'\n'+'OUTPUT : '+pipedOutput

sendMail(server,address,uname,pwd,SUBJECT_PREFIX+title,content)

