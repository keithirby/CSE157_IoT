"""
This file runs the primary server file that collects data from other IoT devices
"""
from sink_server import Sink_server
HOST = "192.168.1.1"
PORT = 1024

def main(): 
	
	host2 = "192.168.1.2"
	port2 = 1024
	request_data_msg = "Requesting Data" 
	
	
	mySink = Sink_server(HOST, PORT)
	mySink.send_msg(host2, port2, request_data_msg)
	mySink.run_listener()
	
if __name__ == '__main__': 
	main()
