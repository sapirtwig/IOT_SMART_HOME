# Smart_DHT_Sensor_Project

This project is a Python-based GUI application built with PyQt5 for monitoring and controlling home environmental data (temperature and humidity) using MQTT communication. 
It features real-time data visualization, manual control of an A/C unit, and send push notifications. 
The system integrates with an MQTT broker, SQLite for data storage, and Matplotlib for dynamic graphing. 

To run the project, please download the folder and run the file DHT_Dock.py, which is the main GUI.

The GUI consists of four different windows:
* Broker connection
* DHT application
* Real-time dynamic graph of temperature and humidity
* Alarms screen

![image](https://github.com/user-attachments/assets/8928d08b-bd6d-46e0-ba4f-46928d40e8f2)


The DHT window displays real-time temperature and humidity data from a sensor. When the temperature drops below 18°C, the button turns red, and a request is sent to turn on the air conditioner. Once the air conditioner is on, a 5-second timer is triggered, increasing the room temperature. If humidity exceeds 85%, the humidity button turns red, and a 5-second timer activates to reduce humidity. Additionally, a knob allows you to control the air conditioner's intensity (0-100), sending messages to the hardware through the broker. The relay button controls the air conditioner's use by pausing it. When the relay is engaged, the air conditioner cannot be turned on, even if the temperature drops below 18°C, and the button remains gray.

The data changes are visible in the graph with separate temperature and humidity scales. 

Alerts for sensor activation can be viewed in both the terminal and the notifications window.

After running the application, a file named sensor_data.db is created, containing all the data from the sensor. 
You can view the messages and information that pass through both the terminal and the notifications screen in the GUI.







