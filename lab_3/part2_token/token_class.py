import sys
import socket
import selectors
import types
import logging
from classes import i2c_controller
# Set up logging for server.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)
#Setting global defaults like all IP addresses, number of devices, and ports
#NOTE: because of the logic in ring_handler this version does not support more than 9 hosts
#NOTE: KEEP THE HOSTS LIST ORDERED FROM SMALLEST TO LARGEST ON LAST DIGIT OR DOESNT WORK
#NOTE: The code in ring_handler assumes the hosts last digit count up +1 
HOSTS = ["192.168.1.1","192.168.1.2","192.168.1.3"]
TOTAL_HOSTS = 3 
PORT = 1024
TOKEN_HEADER = "token"


class token_server:
    def __init__(self, host, port):
        """
        Initialization of the server class.
        """
        slogger.info(f"__init__: starting...")
        self.sel = selectors.DefaultSelector()
        self._host = host
        self._port = port
        self._no_packet = True
        self.i2c_cont = i2c_controller() # i2c controller

        self._rtemp_list = []
        self._rhumd_list = []
        self._smois_list = []
        self._speed_list = []
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._host, self._port))

        sock.listen()
        sock.setblocking(False)
        self.sel.register(sock, selectors.EVENT_READ, data=None)
        slogger.info(f"__init__: finished")

    
    def run_listener(self):
        """
        Starts listening for connections and starts the main event loop.
        """
        slogger.info("run_listener: starting...")
        try:
            slogger.debug(f"run_listener:self._no_packet = {self._no_packet}")
            while self._no_packet:
                slogger.debug(f"run_listener:self._no_packet = {self._no_packet}")
                try:
                    events = self.sel.select(timeout=5)
                    for key, mask in events:
                        if key.data is None:
                            self.accept_wrapper(key.fileobj)    
                        else:
                            return self.service_connection(key, mask)
                except Exception as error:
                    slogger.error(f"run_listener: error is [{error}]")
                    break
        except KeyboardInterrupt:
            slogger.info("run: Caught keyboard interrupt, exiting...")
        finally:
            #self.sel.close()
            slogger.info("run_listener: finished")
    

    def set_packet_flag_F(self):
        """
        Set the packet received flag to false
        """
        self._no_packet = False


    def set_packet_flag_T(self):
        """
        Set the packet received flag to true
        """
        self._no_packet = True


    def accept_wrapper(self, sock):
        """
        Helper function for accepting and registering new connections
        """
        # Use sock.accept() to start a connection with another device
        conn, addr = sock.accept()
        slogger.debug(f"accept_wrapper: Accepted connection from {addr}.")
        
        # Disable blocking.
        conn.setblocking(False)
        
        # Create data object to monitor for read and write availability.
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        slogger.info(f"accept_wrapper: {data} | {conn} | {type(conn)}")
        
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        # Register connection with selector.
        self.sel.register(conn, events, data=data)


    def service_connection(self, key:selectors.SelectorKey, mask):
        """
        Services the existing connection and calls to unregister upon completion.
        """
        slogger.debug(f"service_connection: Servicing connection from: {key}, {mask}")
        sock = key.fileobj
        data = key.data
        # Check for reads or writes.
        """
        In this model, we are first waiting for new messages from the 
        client connections, so we are reading for data as it arrives 
        and until it stops arriving (end of message). We then switch 
        to writing to the client, sending a reply.
        """
        if mask & selectors.EVENT_READ:
            # At event, it should be ready for read.
            recv_data = sock.recv(1024)
            # As long as data comes in, append it.
            if recv_data:
                data.outb += recv_data
            # When data stops, close the connection.
            else:
                slogger.debug(f"Closing connection to {data.addr}")
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            # At event, it should be ready to write.
            if data.outb:
                """
                EVENT HANDLING CODE HERE:

                At this point, you have received a complete message from 
                one of the client connections and it is stored in 
                data.outb. You can now handle the message however you 
                like. It is good practice to make a new method to handle 
                the message, and then call it here.
                """
                slogger.info(f"handling data: {data.outb}")
                #add twice. list[0],list[1]
                parsed_data = self.packet_parser(data.outb)
                self.result_to_list(parsed_data)
                slogger.debug(f"handling_data: parsed_data is [{parsed_data}]")
                # ADD HANDLING CODE HERE.
                
		        # Unregister and close socket.
                self.unregister_and_close(sock)

                #Return the parsed data packet
                return parsed_data


    def poll_data_to_string(self):
        """
        Creates a new Post Data and adds all the polling data to it
        """
        # Get the polling list (list with all the sensor reads)
        slogger.info(f"packet_post_encapsulator: running...")
        polling_list = self.poll_all()


        #Calculate the entire length of the post packet
        polling_length = len(polling_list)
        header_length = len("Post Data")
        num_commas = 5 # We poll 5 sensors so we need 5 commas as delimiter
        
        #Define the header msg of the packet
        post_packet = "Post Data,"
        
        #compile all the sensor data into one packet
        for data in polling_list:
            slogger.debug(f"post_encap: pre-Data [{data}]")
            slogger.debug(f"    post_encap: pre-post-packet[{post_packet}]")
            data += ","
            post_packet += data

            slogger.debug(f"post_encap: post-post-packet[{post_packet}]")

        slogger.info("packet_post_encapsulator: finished")
        return post_packet
    
    @classmethod
    def create_token_packet(cls):
        """
        Create the token packet for the token ring network
        """ 
        #Define the three main portions of the first token packet
        slogger.info(f"create_token_packet: running...")
        header = TOKEN_HEADER
        footer = "seq:1"
        deliminter = ","
        #Combine the token packet parts into one
        combined = header + deliminter + footer
        slogger.debug(f"create_token_packet: msg is [{combined}]")
        slogger.info(f"create_token_packet: finished")
        #Return the token packet
        return combined
    
    def packet_splitter(cls, packet):
        """
        Split the packet into a list of lists
        """        
        #Create empty list to be used later
        split_list = []
        #Split the packet by the first deliminter
        item_split = packet.split(",")
        slogger.debug(f"packet_splitter: item_split [{item_split}]")
        #split the items from their numbers
        for item in item_split:
            temp = item.split(":")
            split_list.append(temp)
        slogger.debug(f"packet_splitter: split_list [{split_list}]")
        #Return the split list
        return split_list

    @classmethod
    def check_seq_number(cls, packet):
        """
        Helper function to check what the sequence number of the current packet is
        """
        slogger.info("check_seq_number: starting...")
        #If the packet is not empty
        if packet:
            #Set two empty strings to be used later
            seq_check = "" 
            seq_num = ""
            #Split the packet items from eachother
            split_list = cls.packet_splitter(packet)

            #Find the length of the list
            list_length = len(split_list)
            
            #Check the seq # which should be the last item in the list
            seq_item = split_list[list_length - 1] # Should look like [seq, <#>]
            slogger.debug(f"check_seq_number: seq_item [{seq_item}]") 
            if seq_item[0] == "seq":
                slogger.info("check_seq_number: finished")
                slogger.debug(f"check_seq_number: returned number is [{seq_item[1]}]")
                return seq_item[1]
        
        #If it is a empty packet or something else errors return None
        slogger.info("check_seq_number: finished")
        return None


    @classmethod
    def check_if_token_packet(cls, packet):
        """
        Checks if the packet header is the preset token header
        """
        slogger.info("check_if_token_packet: starting...")

        #Check that the packet is not none
        if packet:
            split_list = cls.packet_splitter()
            slogger.debug(f"check_if_token_packet: split_list is [{split_list}]")

            if split_list[0] == TOKEN_HEADER: 
                slogger.debug(f"check_if_token_packet: returning True")
                return True
        
        slogger.debug(f"check_if_token_packet: returning False")
        return False
            
    def packet_adder(self, packet):

    def packet_ring_handler(self, packet,seq_number):
        """
        React to what position we are in the seq number 
        """
        if seq_number < TOTAL_HOSTS:
            #If less than total_hosts we are not the plotting host only last one is
            host_last_digit = self._host[-1] #Grab our current hosts last IP digit
            last_host_ip = HOSTS[-1] #Grab the last host IP address 
            last_host_last_digit = last_host_ip[-1] #Grab the last host's IP address digit
            
            if host_last_digit == last_host_last_digit:
                #Need to send cyclically at the first host 
                send_host = HOSTS[0] #Restart the send host cyclical check
                #add our polling data to the packet
                pass
            else: 
                # send cyclically to the next host in front of it which is +1 on the last digit
                last_digit = int(host_last_digit)
                send_host = HOSTS[last_digit]
                #Add our polling data to the packet


        else: 
            #If not less than or equal to we are the plotting host
            # we dont need to add our polling data to the packet, we can just call it later
            pass
        
    
    def send_msg(self, send_host, send_port, msg):
        """
        Send a socket message to a specfied address and port
        """
        
        # Create a temporary socket and send a message
        slogger.info(f'Attempting msg send to {send_host} on port {send_port}, message is [{msg}]')
        #self.set_packet_flag_T()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Try to connect to the host
            try:
                s.connect((send_host, send_port))
                byte_msg = bytes(msg, 'utf-8')
                s.sendall(byte_msg)
                slogger.debug(f"send_msg: msg is [{byte_msg}]")
                slogger.info(f"send_msg: message sent!")
            
            #If the connection doesnt work print the failure
            except Exception as error:
                slogger.error(f"send_msg: Error is [{error}]")


    def unregister_and_close(self, sock:socket.socket):
        """
        Unregisters and closes the connection, called at the end of service.
        """
        # Set the self._no_packet flag to false because a packet was sent
        slogger.info(f"unregister_and_close: running...")
        self.set_packet_flag()
        slogger.debug("unregister_and_close: Closing connection... No_data" + str(self._no_packet))
        # Unregister the connection.
        try:
            self.sel.unregister(sock)
        except Exception as e:
            slogger.error(f"unregister_and_close: Socket could not be unregistered:\n{e}")
        # Close the connection.
        try:
            sock.close()
        except OSError as e:
            slogger.error(f"unregister_and_close: Socket could not close:\n{e}")
        
        slogger.info("unregister_and_close: finished")
    
    def poll_all(self):
        """
        helper function to poll all 5 sensors and append their data to a 
        list and return it 
        """
        #Create a empty list to append the sensor results too
        slogger.info(f"poll_all: running...")
        poll_list = [] 
        #Poll all 5 of the sensors and append them each to the list
        poll_list.append(self.i2c_cont.getTemp())
        poll_list.append(self.i2c_cont.getHumd())
        poll_list.append(self.i2c_cont.getSoilTemp())   
        poll_list.append(self.i2c_cont.getSoilMoist())
        try:
            poll_list.append(self.i2c_cont.map_volt_value(self.i2c_cont.getADCVoltage()))
        except:
            poll_list.append("winds:ERR") # in the case init adc returns a None
            
        #Return the poll list
        slogger.info(f"poll_all: finished")
        return poll_list
    
    def get_i2c_data(self):
        """
        Poll your own raspberry Pi's data data and properly encasulate it
        """
        try:
            #Grab the current Pi's I2C data
            i2cdata = self.poll_all()
            #properly parse the data
            parsedData = self.packet_parser(i2cdata)
            #Take out the float data and put it in a instance variable
            self.result_to_list(parsedData)
        except Exception as error:
            #Create a empty return list when there is an error
            noData = []
            #Take out the "float data" and put it in a instance variable
            self.result_to_list(noData)
            slogger.info(f"get_i2c_data: i2c error:{error}")

    def packet_parser(self, data):
        """
        Parse a "Post Data" packet and sort the sensor polling data from it
        """
        #Decode and split the data 
        slogger.info(f"packet_parser: starting... {data}")
        if(type(data) == bytes):
            str_data = data.decode()
        elif (type(data) == list):
            str_data = ",".join(data)
        data_results = str_data.split(",")
        slogger.debug(f"packet_parser: decode is [{str_data}]")
        slogger.debug(f"packet_parser: data_results is [{data_results}]")

        #Split the list again to seperate the readings from their string assosciation
        data_results_split = []        
        for combined in data_results:
            #Split the association string from the poll reading (should be a number)
            association, value = combined.split(":")
            #If the poll reading isnt a number we keep it as a string and add to temp_list
            try: 
                value = float(value)
                temp_list = [association, value]
            except ValueError:
                temp_list = [association, value]
            
            #Append to the main results list
            data_results_split.append(temp_list)
            #Clear the temp list
            temp_list = [] 
        slogger.debug(f"packet_parser: second split is [{data_results_split}]")
        slogger.info(f"packet_parser: finished")
        return data_results_split

    def result_to_list(self, data):
        """
        Inputs data from the list of lists to a single instance variable list for plotting data
        """
        if len(data) != 0:
            self._rtemp_list.append(data[0][1])
            self._rhumd_list.append(data[1][1])
            self._smois_list.append(data[3][1])
            self._speed_list.append(data[4][1])
        else:
            #exception for ERR
            self._rtemp_list.append(0)
            self._rhumd_list.append(0)
            self._smois_list.append(0)
            self._speed_list.append(0)

    def reset_data(self):
        """
        Resets instance variable list that is used for plotting data
        """
        print("is in reset_data")
        self._rtemp_list = []
        self._rhumd_list = []
        self._smois_list = []
        self._speed_list = []