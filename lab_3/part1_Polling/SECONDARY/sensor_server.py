import sys
import socket
import selectors
import types
import logging
HOST = "192.168.1.2"
PORT = 1024

# Set up logging for server.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)


class Sensor_server:
    def __init__(self, host, port):
        """
        Our server will use a host (its own address) and port to listen 
        for connections. It must also use a selector to monitor for events 
        on the socket.
        """
        slogger.debug("__init__: Initializing server...")
        # Set up selector.
        self.sel = selectors.DefaultSelector()
        # Set host and port.
        self._host = host
        self._port = port
        self.no_data = True
        
        
        """
        Setting up the actual server using socket library
        """
        # Mandatory start for setting server socket connections
        slogger.debug("__init__: Starting server...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Binding actual host and port.
        slogger.debug("__init__: \tSetting socket...")
        sock.bind((self._host, self._port))
        
        """
        The socket is all set up and ready to listen for connections.
        """
        sock.listen()
        slogger.info(f"__init__: Listening from port {self._port}.")
        sock.setblocking(False) #dont block the program while we wait on callee-"not busy waiting"
        slogger.info("__init__: Server initialized.")
        
        """
        As mentioned before, we use selectors to monitor for new events 
        by monitoring the socket for changes.
        """
        # Register the socket to be monitored.
        self.sel.register(sock, selectors.EVENT_READ, data=None)
        slogger.debug("__init__: Monitoring set.")
    # Run function.
    
    def send_msg(self, send_host, send_port, msg):
        """
        Send a socket message to a specfied address and port
        """
        
        # self.no_data = True
        # Create a temporary socket and send a message
        slogger.info(f'Attempting msg send to {send_host} on port {send_port}, message is [{msg}]')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((send_host, send_port))
                byte_msg = bytes(msg, 'utf-8')
                s.sendall(byte_msg)
            
    def run_listener(self):
        """
        Starts listening for connections and starts the main event loop. 
        This method works as the main "run" function for the server, 
        kicking off the other methods of this service.
        """
        
        """
        Finally, we arrive at the event loop. This is where the server
        will handle new incoming connections and their ensuing sessions.
        """
        # Event loop.
        try:
            while self.no_data:
                slogger.debug(f"In while loop! {self.no_data}")
                events = self.sel.select(timeout=5)
                self.no_data = False

                for key, mask in events:
                    if key.data is None:
                        """
                        Here, we accept and register new connections.
                        """
                        slogger.debug(f"entering accept_wrapper")
                        self.accept_wrapper(key.fileobj) 
                    else:
                        """
                        Here, we service existing connections. This is 
                        the method where we will include our event-handling
                        code.
                        """
                        slogger.debug(f"entering service_connection")
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            slogger.info("run_listener: Caught keyboard interrupt, exiting...")
        finally:
            self.sel.close()
    # Helper functions for accepting wrappers, servicing connections, and closing.
    def accept_wrapper(self, sock):
        """
        Accepts and registers new connections.
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
                pass # ADD HANDLING CODE HERE.
                
                # Unregister and close socket.
                self.unregister_and_close(sock)
                
    def unregister_and_close(self, sock:socket.socket):
        """
        Unregisters and closes the connection, called at the end of service.
        """
        self.no_data = False
        slogger.debug("unregister_and_close: Closing connection... No_data" + str(self.no_data))
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

"""
Using this simple server class, you should be able to create a server 
that can accept multiple socket connections from multiple clients and 
handle incoming messages.
"""

mySensor = Sensor_server(HOST, PORT)
mySensor.run_listener()
