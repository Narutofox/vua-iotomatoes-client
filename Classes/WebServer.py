import RPi.GPIO as GPIO
import os
from time import sleep
from http.server import BaseHTTPRequestHandler, HTTPServer
from ActionManager import ActionManager


class MyServer(BaseHTTPRequestHandler):
    # A special implementation of BaseHTTPRequestHander for reading data from
    #  and control GPIO of a Raspberry Pi
	
	def __init__(self, manager):
		self.manager = manager
		
	def do_HEAD(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def _redirect(self, path):
		self.send_response(303)
		self.send_header('Content-type', 'text/html')
		self.send_header('Location', path)
		self.end_headers()

	def do_GET(self):
		#'curl http://server-ip-address:port'		
		self.manager.getRuleset()
		self.send_response(200)
		self.send_header('Content-Length', '0')
		self.end_headers()


