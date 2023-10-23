import board #General library for GPIO 
import adafruit_sht31d #Library for temp and humd sensor

def init_components():
    #Create a I2C controller
    i2c = board.I2C()

    #Initialize temp and humd sensor
    sht31d = adafruit_sht31d.SHT31D(i2c)


    return sht31d


#Main function that is the central caller to all other functions
def main():
    print("Getting I2C data")
    #Get the sht31d I2C controller
    sht31d_controller = init_components()
    #Print the values found
    if sht31d_controller:
        #If the controller was made print the values
        print("temperature: %0.1f C" % sht31d_controller.temperature)
        print("Humidity: %0.1f " % sht31d_controller.relative_humidity)
    else: 
        #If the controller wasnt made tell the user
        print("sht31d controller was not initialized")

#Call to main to start the program 
main()
