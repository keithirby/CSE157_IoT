#Based on code provided by Adafruit found here https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
import board 
import digitalio
import busio

#Function that checks if our input and output is working
def check_io(): 
    pin = digitalio.DigitalInOut(board.D4)
    
    #If the io object was created and didnt return none, it worked
    if pin: 
        print("IO is good!", pin)
    else: 
    #Otherwise a io object was not created and io is not working
        print("IO is not working...")


#Function that checks if our i2c is working
def check_i2c(): 
    #Create a i2c object
    i2c = busio.I2C(board.SCL, board.SDA)
    
    #If the i2c object was created and didnt return none, it worked
    if i2c: 
        print("i2c is good!", i2c)
    else:
    #Otherwise a i2c object was not created and i2c isnt working
        print("i2c is not working...")

def main(): 
    #Initial display to the user if the checks crash
    print("Hello! Checking board connections...")
    #Call io check
    check_io()
    #Call i2c check
    check_i2c()

#Call main function
main()
