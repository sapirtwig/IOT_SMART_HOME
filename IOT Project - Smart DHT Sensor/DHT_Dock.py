import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QCheckBox, QDockWidget, QSpinBox, QLabel, QComboBox, QAction, QListWidget
)
from PyQt5.QtGui import QIcon, QFont, QDoubleValidator, QIntValidator
from PyQt5.QtCore import Qt, QTimer, QDateTime
import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mqtt_init import *
from DataManager import *

# Create unique MQTT client
global clientname
r = random.randrange(1, 100000)
clientname = "IOT_client-Id-" + str(r)
DHT_topic = 'pr/home/5976397/sts'
control_topic = 'pr/home/5976397/control'  # A/C control
knob_topic = 'pr/home/5976397/knob'  # A/C power
update_rate = 2000  # Update every two sec

# Class for MQTT connection
class Mqtt_client():
    def __init__(self):
        self.broker = ''
        self.topic = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''
        self.client = None

    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def get_broker(self):
        return self.broker

    def set_broker(self, value):
        self.broker = value

    def get_port(self):
        return self.port

    def set_port(self, value):
        self.port = value

    def get_clientName(self):
        return self.clientName

    def set_clientName(self, value):
        self.clientName = value

    def get_username(self):
        return self.username

    def set_username(self, value):
        self.username = value

    def get_password(self):
        return self.password

    def set_password(self, value):
        self.password = value

    def get_subscribeTopic(self):
        return self.subscribeTopic

    def set_subscribeTopic(self, value):
        self.subscribeTopic = value

    def get_publishTopic(self):
        return self.publishTopic

    def set_publishTopic(self, value):
        self.publishTopic = value

    def get_publishMessage(self):
        return self.publishMessage

    def set_publishMessage(self, value):
        self.publishMessage = value

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print("DisConnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)
        mainwin.dhtDock.update_mess_win(m_decode)

    def connect_to(self):
        self.client = mqtt.Client(self.clientname, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)

    def disconnect_from(self):
        self.client.disconnect()

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        self.client.subscribe(topic)

    def publish_to(self, topic, message):
        self.client.publish(topic, message)
        print(f"Published to {topic}: {message}")

class ConnectionDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eClientID = QLineEdit()
        global clientname
        self.eClientID.setText(clientname)

        self.eUserName = QLineEdit()
        self.eUserName.setText(username)

        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL = QCheckBox()

        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectbtn = QPushButton("Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: red")

        formLayot = QFormLayout()
        formLayot.addRow("Host", self.eHostInput)
        formLayot.addRow("Port", self.ePort)
        formLayot.addRow("Client ID", self.eClientID)
        formLayot.addRow("User Name", self.eUserName)
        formLayot.addRow("Password", self.ePassword)
        formLayot.addRow("Keep Alive", self.eKeepAlive)
        formLayot.addRow("SSL", self.eSSL)
        formLayot.addRow("Clean Session", self.eCleanSession)
        formLayot.addRow("", self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        self.mc.connect_to()
        self.mc.start_listening()

# Class for DHT window
class DHTDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        self.mc = mc

        self.eTemperature = QLineEdit()
        self.eTemperature.setText('0')

        self.eHumidity = QLineEdit()
        self.eHumidity.setText('0')

        self.eKnob = QSpinBox()
        self.eKnob.setRange(0, 100)
        self.eKnob.setValue(50)
        self.eKnob.valueChanged.connect(self.on_knob_change)

        self.eRelay = QCheckBox("Relay (A/C)")
        self.eRelay.stateChanged.connect(self.on_relay_change)

        self.eHeaterButton = QPushButton("Turn On A/C")
        self.eHeaterButton.setStyleSheet("background-color: gray")
        self.eHeaterButton.clicked.connect(self.turn_on_heater)

        self.eHumidityControlButton = QPushButton("Control Humidity")
        self.eHumidityControlButton.setStyleSheet("background-color: gray")
        self.eHumidityControlButton.clicked.connect(self.control_humidity)

        self.heater_timer = QTimer(self)
        self.heater_timer.timeout.connect(self.stop_heater)
        self.heater_active = False

        self.humidity_timer = QTimer(self)
        self.humidity_timer.timeout.connect(self.stop_humidity_control)
        self.humidity_active = False

        self.temp_backup = None
        self.hum_backup = None

        self.heater_timer = QTimer(self)
        self.heater_timer.timeout.connect(self.stop_heater)  # Ensure this is connected
        self.heater_active = False
        
        self.humidity_timer = QTimer(self)
        self.humidity_timer.timeout.connect(self.stop_humidity_control)  # Ensure this is connected
        self.humidity_active = False

        formLayot = QFormLayout()
        formLayot.addRow("Temperature", self.eTemperature)
        formLayot.addRow("Humidity", self.eHumidity)
        formLayot.addRow("Knob (A/C Control)", self.eKnob)
        formLayot.addRow("Relay", self.eRelay)
        formLayot.addRow("", self.eHeaterButton)
        formLayot.addRow("", self.eHumidityControlButton)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setWidget(widget)
        self.setWindowTitle("DHT Data")

    def update_mess_win(self, text):
        self.eTemperature.setText(text.split()[1])
        self.eHumidity.setText(text.split()[3])

    def on_knob_change(self, value):
        self.mc.publish_to("pr/home/5976397/knob", str(value))
        print(f"Knob value changed to: {value}")

    def on_relay_change(self, state):
        if state == Qt.Checked:
            self.mc.publish_to("pr/home/5976397/control", "ON")
            print("Relay is ON")
            self.eHeaterButton.setEnabled(False)  # השבתת כפתור המזגן
            self.eHeaterButton.setStyleSheet("background-color: gray")
        else:
            self.mc.publish_to("pr/home/5976397/control", "OFF")
            print("Relay is OFF")
            self.eHeaterButton.setEnabled(True)  # הפעלת כפתור המזגן מחדש

    def turn_on_heater(self):
        if not self.eRelay.isChecked() and not self.heater_active:  # Check that the Relay is not active
            self.heater_active = True
            self.eHeaterButton.setStyleSheet("background-color: green")
            self.temp_backup = self.eTemperature.text()  # Save the original temperature value
            new_temp = round(float(self.eTemperature.text()) + 5, 2)  # Increase temperature by 5
            self.eTemperature.setText(str(new_temp))
            if not self.heater_timer.isActive():  # Ensure the timer is not already running
                self.heater_timer.start(5000)  # Start the timer for 5 seconds
            print("A/C turned on for 5 seconds")
            
    def stop_heater(self):
        self.heater_active = False
        self.eHeaterButton.setStyleSheet("background-color: gray")
        if self.temp_backup:
            self.eTemperature.setText(self.temp_backup)  # Restore the original temperature value
        self.heater_timer.stop()
        print("A/C turned off")
        
    def control_humidity(self):
        if not self.humidity_active:
            self.humidity_active = True
            self.eHumidityControlButton.setStyleSheet("background-color: green")
            self.hum_backup = self.eHumidity.text()  # Save the original humidity value
            new_hum = round(float(self.eHumidity.text()) - 10, 2)  # Decrease humidity by 10%
            self.eHumidity.setText(str(new_hum))
            if not self.humidity_timer.isActive():  # Ensure the timer is not already running
                self.humidity_timer.start(5000)  # Start the timer for 5 seconds
            print("Humidity control activated for 5 seconds")

    def stop_humidity_control(self):
        self.humidity_active = False
        self.eHumidityControlButton.setStyleSheet("background-color: gray")
        if self.hum_backup:
            self.eHumidity.setText(self.hum_backup)  # Restore the original humidity value
        self.humidity_timer.stop()
        print("Humidity control deactivated")  


# Class for graph window
class GraphDock(QDockWidget):
    def __init__(self):
        QDockWidget.__init__(self)

        self.figure = plt.figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax2 = self.ax.twinx()

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setWindowTitle("Graph")

    def update_graph(self, time_data, temp_data, hum_data):
        self.ax.clear()
        self.ax2.clear()

        self.ax.plot(time_data, temp_data, label='Temperature (°C)', color='red')
        self.ax.set_ylabel('Temperature (°C)', color='red')
        self.ax.tick_params(axis='y', labelcolor='red')
        self.ax.set_ylim(10, 40)

        self.ax2.plot(time_data, hum_data, label='Humidity (%)', color='blue')
        self.ax2.set_ylabel('Humidity (%)', color='blue')
        self.ax2.tick_params(axis='y', labelcolor='blue')
        self.ax2.set_ylim(30, 100)
        self.ax2.yaxis.set_label_position('right')

        self.ax.set_xticks(range(len(time_data)))
        self.ax.set_xticklabels(time_data, rotation=0)

        if len(time_data) > 6:
            self.ax.set_xlim(len(time_data) - 6, len(time_data) - 1)

        self.ax.legend(loc='upper left')
        self.ax2.legend(loc='upper right')

        self.canvas.draw()

# Class for alarms window
class AlarmWindow(QDockWidget):
    def __init__(self):
        QDockWidget.__init__(self)
        self.setWindowTitle("Alarms")
        self.alarm_list = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.alarm_list)
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setWidget(widget)

    def add_alarm(self, message):
        self.alarm_list.addItem(message)

# Main GUI class
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.mc = Mqtt_client()
        self.data_manager = DataManager()
        self.alarm_window = AlarmWindow()

        self.setGeometry(30, 100, 800, 600)
        self.setWindowTitle('Monitor GUI')

        self.connectionDock = ConnectionDock(self.mc)
        self.dhtDock = DHTDock(self.mc)
        self.graphDock = GraphDock()

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dhtDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.graphDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.alarm_window)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate)

        self.temp_data = []
        self.hum_data = []
        self.time_data = []

        if self.mc.client is not None:
            self.mc.subscribe_to(DHT_topic)
            self.mc.subscribe_to(control_topic)
            self.mc.subscribe_to(knob_topic)
        else:
            print("MQTT client is not connected.")

    def update_data(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        temp = round(random.uniform(15, 30), 2)
        hum = round(random.uniform(30, 100), 2)
        
        self.data_manager.save_data(temp, hum)
        alarm_message = self.data_manager.check_alarms(temp, hum)
        self.alarm_window.add_alarm(alarm_message)
        
        self.temp_data.append(temp)
        self.hum_data.append(hum)
        self.time_data.append(current_time)
        
        if len(self.temp_data) > 10:
            self.temp_data.pop(0)
            self.hum_data.pop(0)
            self.time_data.pop(0)
            
        self.dhtDock.eTemperature.setText(str(temp))
        self.dhtDock.eHumidity.setText(str(hum))
        self.graphDock.update_graph(self.time_data, self.temp_data, self.hum_data)
        
         # Check if the relay is off before changing the button color
        if temp < 18 and not self.dhtDock.eRelay.isChecked():
            self.dhtDock.eHeaterButton.setStyleSheet("background-color: red")
        else:
            self.dhtDock.eHeaterButton.setStyleSheet("background-color: gray")
            
        if hum > 85:
            self.dhtDock.eHumidityControlButton.setStyleSheet("background-color: red")
        else:
            self.dhtDock.eHumidityControlButton.setStyleSheet("background-color: gray")

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()