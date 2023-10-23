import board #General library for GPIO 
from adafruit_seesaw.seesaw import Seesaw

def init_components():
    #Create a I2C controller
    i2c_bus = board.I2C()

    #Make a Seesaw controller for the STEMMA device at address = 0x36
    ss = Seesaw(i2c_bus, addr=0x36)
    return ss


#Main function that is the central caller to all other functions
def main():
    print("Getting I2C data")
    #Get the STEMMA  I2C controller
    ss_controller = init_components()
    
    #Print the values found
    if ss_controller:
        #If the controller was made print the values
        print("tempature: %0.1f C" % ss_controller.get_temp())
        print("mositure: %0.1f " % ss_controller.moisture_read())
    else: 
        #If the controller wasnt made tell the user
        print("STEMMA  controller was not initialized")

#Call to main to start the program 
main()
