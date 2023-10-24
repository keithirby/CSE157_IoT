#General libraries
import board #General library for GPIO 
import busio #For io usage
#Board specfic libraries
import adafruit_sht31d #Library for temp and humd sensor
from adafruit_seesaw.seesaw import Seesaw
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class i2c_controller:
    def __init__(self):
        """
        Initialize the controllers for the temp and humd sensor, soil and moisture sensor, and ADC
        """
        #Create a i2c controller for board 
        i2c_board = board.I2C()

        #Create a i2c controller for busio
        i2c_bus = busio.I2C(board.SCL, board.SDA)

        #Initialize the i2c device specfic controllers
        #For the temperature and humidity sensor
        self.tempHumdContr  = adafruit_sht31d.SHT31D(i2c_board)
        #For the soil and moisture sensor
        self.soilMoistContr = Seesaw(i2c_board, addr=0x36)
        #For the ADC
        ads = ADS.ADS1015(i2c_bus)
        self.adcContr = AnalogIn(ads, ADS.P0)

    def getTemp(self):
        """
        Get the ambient temperature using the temperature and humidity sensor
        """
        return self.tempHumdContr.temperature
    
    def getHumd(self):
        """
        Get the ambient moisture using the temperature and humidity sensor
        """
        return self.tempHumdContr.relative_humidity
    
    def getSoilTemp(self): 
        """
        Get soil tempature using the soil and moisture sensor
        """
        return self.soilMoistContr.get_temp()
    
    def getSoilMoist(self):
        """
        Get soil moisture using the soil and moisture sensor
        """
        return self.soilMoistContr.moisture_read()
    
    def getADCValue(self):
        """
        Get the value from the ADC
        """ 
        return self.adcContr.value
    
    def getADCVoltage(self):
        """
        Get the voltage reading from the ADC
        """
        return self.adcContr.voltage

    

    
    

