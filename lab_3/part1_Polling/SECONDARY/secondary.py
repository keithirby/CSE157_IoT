# Wait to receive string "Requesting Data"
# Reply with sensor measurements

from sensor_server import Sensor_server
HOST = "192.168.1.2"
PORT = 1024


        
def main():
    mySensor = Sensor_server(HOST, PORT)
    mySensor.run_listener()
    host = "192.168.1.1"
    mySensor.send_msg(host,PORT,"*******temp:103**********")
        

if __name__ == '__main__':
    main()
