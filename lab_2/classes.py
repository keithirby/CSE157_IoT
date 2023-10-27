#General libraries
import board #General library for GPIO 
import busio #For io usage
#Board specfic libraries
import adafruit_sht31d #Library for temp and humd sensor
from adafruit_seesaw.seesaw import Seesaw
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import simpleio #For mapping voltage values to wind speed
#For files
import os

#Constants for mapping the ADC values 
SENSOR_MIN = 0.41
SENSOR_MAX = 0.76
VALUE_MIN  = 0
VALUE_MAX  = 32.4
#Constants for files
FILE_NAME = "polling-log.txt"
FILE_LOCATION = "~/Desktop/"

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
        return "{:.2f}".format(self.tempHumdContr.temperature)
    
    def getHumd(self):
        """
        Get the ambient moisture using the temperature and humidity sensor
        """
        return "{:.2f}".format(self.tempHumdContr.relative_humidity)
    
    def getSoilTemp(self): 
        """
        Get soil tempature using the soil and moisture sensor
        """
        return "{:.2f}".format(self.soilMoistContr.get_temp())
    
    def getSoilMoist(self):
        """
        Get soil moisture using the soil and moisture sensor
        """
        return "{:.2f}".format(self.soilMoistContr.moisture_read())
    
    def map_volt_value(self, voltage):
        """
        Map a voltage to a wind speed value and return it
        """
        mapped_value = "{:.2f}".format(simpleio.map_range(
            voltage, SENSOR_MIN, SENSOR_MAX, VALUE_MIN, VALUE_MAX))
        return mapped_value
    
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

class file_manager:
    def __init__(self):
        """
        Create the file save path from constants defined in the classes.py file and store it
        """
        #Create the save path of where we want the file
        save_path = os.path.expanduser(FILE_LOCATION)
        #Save the file name to the save path
        self.__save_path = os.path.join(save_path, FILE_NAME)

    def write_single(self, item):
        """
        Write a single item to a file, when this is called the file IS overwritten
        """
        with open(self.__save_path, "w") as file:
            file.write(item)
    
    def write_multiple(self, items): 
        """
        Write multiple items to a file, when this is called the file IS overwritten
        """
        with open(self.__save_path, "w") as file:
            for i in items:
                file.writelines(i)
    
    def append_single(self, item):
        """
        Append a single item to a file, when this is called the file is NOT overwritten
        """
        with open(self.__save_path, "a") as file:
            file.write(item)
    
    def append_multiple(self, items): 
        """
        Append multiple items to a file, when this is called the file is NOT overwritten
        """
        with open(self.__save_path, "a") as file:
            for i in items:
                file.writelines(i)