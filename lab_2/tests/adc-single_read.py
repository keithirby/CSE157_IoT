import board #General library for GPIO 
import busio #For io usage
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

def init_components():
    #Create a I2C controller
    i2c_bus = busio.I2C(board.SCL, board.SDA)

    #Make a ads controller
    ads = ADS.ADS1015(i2c_bus)
    
    #Setup the channel to read from
    chan = AnalogIn(ads, ADS.P0)
    
    #return channel ADS is reading from
    return chan



#Main function that is the central caller to all other functions
def main():
    print("Getting I2C data")
    #Get the STEMMA  I2C controller
    ads_controller = init_components()
    
    #Print the values found
    if ads_controller:
        #If the controller was made print the values
        print("ADS value:", ads_controller.value)
        print("ADS voltage:", ads_controller.voltage)
    else: 
        #If the controller wasnt made tell the user
        print("STEMMA  controller was not initialized")

#Call to main to start the program 
main()
