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
    sht31d_controller = init_components()
    print("temperature: ", sht31d_controller.temperature)
    print("Humidity: ", sht31d_controller.relative_humidity)

#Call to main to start the program 
main()
