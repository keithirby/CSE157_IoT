CSE 157 Internet of Things (IoT) Lab #2
# Objective
The task of this lab is to familiarize students with how to use the 
Adafruit pre-built python libraries for interfacing with their sensors. 
Also covered is better virtual environment usage, code abstraction, and 
asynchronous sensor readings. 

# File Descriptions
### `tests/` folder 
The test folder contains single read tests for each sensor used in this lab. Plus there is a single continous read test for the ADC. 

### `sensor-polling.py` 
This file polls all of the sensors used in the lab and writes them to a file on the deskop.

### `concurrent-sensor-reading.py`
This file is meant to be an improvment and slightly different version of `sensor-polling.py` file. First, its an improvemnt in that print is no longer used to notify the user and a logger was installed instead. Second, asyncfunctions are used to poll from the sensiors instead of synchronous functions.

### `classes.py`
This is a support file that provides two classes used in some of the files above. The first class is used for interfacing and polling all the sensors. The second class is a file manager.