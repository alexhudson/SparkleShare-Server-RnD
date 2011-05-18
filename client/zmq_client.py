#!/usr/bin/env python

import zmq
import json
import argparse

def watch(repo):
	context = zmq.Context()
	s = context.socket(zmq.SUB)
	s.connect("tcp://localhost:9998")
	s.setsockopt(zmq.SUBSCRIBE, repo)
	
	running = True
	while running:
		event_repo = s.recv(4096)
		data = s.recv(4096)
		if event_repo == repo:
			# even with a filter, this may not be true - the filter only stems
			print "Received on %s: %s" % (repo, data)
	
	s.close()

def notify(repo, rev):
	context = zmq.Context()
	s = context.socket(zmq.PUSH)
	s.connect("tcp://localhost:9997")
	message = json.dumps({'command': 'new_version', 'repo' : repo, 'revision' : rev })
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
