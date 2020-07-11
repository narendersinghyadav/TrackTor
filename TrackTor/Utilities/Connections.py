"""
**Module Overview:**

This module will implement the funtionality of showing all the connections

- connections: This function will show all the connections

"""

import argparse
import collections
import time
import os
import distutils.spawn
import subprocess
import re
import threading
import enum
import platform
import logging 
import codecs
import socket
import sys
import base64
import ipaddress
from collections import OrderedDict

from TrackTor.Utilities import StaticInfo
from TrackTor.Utilities.dna import get_pid,get_ports,get_network_statuses,get_exit_policy,prt_check,can_exit_to,get_circuits,port_usage,is_valid_ipv4_address
'''
INBOUND_OR = 'Inbound to our ORPort'
INBOUND_DIR = 'Inbound to our DirPort'
INBOUND_CONTROL = 'Inbound to our ControlPort'
OUTBOUND = 'Outbound to a relay'
'''

categories = collections.OrderedDict((
('INBOUND_OR', []),
('INBOUND_DIR', []),
('INBOUND_CONTROL', []),
('OUTBOUND', []),
('EXIT', []),
('CIRCUIT', [])
))
UNDEFINED = '<Undefined_ >'
LOGGER = logging.getLogger('TrackTor')
LOGGER.setLevel(logging.DEBUG -5 )

def log_debug(message):
  LOGGER.log(logging.DEBUG , message)
def log_trace(message):
  LOGGER.log(logging.DEBUG-5 , message)




class Connection(collections.namedtuple('Connection', ['local_address', 'local_port', 'remote_address', 'remote_port', 'protocol', 'is_ipv6'])):
	pass


import subprocess
import platform
system=platform.system()

def get_connection():
	if system=='Linux':
		try:
			process=subprocess.check_output("netstat -npWt | grep 'ESTABLISHED' | grep 'tor'",shell=True).decode('utf-8')
			process=process.splitlines()
			lconnection=[]
			for proc in process:
				local_addr=proc.split()[3].split(':')[0]
				local_port=proc.split()[3].split(':')[1]
				remote_port=proc.split()[4].split(':')[1]
				remote_addr=proc.split()[4].split(':')[0]
				lconnection.append(Connection(local_addr,local_port,remote_addr,remote_port,'tcp',False))
			return lconnection
		except Exception:
			log_trace("BUG: Failed to recognise command")
			return ""
	elif system=='Windows':
		try:
			pid=get_pid()
			process=subprocess.check_output('netstat -ano | findstr "ESTABLISHED"|findstr "TCP" |findstr '+str(pid),shell=True).decode('utf-8')
			process=process.splitlines()
			lconnection=[]
			for proc in process:
				local_addr=proc.split()[1].split(':')[0]
				local_port=proc.split()[1].split(':')[1]
				remote_port=proc.split()[2].split(':')[1]
				remote_addr=proc.split()[2].split(':')[0]
				lconnection.append(Connection(local_addr,local_port,remote_addr,remote_port,'tcp',False))
			return lconnection
		except Exception:
			log_trace("BUG: Failed to recognise command")
			return ""
	elif system=="Darwin":
		try:
			process=subprocess.check_output('lsof -wnPi | grep "ESTABLISHED" | grep "tor"| grep "TCP"',shell=True).decode('utf-8')
			process=process.splitlines()
			lconnection=[]
			for proc in process:
				local_addr=proc.split()[8].split('->')[0].split(':')[0]
				local_port=proc.split()[8].split('->')[0].split(':')[1]
				remote_addr=proc.split()[8].split('->')[1].split(':')[0]
				remote_port=proc.split()[8].split('->')[1].split(':')[1]
			return lconnection
		except Exception:
			log_trace("BUG: Failed to recognise command")
			return ""
	else:
		from  TrackTor.Home import MessageBox
		MessageBox.box.showMessageBox(MessageBox.box,'Alert', 'This os is not supported')
		sys.exit()
###copied
from TrackTor.Utilities.dna import is_alive,authenticate
from TrackTor.Utilities import StaticInfo
	
def connections():
    args = StaticInfo.args

    if not (is_alive()):
        return

    pid = StaticInfo.pid


    policy = get_exit_policy()
    relays = {}  # address => [orports...]
    list_add,list_or=get_network_statuses()
    for desc_add,desc_or in zip(list_add,list_or):
        relays.setdefault(desc_add, []).append(desc_or)

    exit_connections = {}  # port => [connections]

    for conn in get_connection():
        global categories

        if conn.local_port in get_ports('OR'):
          categories['INBOUND_OR'].append(conn)
        elif conn.local_port in get_ports('DIR'):
          categories['INBOUND_DIR'].append(conn)
        elif conn.local_port in get_ports('CONTROL'):
          categories['INBOUND_CONTROL'].append(conn)
        elif conn.remote_port in relays.get(conn.remote_address, []):
          categories['OUTBOUND'].append(conn)
        elif can_exit_to(policy,conn.remote_address, conn.remote_port):
          categories['EXIT'].append(conn)
          exit_connections.setdefault(conn.remote_port, []).append(conn)
        else:
          categories['OUTBOUND'].append(conn)
    circ = get_circuits()
    for conn in circ:
        categories['CIRCUIT'].append(conn)


    if exit_connections:
        total_ipv4, total_ipv6 = 0, 0

        for port in sorted(exit_connections):
          connections = exit_connections[port]
          ipv4_count = len([conn for conn in connections if is_valid_ipv4_address(conn.remote_address)])
          ipv6_count = len(connections) - ipv4_count
          total_count = len(connections)
          total_ipv4, total_ipv6 = total_ipv4 + ipv4_count, total_ipv6 + ipv6_count

          usage = port_usage(port)
          label = '%s (%s)' % (port, usage) if usage else port

connections()
