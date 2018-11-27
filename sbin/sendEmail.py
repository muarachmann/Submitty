#!/usr/bin/env python3

import smtplib
import json
import os
import sys
from sqlalchemy import create_engine, Table, MetaData

with open(os.path.join("/usr/local/submitty/config", 'database.json')) as open_file:
    OPEN_JSON = json.load(open_file)

EMAIL_USER = OPEN_JSON['email_user']
EMAIL_PASSWORD = OPEN_JSON['email_password']
DB_HOST = OPEN_JSON['database_host']
DB_USER = OPEN_JSON['database_user']
DB_PASSWORD = OPEN_JSON['database_password']

#configures a mail client to send email 
def constructMailClient():
	try:
		#TODO: change hostname for smtp server to a domain name
		client = smtplib.SMTP_SSL('173.194.66.109', 465)
		client.ehlo()
		client.login(EMAIL_USER, EMAIL_PASSWORD)
	except:
		print("Error: connection to mail server failed. check mail config")
		exit(-1) 
	return client 

#gets the email list for a class
def getClassList(semester, course):
	db_name = "submitty_{}_{}".format(semester, course)
	 # If using a UNIX socket, have to specify a slightly different connection string
	if os.path.isdir(DB_HOST):
		conn_string = "postgresql://{}:{}@/{}?host={}".format(DB_USER, DB_PASSWORD, db_name, DB_HOST)
	else:
		conn_string = "postgresql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, db_name)

	engine = create_engine(conn_string)
	db = engine.connect()
	metadata = MetaData(bind=db)

	student_emails = []
	result = db.execute("SELECT user_email FROM users WHERE registration_section IS NOT NULL;")
	for email in result:
		student_emails.append(email)

	return student_emails


def constructMailString(sent_from, sent_to, subject, body):
	return "From %s\nTo:  %s\nSubject: %s\n%s" %(sent_from, sent_to, subject, body)

def constructAnnouncementEmail(thread_title, thread_content, course, student_email):
	body = "Your Intructor Posted a Note\n" + thread_content 
	mail_string = constructMailString(EMAIL_USER, student_email, thread_title, body)
	return mail_string

def sendAnnouncement():
	mail_client = constructMailClient()

	if(len(sys.argv) < 6):
		print("Error: insufficient arguments given - Usage: python3 sendEmail.py {email_type} {semester} {course} {title} {body}")
		exit(-1) 


	#TODO: check arguments length 
	semester = sys.argv[2]
	course = sys.argv[3]
	thread_title = sys.argv[4]
	thread_content = sys.argv[5]
	print("Attempting to Send an Email Announcement. Course: {}, Semester: {}, Announcement Title: {}".format(course, semester, thread_title))

	class_list = getClassList(semester, course)
	for student_email in class_list:
		announcement_email = constructAnnouncementEmail(thread_title, thread_content, course, student_email)
		mail_client.sendmail(EMAIL_USER, student_email, announcement_email)

	print("Sucessfully Emailed Announcement!")

def main():
	try:
		#grab arguments and figure out mail type
		if len(sys.argv) < 2:
			print("Error: email type not given to to email_script")
			return 
		
		email_type = sys.argv[1]

		if email_type == 'announce':
			sendAnnouncement()

	except Exception as e:
		print("Error: " + str(e))


if __name__ == "__main__":
    main()
