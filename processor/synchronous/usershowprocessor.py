#!/usr/bin/env python
# encoding: utf-8
"""
usershowprocessor.py

Created by wenzhenwei on 2012-03-28.
Copyright (c) 2012 snda inc. All rights reserved.
"""

import sys
import os
import json

import Pyro4
import redis

from init import *

class UserShowProcessor(object):

	def example(self):
		# uri = raw_input("what is the Pyro uri of the database handler object?").strip()
		# database_url = raw_input("please input your database url:").strip()
		# database_info = adapter.DatabaseHandler()
		# database_info = Pyro4.Proxy('PYRO:obj_46d0af449b2941c5bb4d0fb4a2f80fa3@localhost:65459')
		database_info = Pyro4.Proxy("PYRONAME:database_handler")
		data = database_info.info('test')
		print data
		return data
	
	def show(self, userid, level=2, require=None):
		# first redis
#		redisHandler = Pyro4.Proxy("PYRONAME:redis_handler")
#		data = redisHandler.userShow(userid, args)
#		if data != None:
#			return data
#		dbHandler = Pyro4.Proxy("PYRONAME:database_handler")
#		data = dbHandler.userShow(userid, args)
		ns = Pyro4.locateNS(host=PYRONSADDR, port=PYRONSPORT)
		uri = ns.lookup("redis_processor")
		redisProcessor = Pyro4.Proxy(uri)
		data = redisProcessor.userShow(userid, level, require)
		if data == None:
			uri = ns.lookup("database_handler")
			dbProcessor = Pyro4.Proxy(uri)
			data = dbProcessor.userShow(userid, level, require)
		#print unescape(str(data))
		print data
		#return str(data)
		#return data
		return json.dumps(data).encode('utf8')
		return json.dumps(data,ensure_ascii=True,encoding='utf8')
		
	# api list
	'''
	def userData(self,userid):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userData(userid)
		return data
	'''
	###
	# api list
	# user
	# user base info
	def userBaseData(self,userid):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userBaseData(userid)
		return data

	# user full info
	def userFullData(self,userid):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userFullData(userid)
		return data


	def userLookup(self, TelOrEmail='', retType='full'):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userLookup(TelOrEmail,retType)
		return data

	###
 	# Contact

	def userContacts(self, user_id, commonParam={}):
		print user_id, commonParam
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userContacts(user_id, commonParam)
		return data

	def userRelationsIdList(self, user_id, commonParam={}):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userRelationsIdList(user_id, commonParam)
		return data

	def userRelationData(self, rel_id):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userRelationData(rel_id)
		return data

	def userContactData(self, rel_id):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userContactData(rel_id)
		return data


	###
 	# In Contact

	def userInRelationsIdList(self, user_id, commonParam={}):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userInRelationsIdList(user_id, commonParam)
		return data

	def	userInContacts(self, user_id, commonParam={}):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userInContacts(user_id, commonParam)
		return data

 	# friends
	###
	
	def userFriends(self, user_id, commonParam={}):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userFriends(user_id, commonParam)
		return data

 	# apps
	###
	def userApps(self, user_id, commonParam={}):
		uri = ns.lookup("database_handler")
		dbProcessor = Pyro4.Proxy(uri)
		data = dbProcessor.userApps(user_id, commonParam)
		return data


# userProcessor = UserProcessor()
# daemon = Pyro4.Daemon()
# uri = daemon.register(userProcessor)
# 
# print "Ready, User Processor Uri is [%s] " % uri
# daemon.requestLoop()
daemon = Pyro4.Daemon(host=LOCALADDR)
up = UserShowProcessor()
up_uri = daemon.register(up)
ns = Pyro4.locateNS(host=PYRONSADDR, port=PYRONSPORT)
ns.register("user_show_processor", up_uri)
daemon.requestLoop()

#daemon = Pyro4.Daemon()
#ns = Pyro4.locateNS(host=PYRONSADDR, port=PYRONSPORT)
#
## uri = daemon.register(database_handler)
## ns.register("database_handler", uri)
## print "Ready, object uri = ", uri
## daemon.requestLoop()
## -----alternatively, using serverDatabaseHandler-----
#Pyro4.Daemon.serveSimple(
#	{
#		UserShowProcessor():"user_show_processor",
#	},
#	host=LOCALADDR,
#	ns = True, verbose = True)
