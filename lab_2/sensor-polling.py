from datetime import datetime, date #For getting current date and time
import os #For getting actual path when messing with files
from i2c_class import i2c_controller, file_manager
import time


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

def poll_sensors(i2c_cont)->[]:
    """
    Polls all the important sensors reading together and combines and returns a list of them
    """
    #Make a empty list of size 5 for 5 sensor polls
    poll_strs = [None] * 5
    #Fill in the polls list
    poll_strs[0] = "Temperature: " + i2c_cont.getTemp() + "C" + "\n"
    poll_strs[1] = "Humidity: "+ i2c_cont.getHumd() + "%" + "\n"
    poll_strs[2] = "Soil Moisture: " + i2c_cont.getSoilTemp() + "C" + "\n"
    poll_strs[3] = "Soil Temperature: " + i2c_cont.getSoilMoist() + "\n"
    poll_strs[4] = "Wind Speed: "+ i2c_cont.map_volt_value(i2c_cont.getADCVoltage()) + "m/s" + "\n"
    #Return the polls list
    return poll_strs
      
def write_item(file_path, write_item): 
    """
    This function is dedicated to writing one item to a file
    """
    #Write to a file
    with open(file_path, "w") as file: 
         file.writelines(write_item)

def write_items(file_path, write_items): 
    """
    This function is dedicated to writing multiple items to a file
    """
    #Write to a file
    with open(file_path, "w") as file: 
         for i in write_items:
            file.writelines(i)

#Main function that calls all other functions 
def main():
	#Get the I2C device controller
    i2c_cont = create_I2C_controller()

    #Start the file manager
    filer = file_manager()
    #Quickly write name to file once
    user_name = grab_name()
    filer.write_single(user_name)

    
    
    #Start the sensor polling
    print("Hello there! commencing sensor polling...")
    
    num_polls = 6 # 1 date and time poll + 5 sensor polls = 6 polls 

    #While loop that continues until the program is cancelled to write to a file every 5 seconds
    while(1):
        filer.append_single(grab_date_time())
        filer.append_multiple(poll_sensors(i2c_cont))
        print("Write Complete")
        time.sleep(5)


	
    

#Starting the program
main()
