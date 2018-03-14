# addbook.py by Charles Yang
# 3/12/18
# Completed as a coding challenge for EAI Technologies
# an addressbook web API for elasticsearch
# Assumes elasticsearch index is named addressbook and the doc_type is doc


from flask import Flask, request, render_template, flash, abort
from elasticsearch import Elasticsearch
import json
import ast
import re
import math


host = raw_input('Enter host and port of elasticsearch node (host_name:portnos) (ex: localhost:9200): ')

es = Elasticsearch([host])

#A hacky way to generate new IDs. Hopefully no preexisting IDs conflict.
ids = 10000


app = Flask(__name__)
app.config.from_object(__name__)

#returns -1 as ID if no entry exists
def findID(name):
	doc_id = -1
	q = "{\"query\" : {\"match\" : {\"name\" : { \"query\" : \"" + name + "\", \"fuzziness\" : 0 }}}}"
	results = es.search(index = "addressbook", doc_type = "doc", body = q)

	if results['hits']['total'] != 0:
		doc_id = results['hits']['hits'][0]['_id']

	return doc_id


def getNewID():
	global ids
	ids = ids + 1
	return ids


#Lists pageSize number of contacts offset by the page number of pages of pageSize.
#Returns results by query if supplied otherwise matches all
@app.route('/contact', methods = ['GET'])
def listContacts():
	pageSize = request.args.get('pageSize', default = 10, type = int)
	page = request.args.get('page', default = 0, type = int)
	page = page * pageSize
  	query = request.args.get('query')


	if query:
		q = query
		q = "{ \"from\" : " + str(page) + ", \"size\" : " + str(pageSize) + "," + q[1:]
	else: 
		q = "{ \"from\" : " + str(page) + ", \"size\" : " + str(pageSize) + ", \"query\" : { \"match_all\": {}}}"


	results = es.search(index = "addressbook", doc_type = "doc", body = q)

	return json.dumps(results)



#Returns the elasticsearch contact with the given name
@app.route('/contact/<name>', methods = ['GET'])
def getContact(name):
	doc_id = findID(name)
	if doc_id == -1:
		return 'No contact with that name found'

	return json.dumps(es.get(index = "addressbook", doc_type = "doc", id = doc_id))

#Updates a contacts information. 404s if name is not present
@app.route('/contact/<name>', methods = ['PUT'])
def updateContact(name):
	doc_id = findID(name)
	if doc_id == -1:
		abort(404)

	data = request.data
	check = ast.literal_eval(data)
	name = check.get('name')
	number = check.get('phonenumber')

	if not(validName(name)):
		return 'Not a valid name'
	if not(validPhoneNumber(number)):
		return 'Not a valid phonenumber'

	data = "{'doc' : " + data + "}"
	data = ast.literal_eval(data)

	es.update(index = "addressbook", doc_type = "doc", id = doc_id, body = data)

	return 'Contact Updated'

#Deletes a contact with a specific name. 404s if name is not present
@app.route('/contact/<name>', methods = ['DELETE'])
def deleteContact(name):

	doc_id = findID(name)
	if doc_id == -1:
		abort(404)
	else:
		es.delete(index = "addressbook", doc_type = "doc", id = doc_id)
		return 'Contact Deleted'


#Creates a contact with a new ID based on the name field in the data if the name is not already present
@app.route('/contact', methods = ['POST'])
def createContact():
	data = request.data
	data = ast.literal_eval(data)
	name = data['name']
	number = data.get('phonenumber')
	if not(validName(name)):
		return 'Not a valid name'
	if  not(validPhoneNumber(number)):
		return 'Not a valid phonenumber'
	if findID(name) != -1:
		return 'Error: Contact with that name already exists!'

	res = es.create(index = "addressbook", doc_type = "doc", id = getNewID(), body = data)

	return 'Contact Added'

#Returns true for values containing between 3-15 digits
def validPhoneNumber(number):
	if number == None:
		return True

	digits = int(math.log10(number)) + 1

	if digits >= 3 and digits <=15:
		return True


	return False

#Returns true for strings of all lowercase alphabetic characters or one uppercase character followed by all lowercase characters
def validName(name):
	regx = re.compile('[a-zA-Z]?[a-z]+')
	if regx.match(name) == None:
		return False

	else: 
		return True









