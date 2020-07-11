"""
**Module Overview:**

This module will implement the funtionality of showing static info

|- Tor_Usage_Info
    - __init__: This function will initialize UI object and other class variables in all files
    - Info: This function will show the static info
"""
import socket
import argparse
import binascii
import time
import os
from datetime import datetime, timedelta
import psutil
import sys
from subprocess import check_output

from TrackTor.Utilities.dna import authenticate,get_version,get_pid
_stderr = sys.stderr
_stdout = sys.stdout
version=get_version() #take care of version
parser = argparse.ArgumentParser()
parser.add_argument("--ctrlport", help="default: 9051 or 9151")
parser.add_argument("--resolver", help="default: autodetected")
args = parser.parse_args()
control_port ='9051'

#CPU and RAM Usage
CPU_Tor1 = 0
RAM_Tor1 = 0

pid=get_pid("tor")
#CPU Usage Percentage
tor = psutil.Process(pid)

class Tor_Usage_Info():
    def __init__(self, ui):
        self.ui = ui
        self.flag = 0

    def Info(self):
        global CPU_Tor1
        global RAM_Tor1
        #Tor Uptime
        Uptime_Sec = (time.time() - tor.create_time())
        Uptime = datetime(1,1,1) + timedelta(seconds = int(Uptime_Sec))
        self.ui.Uptime1.setText(str(Uptime.hour) + ':' + str(Uptime.minute) + ':' + str(Uptime.second))
        if psutil.pid_exists(pid):
            CPU_Tor1 = tor.cpu_percent()
            self.ui.CPU_Tor.setText(str(CPU_Tor1)[0:5] + '%')
            RAM_Tor1 = tor.memory_percent()
        else:
            self.flag = 1
            from  TrackTor.Home import MessageBox
            MessageBox.box.showMessageBox(MessageBox.box,'Alert', 'Tor Services Diconnected. TrackTor is Offline. Reconnect Tor Services and Restart TrackTor.')
            self.ui.uptime_timer.stop()
            self.ui.Disconnect_Tor_Message.show()
            self.ui.Disconnect_Tor.setEnabled(False)
            sys.exit()
            
