"""
**Module Overview:**

This module will implement the funtionality of New Identity and Reload Tor

|- actions
	- NewIdentity: This function will generate new identity
	- ReloadTor: This function will reload tor
"""

import os
import time
import argparse
import socket
import threading  

from TrackTor.Home import DialogBox
from TrackTor.Utilities import StaticInfo
from TrackTor.Utilities import Connections
from TrackTor.Utilities.dna import signal
args = StaticInfo.args
control_socket=StaticInfo.authenticate()
def authenticate():
	if control_socket ==None:
		return False
	return True
	
class actions():
	def NewIdentity(self):

		"""
		Requests a new identity and provides information about the same.
		"""
		if not authenticate():
			DialogBox.box.showMessageBox(DialogBox.box,'Message','Unable to connect to Tor. Are you sure it is running?')
		else :
			

			if not signal("NEWNYM",control_socket):
				DialogBox.box.showMessageBox(DialogBox.box,'Message','Sorry! New Relays are not available at the moment!')

			else:
				DialogBox.box.showMessageBox(DialogBox.box,'Message','New Identity has been generated!')


	def ReloadTor(self):
		"""
		Requests a reload from torrc file
		"""
		
		if not authenticate():
			DialogBox.box.showMessageBox(DialogBox.box,'Message','Unable to connect to Tor. Are you sure it is running?')
		else:
			
			signal("RELOAD",control_socket)
			from TrackTor.Home.Edit_Torrc import _Edit_Torrc
			DialogBox.box.showMessageBox(DialogBox.box,'Message','Torrc has been reloaded!')
			_Edit_Torrc.Close_Edit_Torrc(_Edit_Torrc)
