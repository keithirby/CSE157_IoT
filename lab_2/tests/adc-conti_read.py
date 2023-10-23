#Based on code provided by Adafruit found here https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython#python-installation-of-ads1x15-library-2997261
import board #General library for GPIO 
import busio #For io usage
import time #Used for pausing between reads
import simpleio #Used for mapping voltage values to wind speeds
#Bottom two are used for the ADC
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

def init_components():
    #Create a I2C controller
    i2c_bus = busio.I2C(board.SCL, board.SDA)

    #Make a adc controller
    ads = ADS.ADS1015(i2c_bus)
    
    #Setup the channel to read from
    chan = AnalogIn(ads, ADS.P0)
    
    #return channel ADC is reading from
    return chan



#Main function that is the central caller to all other functions
def main():
    print("Getting I2C data")
    #Get the STEMMA  I2C controller
    ads_controller = init_components()
    
    #Used to find current max voltage reading
    v_max = 0.0

    #Setup for using simpleio
    sensor_min = 0.40 
    sensor_max = 0.76
    value_min  = 0
    value_max  = 32.4
    
    #Print the values found
    if ads_controller:
        #If the controller was made print the values continously
        while(1): 
            #Grab values from the ADC
            ads_value    = ads_controller.value
            ads_voltage  = ads_controller.voltage
            #Map the voltage values to a wind speed
            mapped_value = simpleio.map_range(ads_voltage, sensor_min, sensor_max, value_min, value_max)

            #If the current voltage is higher than the max found, replace it with new highest
            if ads_voltage > v_max: 
                v_max = ads_controller.voltage
            
            #Print to the user
            print("ADC value vs voltage: %.2f vs %.2f | max: %.2f | mapped speed %.2f m/s" % 
                  (ads_value, ads_voltage, v_max, mapped_value))

            #Sleep for 1 second inbetween reads
            time.sleep(1) 
    else: 
        #If the controller wasnt made tell the user
        print("ads controller was not initialized")

#Call to main to start the program 
main()
