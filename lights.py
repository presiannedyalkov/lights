import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import config

# Functions
def lights_on():
        GPIO.output(RELAIS_1_GPIO, GPIO.LOW)
        mqttClient.publish("home/lights/entrance/state", "ON") # Publish message to MQTT broker
        print("ON")

def lights_off():
        GPIO.output(RELAIS_1_GPIO, GPIO.HIGH)
        mqttClient.publish("home/lights/entrance/state", "OFF") # Publish message to MQTT broker
        print("OFF")

# Our "on message" event
def messageFunction (client, userdata, message):
        topic = str(message.topic)
        message = str(message.payload.decode("utf-8"))
        print(topic + ": " + message)
        
        isSetTopic = topic == "home/lights/entrance/set" or topic == "home/lights/set"

        global switch_state
        
        if isSetTopic and message == "ON":
                switch_state = 1
        if isSetTopic and message == "OFF":
                switch_state = 0

# Configure GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN1 = 5
#PIR_PIN2 = 4
RELAIS_1_GPIO = 17
timer = 0
relay_state = False
switch_state = 3
MOTION_INTERVAL = 60

GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO output
GPIO.setup(PIR_PIN1, GPIO.IN) # GPIO SENSOR 1 input
#GPIO.setup(PIR_PIN2, GPIO.IN) # GPIO SENSOR 2 input
turn_on = GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # on
turn_off = GPIO.output(RELAIS_1_GPIO, GPIO.HIGH) # off

# Configure MQTT
mqttClient = mqtt.Client("light_entrance") # Create a MQTT client object
mqttClient.username_pw_set(config.username, password=config.password)
mqttClient.connect(config.broker, 1883) # Connect to the Home Assistant
mqttClient.publish("home/lights/entrance/config", '{"name": "light_entrance", "friendly_name": "Entrance Light", "state_topic": "home/lights/entrance/state"}') 
mqttClient.subscribe("home/lights/entrance/set") # Subscribe to the topic lights/entrance
mqttClient.subscribe("home/lights/set") # Subscribe to the topic lights
mqttClient.on_message = messageFunction # Attach the messageFunction to subscription
mqttClient.loop_start() # Start the MQTT client

try:
        print("PIR Module Test (CTRL+C to exit)")
        time.sleep(2)
        print("Ready")

        # Start the loop
        while True:
                time.sleep(0.985)
                # Test PIR_PIN condition
                current_state = GPIO.input(PIR_PIN1) #or GPIO.input(PIR_PIN2)

                if timer > 0:
                        timer -= 1
                        print(timer)

                        # Motion detected
                        if current_state or switch_state == 1:
                                # Reset timer
                                timer = MOTION_INTERVAL
                                # Reset switch
                                switch_state = 3
                                print("Motion Detected! Reset Timer!")

                # Timer is initiated or went to 0
                else:
                        # Motion detected
                        if current_state:
                                if relay_state is False:
                                        print("Lamp is off, turn on!")
                                        relay_state = True
                                        lights_on()

                                # Reset timer
                                timer = MOTION_INTERVAL
                                print("Motion Detected! Reset Timer!")

                        # Timer is 0 and there is no motion
                        else:
                                if relay_state is True:
                                        print("Lamp is on, turn off!")
                                        relay_state = False
                                        lights_off()

                # Switch is set to ON
                if switch_state == 1:
                        timer = MOTION_INTERVAL
                        print("Switch is toggled! Reset Timer!")
                # Switch is set to OFF
                elif switch_state == 0:
                        timer = 0
                        switch_state = 3
                        print("Switch is toggled! Null Timer!")

except KeyboardInterrupt:
        print("Quit")
        GPIO.cleanup()