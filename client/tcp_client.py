#!/usr/bin/env python
import socket
import select
from lxml import etree
from lxml.builder import E
import argparse

HOST = 'localhost'
PORT = 9999

def connect():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	return s

def watch(repo):
	s = connect()
	command = E.packet(E.command("register"), E.repo(repo))
	message = etree.tostring(command, pretty_print=False)
	s.send(message)
	
	running = True
	while running:
		rdy_read, rdy_write, rdy_err = select.select([s], [], [s], 0)
		data = s.recv(4096)
		if not data:
			running = False # server died on us..
		print "Received: %s" % (data)
	
	s.close()

def notify(repo, rev):
	s = connect()
	command = E.packet(E.command("new_version"), E.repo(repo), E.readable("New revision is %s" % (rev)))
	message = etree.tostring(command, pretty_print=False)
	s.send(message)
	s.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('command', metavar='[watch|notify]', type=str, help='command')
	parser.add_argument('repo', metavar='<repo>', type=str, help='name of the repo')
	parser.add_argument('-revision', metavar='<revision>', type=str, help='current rev of repo')
	args = parser.parse_args()
	
	if args.command == 'watch':
		watch(args.repo)
	elif args.command == 'notify':
		notify(args.repo, args.revision)
	else:
		print "Unknown command %s" % (args.command)
