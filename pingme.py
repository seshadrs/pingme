# !/usr/bin/env python

"""pingme.py: A Unix utility that sends an email when a shell command completes executing."""

__author__      = "Seshadri Sridharan"



import ast
import argparse
import datetime
from email.mime.text import MIMEText
import getpass
import os
import pickle
import pyDes
import smtplib
import sys


SUBJECT_PREFIX='PingMe : '
CONFIG_FILE_NAME='.pingme_config'


def sendMail(server, address, uname, pwd, subject,body):
	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = address
	msg['To'] = address
	server = smtplib.SMTP(server)
	server.starttls()
	server.login(uname,pwd)
	server.sendmail(address, [address], msg.as_string())
	server.quit()

def readPipedOutput():
	startTime=datetime.datetime.now()
	pipedOutput=""
	for line in sys.stdin:
		pipedOutput+=line
	endTime=datetime.datetime.now()
	executionTime = endTime - startTime	
	return (executionTime,pipedOutput)


def configFilePath():
	return os.path.expanduser('~')+'/'+CONFIG_FILE_NAME


def getProfiles():
	filePath=configFilePath()
	if os.path.isfile(filePath):
		try:
			return ast.literal_eval(decrypt(pickle.load(open(filePath,'rb'))))
		except:
			pass
	return []

def setProfiles(profiles):
	filePath=configFilePath()
	pickle.dump(encrypt(str(profiles)),open(filePath,'wb'))


def encrypt(data):
	key = pyDes.des("DESCRYPT", pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
	return key.encrypt(data)


def decrypt(encryptedData):
	key = pyDes.des("DESCRYPT", pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
	return key.decrypt(encryptedData, padmode=pyDes.PAD_PKCS5)


def configure():
	profileConfig={}
	profileConfig['profileName']=raw_input('Enter Config Profile Name : ')
	profileConfig['smtpServer']=raw_input('Enter SMTP Server Domain (ex:smtp.gmail.com) : ')
	profileConfig['smtpPort']=raw_input('Enter SMTP Port (ex:587 for Gmail) : ')
	profileConfig['emailAddress']=raw_input('Enter Email Address : ')
	profileConfig['userName']=raw_input('Enter User Name : ')
	profileConfig['password']=getpass.getpass('Enter Password : ')
	pwd=getpass.getpass('Re-enter Password : ')
	while (pwd!=profileConfig['password']):
		print 'Password does not match!'
		profileConfig['password']=getpass.getpass('Enter Password : ')
		pwd=getpass.getpass('Re-enter Password : ')
	yOrN = raw_input('Set this profile as default? (y/n)? : ')
	while yOrN not in ('y','n'):
		yOrN=raw_input("Set this profile as default? Enter 'y' OR 'n' ? : ")
	setAsDefault = True if yOrN=='y' else False

	currentProfiles=getProfiles()
	
	profileExistsAlready=False
	for p in currentProfiles:
		if p['profileName']==profileConfig['profileName']:
			profileExistsAlready=True
			break
	if profileExistsAlready:
		print 'Overwriting profile '+profileConfig['profileName']
		currentProfiles.pop(currentProfiles.index(p))

	if setAsDefault:
		profiles= [profileConfig] + currentProfiles
	else:
		profiles= currentProfiles+[profileConfig]
	setProfiles(profiles)
	print 'Saved profile \''+profileConfig['profileName']+'\'. Your can use pingMe now!'


def erase():
	setProfiles([])
	print 'Erased all profiles'


def getProfile(name=None):
	if name==None:
		if len(getProfiles())>0:
			return getProfiles()[0]
	else:
		for profile in getProfiles():
			if profile['profileName']==name:
				return profile
	return None


def test(profile):
	subject = 'Test Mail'
	body='This is a testmail from PingMe. You profile config works!'
	sendMail(profile['smtpServer']+':'+profile['smtpPort'],profile['emailAddress'],profile['userName'],profile['password'],SUBJECT_PREFIX+subject,body)

def pingme(profile,subject='',body=''):
	sendMail(profile['smtpServer']+':'+profile['smtpPort'],profile['emailAddress'],profile['userName'],profile['password'],SUBJECT_PREFIX+subject,body)

if __name__=="__main__":

	parser = argparse.ArgumentParser(__file__, description='A utility that sends an email when a shell command completes executing.')
	parser.add_argument("--erase", "-e", help="Erase all configuration profiles (encrypted emailids, passwords etc.).", action="store_true")
	parser.add_argument("--configure", "-c", help="Configure email SMTP server, emailid, username, password.", action="store_true")
	parser.add_argument("--profile", "-p", help="Profile Name", type=str)
	parser.add_argument("--subject", "-s", help="Email subject", type=str)
	parser.add_argument("--test", "-t", help="Test setup.", action="store_true")
	args= parser.parse_args()

	if args.configure:
		configure()
	elif args.erase:
		erase()
	else:
		profile=getProfile(args.profile)
		if args.test:
			if profile==None:
				print "You haven't configured a PingMe profile yet. Please Configure now by entering following details"
				configure()
				profile=getProfile(args.profile)
			test(profile)
		else:
			executionTime,pipedOutput=readPipedOutput()
			if profile==None:
				print "You haven't configured a PingMe profile yet. Please Configure now by entering following details"
				configure()
				profile=getProfile(args.profile)
			subject= '' if args.subject==None else args.subject
			body='EXECUTION_TIME : '+str(executionTime)+'\n'+'OUTPUT : '+pipedOutput
			pingme(profile,subject=subject, body=body)



