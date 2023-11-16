import logging
import selectors
import socket
import types
import matplotlib.pyplot as plt

# Set up logging for server.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
slogger = logging.getLogger(f"(srv)")
slogger.setLevel(level=logging.DEBUG)

class Sink_server:
    def __init__(self, host, port):
        """
        Initialization of the server class.
        """
        self.sel = selectors.DefaultSelector()
        self._host = host
        self._port = port
        self._no_packet = True
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

    def set_packet_flag(self):
        """
        Set the packet received flag to true
        """
        self._no_packet = False

    def send_msg(self, send_host, send_port, msg):
        """
        Send a socket message to a specified address and port
        """
        #while True:
        #    print("p")
        # Create a temporary socket and send a message
        slogger.info(f'send_msg: Attempting msg send to {send_host} on port {send_port}, message is [{msg}]')
        try:
            sock = socket.create_connection((send_host, send_port), timeout=2)
            #sock.setblocking(0)
            byte_msg = bytes(msg, 'utf-8')
            sock.sendall(byte_msg)
            slogger.debug(f"send_msg: msg is [{byte_msg}]")
            #sock.setblocking(1)
            return True
        except socket.timeout:
            print("timeout")
            return False
        except ConnectionRefusedError:
            return False

    def run_listener(self):
        """
        Starts listening for connections and starts the main event loop.
        """
        try:
            while self._no_packet:
                events = self.sel.select(timeout=5)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        return self.service_connection(key, mask)
        except KeyboardInterrupt:
            slogger.info("run: Caught keyboard interrupt, exiting...")
        finally:
            self.sel.close()

    def accept_wrapper(self, sock):
        """
        Accepts and registers new connections.
        """
        conn, addr = sock.accept()
        slogger.debug(f"accept_wrapper: Accepted connection from {addr}.")

        conn.setblocking(False)

        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key: selectors.SelectorKey, mask):
        """
        Services the existing connection and calls to unregister upon completion.
        """
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                data.outb += recv_data
            else:
                slogger.debug(f"Closing connection to {data.addr}")
                self.sel.unregister(sock)
                sock.close()
                if mask & selectors.EVENT_WRITE:
                    if data.outb:
                        slogger.info(f"handling data: {data.outb}")
                        self._data_list = self.packet_parser(data.outb)
                        # Unregister and close socket.
                        self.unregister_and_close(sock)
                        return self._data_list
    
    def packet_parser(self, data):
        str_data = data.decode()
        data_results = str_data.split(",")
        exampleList = []
        for i in range(1, 6):
            exampleList.append(data_results[i].split(":"))

        #add the data of sec1 and sec2 to the list when it runs
        #add the third data from direct I2C input to the host pi
        self._rtemp_list.append(float(exampleList[1]))
        self._rhumd_list.append(float(exampleList[1]))
        self._smois_list.append(float(exampleList[1]))
        self._speed_list.append(float(exampleList[1]))

        return exampleList

    def find_average(self, numbers):
        average = sum(numbers) / len(numbers)  # Calculate the average
        return average

    def plot_data(self, i):
        """
        APPEND THE DATA FROM THE OWN RASPBERRY PI
        after receiving data from the two secondary pis but before plotting data
        """
        lables = ['Sec1', 'Sec2', 'Primary', 'Avg']
        
        #finding the average of three pi results        
        rtemp_avg = self.find_average(self._rtemp_list)
        rhumd_avg = self.find_average(self._rhumd_list)
        smois_avg = self.find_average(self._smois_list)
        speed_avg = self.find_average(self._speed_list)        
        
        #adding average to the list
        self._rtemp_list.append(rtemp_avg)
        self._rhumd_list.append(rhumd_avg)
        self._smois_list.append(smois_avg)
        self._speed_list.append(speed_avg)
        
        fig, axs = plt.subplots(2,2,figsize=(10,8))

        axs[0,0].scatter(lables, self._rtemp_list, marker = 'o')
        axs[0,0].set_title('Temperature Sensor')
        #axs[0,0].set_ylables('Temperature(C)')

        axs[0,1].scatter(lables, self._rhumd_list, marker = 'o')
        axs[0,1].set_title('Humidity Sensor')
        #axs[0,1].set_ylables('Humidity(%)')

        axs[1,0].scatter(lables, self._smois_list, marker = 'o')
        axs[1,0].set_title('Soil Moisture Sensor')
        #axs[1,0].set_ylables('Soil Moisture')

        axs[1,1].scatter(lables, self._speed_list, marker = 'o')
        axs[1,1].set_title('Wind Sensor')
        #axs[1,1].set_ylables('Wind speed(m/s)')

        plt.tight_layout()
        filename = f'polling-plot-{i}.png'
        return plt.savefig(filename)

    def reset_data(self):
        self._rtemp_list = []
        self._rhumd_list = []
        self._smois_list = []
        self._speed_list = []
        
    def unregister_and_close(self, sock: socket.socket):
        """
        Unregisters and closes the connection, called at the end of service.
        """
        self.set_packet_flag()
        slogger.debug("unregister_and_close: Closing connection...")
        try:
            self.sel.unregister(sock)
        except Exception as e:
            slogger.error(f"unregister_and_close: Socket could not be unregistered:\n{e}")

        try:
            sock.close()
        except OSError as e:
            slogger.error(f"unregister_and_close: Socket could not close:\n{e}")
