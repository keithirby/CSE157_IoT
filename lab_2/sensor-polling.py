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

def poll_sensors(i2c_cont)->[]:
    sensor_str_1 = "Temperature: " + i2c_cont.getTemp() + "C"
    sensor_str_2 = "Humidity: "+ i2c_cont.getHumd() + "%"
    sensor_str_3 = "Soil Moisture: " + i2c_cont.getSoilTemp() + "C"
    sensor_str_4 = "Soil Temperature: " + i2c_cont.getSoilMoist()
    sensor_str_5 = "Wind Speed: "+ i2c_cont.map_volt_value(i2c_cont.getADCVoltage()) + "m/s"

    print(sensor_str_1)
    print(sensor_str_2)
    print(sensor_str_3)
    print(sensor_str_4)
    print(sensor_str_5)
      
def write_file(): 
    """
    This function is dedicated to writing to a file
    """
    #Setting the path to save the file to
    save_path = os.path.expanduser("~/Desktop/")
    file_name = "report.txt"
    complete_path = os.path.join(save_path, file_name)
    #Write to a file
    with open(complete_path, "w") as file: 
         file.writelines


#Main function that calls all other functions 
def main():
	#Get the I2C device controller
    i2c_cont = create_I2C_controller()
    
    #Start the sensor polling
    print("Hello there! commencing sensor polling...")
    poll_sensors()

	
    

#Starting the program
main()
