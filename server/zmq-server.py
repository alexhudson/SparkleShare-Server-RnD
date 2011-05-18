#!/usr/bin/env python

from SparkleServer import SparkleServer
import zmq
import json

"""
Two ZMQ sockets are used here: one PUB, to broadcast revision change
events, and one PULL to receive updates from clients.
Generally, a SparkleShare would SUB connect to the PUB, and filter on the
repos it's interested in. The PUSH would happen in the server commit 
hook or something.
ZMQ basically does all the work here.
"""
class ZMQSparkleServer(object):
	def setup(self):
		self.ctx = zmq.Context()
		
		self.broadcast = self.ctx.socket(zmq.PUB)
		self.broadcast.bind("tcp://*:9998")
		
		self.command = self.ctx.socket(zmq.PULL)
		self.command.bind("tcp://*:9997")
	
	def run(self):
		self.running = True
		
		while self.running == True:
			incoming = self.command.recv()
			print "Incoming: %s" % (incoming)
			if incoming:
				data = json.loads(incoming)
				if data['command'] == 'new_version':
					self.broadcast.send_unicode(data['repo'], zmq.SNDMORE)
					self.broadcast.send_unicode(data['revision'])

if __name__ == "__main__":
	server = ZMQSparkleServer()
	server.setup()
	server.run()
	exit(0)
