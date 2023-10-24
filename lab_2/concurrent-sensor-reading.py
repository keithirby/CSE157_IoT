import asyncio
import datetime
import logging
from i2c_class import i2c_controller, file_manager




#Setting format for logger
logging.basicConfig(format='[%(asctime)s] (%(name)s) %(levelname)s: %(message)s',)
#  Set up loggers for each of our concurrent functions.
logger_1 = logging.getLogger('temp & humidity')
logger_2 = logging.getLogger('soil temp & moisture')
logger_3 = logging.getLogger('wind speed')
#Set the level for the loggers
logger_1.setLevel(logging.INFO)
logger_2.setLevel(logging.INFO)
logger_3.setLevel(logging.INFO)


#Set the level for the logger 
file_handler = logging.FileHandler('example.log')
file_handler.setLevel(logging.INFO)
# Add the file handler to each of our loggers.
logger_1.addHandler(file_handler)
logger_2.addHandler(file_handler)
logger_3.addHandler(file_handler)


#First function for logging temp and humidity every 5 second by default 
async def concurrent_funct_1(i2c_cont, interval = 5):

    #While loop that continues the sensor reading until the program is cancelled
    while True:
        temp = "Temperature: " + i2c_cont.getTemp() + "C"
        humd = "Humidity: "+ i2c_cont.getHumd() + "%"
        
        logger_1.info(f"{temp} | {humd}")
        await asyncio.sleep(interval)

#Second function for logging soil temp and moisture every 6 second by default 
async def concurrent_funct_2(i2c_cont, interval = 6):

    #While loop that continues the sensor reading until the program is cancelled
    while True:
        temp = "Soil Temperature: " + i2c_cont.getSoilTemp() + "C"
        moist = "Soil Moisture: " + i2c_cont.getSoilMoist() 
        
        logger_1.info(f"{temp} | {moist}")
        await asyncio.sleep(interval)

#Third function for logging wind speed every 3 second by default 
async def concurrent_funct_3(i2c_cont, interval = 3):

    #While loop that continues the sensor reading until the program is cancelled
    while True:
        wind_speed = "Wind Speed: "+ i2c_cont.map_volt_value(i2c_cont.getADCVoltage()) + "m/s"
 
        logger_1.info(f"{wind_speed})
        await asyncio.sleep(interval)

async def main():

    """
    Call the coroutine functions to be added to asyncio gather
    """
    i2c_cont = i2c_controller()

    await asyncio.gather(
        concurrent_funct_1(i2c_cont, 5),
        concurrent_funct_2(i2c_cont, 6),
        concurrent_funct_3(i2c_cont, 3)
    )

if __name__ == "__main__":
    #Use try and except for catching user ending the program 
    try:
        """
        Once we have defined our main coroutine, we will run it using asyncio.run().
        """
        asyncio.run(main())
    except KeyboardInterrupt:
        """
        If the user presses Ctrl+C, we will gracefully exit the program.
        """
        print("Exiting program...")
        exit(0)
