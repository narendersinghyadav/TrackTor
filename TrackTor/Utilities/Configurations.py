"""
**Module Overview:**

This module will implement the funtionality of showing Configurations of Tor

|- _Configurations
	- __init__: This function will initialize UI object and other class variables in all files
	- _Config_CurrentVal: This function will configure the current value
    - manual: This function will information from stem module
    - _Config_ChangeVal: This function will configure the changed value
    - _Config_Reset: This function will configure the changed value to its original version
    - _Config_DropDown: This function will configure the drop down window for time intervals
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import time
import os
import threading
from TrackTor.Utilities.dna import get_info,set_conf,reset_conf,get_conf,is_alive
import psutil

SIZE_UNITS_BITS = (
  (140737488355328.0, ' Pb', ' Petabit'),
  (137438953472.0, ' Tb', ' Terabit'),
  (134217728.0, ' Gb', ' Gigabit'),
  (131072.0, ' Mb', ' Megabit'),
  (128.0, ' Kb', ' Kilobit'),
  (0.125, ' b', ' Bit'),
)

SIZE_UNITS_BYTES = (
  (1125899906842624.0, ' PB', ' Petabyte'),
  (1099511627776.0, ' TB', ' Terabyte'),
  (1073741824.0, ' GB', ' Gigabyte'),
  (1048576.0, ' MB', ' Megabyte'),
  (1024.0, ' KB', ' Kilobyte'),
  (1.0, ' B', ' Byte'),
)
TIME_UNITS = (
  (86400.0, 'd', ' day'),
  (3600.0, 'h', ' hour'),
  (60.0, 'm', ' minute'),
  (1.0, 's', ' second'),
)
def size_label(byte_count, decimal = 0, is_long = False, is_bytes = True, round = False):


  if is_bytes:
    return _get_label(SIZE_UNITS_BYTES, byte_count, decimal, is_long, round)
  else:
    return _get_label(SIZE_UNITS_BITS, byte_count, decimal, is_long, round)
def _get_label(units, count, decimal, is_long, round = False):


  label_format = '%%.%if' % decimal

  if count < 0:
    label_format = '-' + label_format
    count = abs(count)
  elif count == 0:
    units_label = units[-1][2] + 's' if is_long else units[-1][1]
    return '%s%s' % (label_format % count, units_label)

  for count_per_unit, short_label, long_label in units:
    if count >= count_per_unit:
      if not round:
       

        count -= count % (count_per_unit / (10 ** decimal))

      count_label = label_format % (count / count_per_unit)

      if is_long:
       

        if decimal > 0:
          is_plural = count > count_per_unit
        else:
          is_plural = count >= count_per_unit * 2

        return count_label + long_label + ('s' if is_plural else '')
      else:
        return count_label + short_label
def time_label(seconds, decimal = 0, is_long = False):
 

  return _get_label(TIME_UNITS, seconds, decimal, is_long)
CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cached_tor_manual.sqlite')
DATABASE = None 
def is_sqlite_available():
  

  try:
    import sqlite3
    return True
  except ImportError:
    return False
def query(query, *param):
  

  if not is_sqlite_available():
    raise ImportError('Querying requires the sqlite3 module')

  import sqlite3


  global DATABASE

  if DATABASE is None:
    DATABASE = sqlite3.connect(CACHE_PATH)

  return DATABASE.execute(query, param)



from functools import lru_cache

Configurations = {}
Value_Type = {}


class _Configurations():
	def __init__(self, ui):
	    self.ui = ui
	    if not is_alive():
	        import sys
	        sys.stderr = open("Error.txt", "w")


	def _Config_CurrentVal(self):
	    self.ui.Conf_Label.hide()
	    name = self.ui.Config_Options.currentText()
	    self.ui.Config_CurrentVal.setText(Configurations[name])
	    @lru_cache()
	    def manual(option):
	        result = query('SELECT category, usage, summary, description, position FROM torrc WHERE key=?', option.upper()).fetchone()
	        if result==None:
	        	result[0]=''
	        	result[1]=''
	        	result[2]=''
	        item = QtWidgets.QListWidgetItem('Type :  ' + result[0])
	        item1 = QtWidgets.QListWidgetItem('Domain :  ' + result[1])
	        item2 = QtWidgets.QListWidgetItem('Description :  ' + result[2] + '.')
	        item3 = QtWidgets.QListWidgetItem('')
	        self.ui.Config_Desc.clear()
	        self.ui.Config_Desc.addItem(item3)
	        self.ui.Config_Desc.addItem(item3)
	        self.ui.Config_Desc.addItem(item)
	        self.ui.Config_Desc.addItem(item1)
	        self.ui.Config_Desc.addItem(item2)
	    manual(name)

	def _Config_ChangeVal(self):
		if not is_alive():
		    import TrackTor.Home.MessageBox
		    MessageBox.box.showMessageBox(MessageBox.box,'Message','Unable to connect to Tor! Hence can not update Configurations!')

		else:
			self.ui.Conf_Label.hide()
			name = self.ui.Config_Options.currentText()
			new_val = self.ui.Config_NewVal.text()
			self.ui.Config_CurrentVal.setText(new_val)
			self.ui.Config_NewVal.setText('')
			if new_val != Configurations[name]:

				try:
					if Value_Type[name] == 'Boolean':
					    if new_val.lower() == 'true':
					     new_val = '1'
					    elif new_val.lower() == 'false':
					     new_val = '0'
					elif Value_Type[name] == 'LineList':
					    new_val = new_val.split(',')  # set_conf accepts list inputs
					set_conf(name, new_val)
					self.ui.Conf_Label.setText("<html><head/><body><p align=\"center\"><span style=\" color:#227319;\">Value has been updated</span></p></body></html>")
					self.ui.Conf_Label.show()
				except Exception as exc:
					self.ui.Conf_Label.setText(str(exc))
					self.ui.Conf_Label.show()


	def _Config_Reset(self):
	    if not is_alive():
	        import MessageBox
	        MessageBox.box.showMessageBox(MessageBox.box,'Message','Unable to connect to Tor! Hence can not Reset Configurations')
	    else:
	        name = self.ui.Config_Options.currentText()
	        reset_conf(name)

	def _Config_DropDown(self):
	    for line in get_info('config/names').splitlines():
	        line_comp = line.split()
	        if len(line_comp)==1 or line_comp[0]==b'250':
	        	continue          
	        name, value_type = line_comp[0].decode('utf-8'), line_comp[1].decode('utf-8')
	        values = get_conf(name)

	        if not values:
	            Config = '<none>'
	        elif value_type == 'Boolean' and values[0] in ('0', '1'):
	            if values[0] == '0':
	                Config = 'False'
	            else:
	                Config = 'True'
	        elif value_type == 'DataSize' and values[0].isdigit():
	            Config = size_label(int(values[0]))
	        elif value_type == 'TimeInterval' and values[0].isdigit():
	            Config = time_label(int(values[0]), is_long = True)
	        else:
	            Config = values[0]
	        Value_Type.update({name:value_type})
	        Configurations.update({name:Config})
	        self.ui.Config_Options.addItem(name)
	    self._Config_CurrentVal()
