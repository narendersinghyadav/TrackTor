import psutil
import binascii
import socket
import ipaddress
"""
**Module Overview:**

This module will implement the funtionality of stem api
|-is_alive - check tor process is alive or killed
|-is_valid_ipv4_address-check for valid ip address
|-authenticate- cookie authentication of control port
|-get_version- get version of tor 
|-get_pid- find pid of tor service
|-get_info- get information like version,exit policy,network status etc
|-set_conf- change the value of one or more configurable variable
|-reset_conf-set the configurable variable to default values
|-get_conf- Request the value of zero or more configuration variable
|-get_ports- retreive informations about listeners of different ports
|-get_network_statuses- Router status info (v3 directory style) for all ORs.
|-get_exit_policy-The default exit policy lines that Tor will *append* to the ExitPolicy config option.
|-prt_check-check validity of ports
|-can_exit_to- check whether one can exit through a particular port
|-get_circuit- get information about circuits present for use
|-port_usage-Usage of particular port
|-get_info_relay- retrieve information from database about a particular relay
|-status-tell status of a circuit BUILT or not
|-build_flag- build flag on circuit and relays
|-path- return path of circuit
|-created- circuit created info
|-signal-signal control port like NEWNYM,RELOAD etc
|-get_fingerprint-the contents of the fingerprint file that Tor writes as a relay, or a 551 if we're not a relay currently.
!-get_network_status-network status of a relay with given fingerprint
"""

def is_alive():
	for proc in psutil.process_iter():
		try:
			if 'tor' in proc.name().lower():
				return True
		except(psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess):
			pass
	return False

def is_valid_ipv4_address(address):
	if not isinstance(address, (bytes, str)):
		return False
	if address.count('.') != 3:
		return False
	for entry in address.split('.'):
		if not entry.isdigit() or int(entry) < 0 or int(entry) > 255:
			return False
		elif entry[0] == '0' and len(entry) > 1:
			return False 
	return True

def authenticate():
	control_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	control_socket.connect(('127.0.0.1',9051))
	signal=bytes('PROTOCOLINFO  \r\n','utf-8')
	control_socket.send(signal)
	rcv=control_socket.recv(4096).decode('utf-8')
	rcv=rcv.splitlines()
	if rcv[0]!='250-PROTOCOLINFO 1':
		return None
	cookie_path=rcv[1].split('"')
	cookie_path=cookie_path[1]
	f=open(cookie_path,"rb")
	q=f.read()
	q=binascii.b2a_hex(q)
	q=q.decode('utf-8')
	signal=bytes('AUTHENTICATE ' +q+' \r\n','utf-8')
	control_socket.send(signal)
	rcv=control_socket.recv(4096).decode('utf-8').split()[0]
	if rcv=='250':
		return control_socket
	return None

def get_version():
	control_socket=authenticate()
	control_socket.send(bytes("GETINFO version \r\n",'utf-8'))
	result=control_socket.recv(4096)
	result=result.decode('utf-8')
	result=result.split('=')
	result=result[1].split(' ')
	return result[0]

def get_pid(name):
	control_socket=authenticate()
	control_socket.send(bytes("GETINFO process/pid \r\n",'utf-8'))
	result=control_socket.recv(4096)
	result=result.decode('utf-8')
	result=result.splitlines()
	result=result[0].split('=')[1]
	pid=result
	return int(pid)

def get_info(query):
	control_socket=authenticate()
	getinfo='GETINFO '+query+" \r\n"
	control_socket.send(bytes(getinfo,'utf-8'))
	result=control_socket.recv(4096)
	result=result+control_socket.recv(4096)
	result=result+control_socket.recv(4096)
	return result


def set_conf(name,new_value):
	control_socket=authenticate()
	setconf='SETCONF '+name+'='+new_value+' \r\n'
	control_socket.send(bytes(setconf,'utf-8'))
	result=control_socket.recv(4096)

def reset_conf(name):
	control_socket=authenticate()
	setconf='SETCONF '+name+'= \r\n'
	control_socket.send(bytes(setconf,'utf-8'))
	result=control_socket.recv(4096)

def get_conf(name):
	control_socket=authenticate()
	control_socket.send(bytes("GETCONF "+ name+" \r\n",'utf-8'))
	result=control_socket.recv(4096)
	result=result.decode('utf-8')
	if result is None or "=" not in result:
		return result
	result=result.split('=')
	result=' '.join(result[1].split())
	return result
	
def get_ports(port_name):
	control_socket=authenticate()
	port_name=port_name.lower()
	control_socket.send(bytes("GETINFO net/listeners/"+ port_name +" \r\n",'utf-8'))
	result=control_socket.recv(4096)
	result=result.decode('utf-8')
	result=result.splitlines()
	result=result[0].split('=')[1]
	if len(result.split())>1 and len(result.split()[0].split(':'))>1:
		result=result.split()[0].split(':')[1][:-1]
	portlist=[]
	if result!='':
		try:
			value=int(result)
			portlist.append(value)
		except ValueError:
			pass
		
	
	return portlist

def get_network_statuses():
	control_socket=authenticate()
	control_socket.send(bytes("GETINFO ns/all \r\n",'utf-8'))
	controlsocket=control_socket.recv(4096).decode('utf-8')

	result=""
	for i in range(0,250):
		result+=controlsocket
		controlsocket=control_socket.recv(4096).decode('utf-8')
	address_list=[]
	or_list=[]
	for line  in result.splitlines():
		if(line[0]=='r'):
			data=line.split()
			if(len(data)==9):
				address_list.append(data[6])
				or_list.append(data[7])
			else:
				continue
	
	return address_list,or_list

def get_exit_policy():
	PRIVATE_ADDRESSES = (
  	'0.0.0.0/8',
  	'169.254.0.0/16',
  	'127.0.0.0/8',
  	'192.168.0.0/16',
  	'10.0.0.0/8',
  	'172.16.0.0/12',
	)
	control_socket=authenticate()
	control_socket.send(bytes("GETINFO address \r\n",'utf-8'))
	address=control_socket.recv(4096).decode('utf-8').split('=')
	if len(address)>=2:
		address=address[1].splitlines()[0]
		PRIVATE_ADDRESSES+=(address,)
	control_socket.send(bytes("GETCONF ExitPolicyRejectPrivate \r\n",'utf-8'))
	exitpolicy=control_socket.recv(4096).decode('utf-8')
	exitpolicy=exitpolicy.split('=')[1]
	exitpolicy=int(exitpolicy)
	if exitpolicy==1:
		acceptance='reject'
	else:
		acceptence='accept'
	result=""
	for ip_address in PRIVATE_ADDRESSES:
		result+=acceptance+' '+ip_address+':*, '
	control_socket.send(bytes("GETINFO exit-policy/default \r\n",'utf-8'))
	result+=control_socket.recv(4096).decode('utf-8').split('=')[1].replace(',',', ')
	return result.splitlines()[0]

def prt_check(prt,port):
	prt=prt.split('-')
	if len(prt)==2:
		miniport=int(prt[0])
		maxiport=int(prt[1])
	else:
		miniport=int(prt[0])
		maxiport=int(prt[0])	
	if port>=miniport and port<=maxiport:
		return True
	else:
		return False

def can_exit_to(policy,address,port):
	policy=policy.split(',')
	for policy_itr in policy:
		accept=policy_itr.split()[0]
		addr=policy_itr.split()[1].split(':')[0]
		prt=policy_itr.split()[1].split(':')[1]
		if (addr=='*' or ipaddress.ip_address(address) in ipaddress.ip_network(addr)) and (prt=='*' or prt_check(prt,port)):
			 if(accept=='reject'):
			 	return False
			 else:
			 	return True
	return True

def get_circuits():
	control_socket=authenticate()
	control_socket.send(bytes("GETINFO circuit-status \r\n","utf-8"))	
	response=control_socket.recv(4096).decode('utf-8')
	response=response.splitlines()
	circuit_info=[]
	response=response[1:-2]
	for res in response:
		circuit_info.append("CIRC "+res+"\n")
	return circuit_info

def port_usage(port):
	file=open('ports.cfg','r')
	lines=file.readlines()
	port_usg=''
	for line in lines:
		line=line.split()
		if len(line)>3:
			if line[0]=='port':
				if line[1]==str(port):
					port_usg=line[3]
	if port_usg!='':
		return port_usg
	else:
		log_trace("BUG failed to find port usages")
		return None

def get_info_relay(query):
	control_socket=authenticate()
	control_socket.send(bytes("GETINFO "+query+" \r\n",'utf-8'))
	response=control_socket.recv(4096).decode('utf-8')
	if response[0]=='5':
		return None
	response=response.splitlines()[0]
	response=response.split('=')[1]
	return response

def status(circuit_info):
	if len(circuit_info.split())>2 and circuit_info.split()[2]=='BUILT':
		return 'BUILT'
	return 'NOT BUILT'

def build_flags(circuit_info):
	if len(circuit_info.split())<5:
		return []
	circuit_info=circuit_info.split()[4]
	if len(circuit_info.split('='))<2:
		return []
	circuit_info=circuit_info.split('=')[1]
	circuit_info=circuit_info.split(',')
	return circuit_info

def path(circuit_info):
	path_list=[]
	if len(circuit_info.split())<4:
		return []
	circuit_info=circuit_info.split()[3]
	circuit_info=circuit_info.split(',')
	for circ in circuit_info:
		path_list.append(circ.split('~'))
	return path_list

def created(circuit_info):
	if(len(circuit_info.split())<7):
		return ''
	circuit_info=circuit_info.split()[6]
	circuit_info=circuit_info.split('=')[1]
	circuit_info=circuit_info[:10]+" "+circuit_info[11:]
	return circuit_info

def signal(signal_query,control_socket):
	control_socket.send(bytes("SIGNAL "+ signal_query+" \r\n","utf-8"))	
	response=control_socket.recv(4096).decode('utf-8')
	if response.split()[0]=='250':
		return True
	else:
		return False

def get_fingerprint():
	control_socket=authenticate()
	control_socket.send(bytes("GETINFO fingerprint \r\n",'utf-8'))
	result=control_socket.recv(4096)
	response_code=result.decode('utf-8').split()
	if response_code[0]=='551':
		return ""
	fingerprint=result.decode('utf-8').split('=')
	return fingerprint
def get_network_status(fingerprint):
	control_socket=authenticate()
	control_socket.send(bytes("GETINFO ns/id/"+fingerprint+" \r\n",'utf-8'))
	result=control_socket.recv(4096)
	result=result.decode('utf-8')
	dict_network_status={}
	if len(result.split('='))<2:
		return dict_network_status
	result=result.split('=')[1]
	result=result.splitlines()
	flags=result[2]
	result=result[1]
	result=result.split()
	if len(result)>=9:
		dict_network_status["dir_port"]=result[8]
	else:
		dict_network_status["dir_port"]='None'
	if len(result)>=7:
		dict_network_status["or_port"]=result[7]
	else:
		dict_network_status["or_port"]="None"
	dict_network_status["nickname"]=result[1]
	dict_network_status["published"]=result[4]+" "+result[5]
	dict_network_status["flags"]=flags.split()[1:]
	return dict_network_status

