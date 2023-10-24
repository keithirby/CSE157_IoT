from datetime import datetime, date #For getting current date and time
import os #For getting actual path when messing with files
from i2c_class import i2c_controller


def grab_name() -> str: 
	"""
	For returning a pre-defined name
	"""
	name_str = "Keith Irby"
	return name_str

def grab_date_time() -> str:
    """
    Grabs the current date and time and formats it before returning it
    """
    time_obj = datetime.now()
    curr_date = date.today()
    curr_time = time_obj.strftime("%H:%M %p")

    # Combine the current date and time, then return it
    curr_combined = str(curr_time) + "\n" + str(curr_date) + "\n"
    return curr_combined

def create_I2C_controller():
	"""
	Creates the i2c controller object and returns it
	"""
	controller = i2c_controller()
	return controller 




#Main function that calls all other functions 
def main():
	#Get the I2C device controller
    i2c_cont = create_I2C_controller()
    
    #Start the sensor polling
    print("Hello there! commencing sensor polling...")
    print("#1", i2c_cont.getTemp())
    print("#2", i2c_cont.getHumd())
    print("#3", i2c_cont.getSoilTemp())
    print("#4", i2c_cont.getSoilMoist())
    print("#5", i2c_cont.getADCValue())
    print("#6", i2c_cont.getADCVoltage())
	
    

#Starting the program
main()
