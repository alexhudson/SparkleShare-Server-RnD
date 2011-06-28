#!/usr/bin/env python
import socket
import select
from lxml import etree
from lxml.builder import E

HOST, PORT = "localhost", 9999

class TCPSparkleServer(object):
	def setup(self, connection):
		s = socket.socket()
		s.bind(connection)
		s.listen(5)
		s.setblocking(0)
		
		""" repo list is a dictionary, keys are the repo names, values
		are arrays of clients registered to receive events from that
		repo.
		socket is our master listening socket; clientlist contains
		the master socket and all connected clients so that we can
		easily listen for changes on all of them. """
		self.repolist = {}
		self.socket = s
		self.clientlist = [s]
	
	def run(self):
		self.running = True
		
		while self.running == True:
			rdy_read, rdy_write, rdy_err = select.select(self.clientlist, [], self.clientlist, 0)
			
			for skt in rdy_read:
				if skt == self.socket:
					client, address = skt.accept()
					self.add_client(client)
				else:
					try:
						incoming = skt.recv(4096)
						if not incoming:
							# no data means client connection closed
							self.remove_client(skt)
						self.incoming_message(skt, incoming)
					except socket.error, msg:
						self.remove_client(skt)
			
			for skt in rdy_err:
				self.remove_client(skt)
	
	def incoming_message(self, client, message):
		if message == '':
			return
		try:
			data = etree.XML(message)
			command = data.xpath('/packet/command/text()')[0]
			repo = data.xpath('/packet/repo/text()')[0]
			readable = data.xpath('/packet/readable/text()')
			if readable:
				readable = readable[0]
			print message
		except:
			print "Error parsing message from client: %s" % (message)
			return
		
		if command == 'register':
			self.register_client_to_repo(client, repo)
		elif command == 'unregister':
			self.unregister_client_from_repo(client, repo)
		elif command == 'new_version':
			self.notify_clients(client, repo, readable)
	
	def register_client_to_repo(self, client, repo):
		if repo not in self.repolist:
			self.repolist[repo] = []
		
		self.repolist[repo].append(client)
	
	def unregister_client_from_repo(self, client, repo):
		self.repolist[repo].remove(client)
	
	def unregister_client(self, client):
		for repo in self.repolist:
			try:
				self.repolist[repo].remove(client)
			except:
				pass # don't care so much this fails
	
	def notify_clients(self, client, repo, revision):
		print "Got to notify clients!"
		command = E.packet(E.command("new_version"), E.repo("%s" % (repo)), E.readable("New revision is %s" % (revision)))
		message = etree.tostring(command, pretty_print=False)
		print "Need to send message: %s" % (message)
		
		if repo in self.repolist:
			for registration in self.repolist[repo]:
				if registration != client:
					# no point informing the client that told us...
					registration.send(message)
	
	def add_client(self, socket):
		self.clientlist.append(socket)
	
	def remove_client(self, socket):
		socket.close()
		self.clientlist.remove(socket)
		self.unregister_client(socket)

if __name__ == "__main__":
	server = TCPSparkleServer()
	if server.setup((HOST, PORT)):
		print "ERROR: Can't bind to port.\n"
		exit(-1)
	server.run()
	exit(0)
