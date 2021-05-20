import random
import time
from paho.mqtt import client as mqtt_client
#####################################################################
import Adafruit_DHT
import RPi.GPIO as GPIO
sensor = Adafruit_DHT.DHT11

GPIO.setmode(GPIO.BCM) 

ON = True
OFF = False

#온습도센서와 연결된 핀 번호
dht11_Pin = 4

#릴레이를 연결한 핀 번호
relay_Pin = 3

GPIO.setup(relay_Pin, GPIO.OUT) 

#####################################################################
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 8      # Number of LED pixels.
#LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
args = parser.parse_args()

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

print ('Press Ctrl-C to quit.')
if not args.clear:
    print('Use "-c" argument to clear LEDs on exit')

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
#####################################################################
broker = '114.71.241.151'
port = 1883
pubtopic = "python/pub"
subtopic_neo = "jb/shilmu/csle/smenco/mdlp/neo"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'inguk'
password = 'ccit2'

# client = mqtt_client.Client()

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)

def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):            
    # print(str(msg.payload.decode("utf-8")))

    if (str(msg.payload.decode("utf-8")) == "on"):
        print("LED on")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(255,255,255))
            strip.show()
    
    if (str(msg.payload.decode("utf-8")) == "off"):
        print("LED off")
        colorWipe(strip, Color(0,0,0), 0)
    
    if (str(msg.payload.decode("utf-8")) == "red1"):
        print("red1 on")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(255,0,0))
            strip.show()
    
    if (str(msg.payload.decode("utf-8")) == "red3"):
        print("red1 on")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(255,0,0))
            strip.show()

    if (str(msg.payload.decode("utf-8")) == "grn1"):
        print("grn1 on")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(0,255,0))
            strip.show()

    if (str(msg.payload.decode("utf-8")) == "blu1"):
        print("blu1 on")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(0,0,255))
            strip.show()

client = connect_mqtt()
client.loop_start()
client.on_subscribe = on_subscribe
client.on_message = on_message

try:
    client.subscribe(subtopic_neo, 0)
    while True :
        
        humidity, temperature = Adafruit_DHT.read_retry(sensor, dht11_Pin)
        if humidity is not None and temperature is not None :
            print("Temperature = {0:0.1f}*C Humidity = {1:0.1f}%".format(temperature, humidity))
        else :
            print('Read error')
        
        # print ('Color wipe animations.')
        # for i in range(LED_COUNT):
        #     strip.setPixelColor(i, Color(255,0,0))
        #     strip.show()
        # time.sleep(1)
        # for i in range(LED_COUNT):
        #     strip.setPixelColor(i, Color(0,255,0))
        #     strip.show()
        # time.sleep(1)
        # for i in range(LED_COUNT):
        #     strip.setPixelColor(i, Color(0,0,255))
        #     strip.show()
        # time.sleep(1)

        if (temperature <= 15):          # 온도가 15이하라면
            if(humidity < 70):           # 습도가 70미만이면
                print("습도 70까지 가습기를 작동합니다.\n")
                GPIO.output(relay_Pin, ON) # 가습기 On[[]]           
            else:
                print("습도가 현재 실내 온도(15도 이하)에서 적당하거나 다습합니다\n")
                GPIO.output(relay_Pin, OFF) # 가습기 Off
        elif (temperature > 15 and temperature <= 21):     # 온도가 15초과 21이하라면
            if(humidity < 60):                              # 습도가 60미만이라면
                print("습도 60까지 가습기를 작동합니다.\n")
                GPIO.output(relay_Pin, ON)  # 가습기 On
            else:
                print("습도가 현재 실내 온도(16~21도)에서 적당하거나 다습합니다.\n")
                GPIO.output(relay_Pin, OFF) # 가습기 Off
        elif (temperature > 21 and temperature <= 23):
            if(humidity < 50):
                print("습도 50까지 가습기를 작동합니다.\n")
                GPIO.output(relay_Pin, ON)  # 가습기 On
            else:
                print("습도가 현재 실내 온도(22~23도)에서 적당하거나 다습합니다.\n")
                GPIO.output(relay_Pin, OFF) # 가습기 Off
        elif (temperature >= 24):
            if(humidity < 40):
                print("습도 40까지 가습기를 작동합니다.\n")
                GPIO.output(relay_Pin, ON)  # 가습기 On
            else:
                print("습도가 현재 실내 온도(24도 이상)에서 적당하거나 다습합니다.\n")
                GPIO.output(relay_Pin, OFF) # 가습기 Off
    
        time.sleep(1)
except KeyboardInterrupt: # Ctrl + C 누르면 프로그램을 종료한다.
    GPIO.cleanup() #핀 설정들을 모두 '청소'(clean up)해주는 기능
    # if args.clear:
    colorWipe(strip, Color(0,0,0), 10)
    print("Terminated by Keyboard")  
 
finally:
    print("End of Program")
# client.loop_stop()
# client.disconnect()





# def publish(client):
#     msg_count = 0
#     while True:
#         time.sleep(1)
#         msg = f"messages: {msg_count}"
#         result = client.publish(topic, msg)
#         # result: [0, 1]
#         status = result[0]
#         if status == 0:
#             print(f"Send `{msg}` to topic `{topic}`")
#         else:
#             print(f"Failed to send message to topic {topic}")
#         msg_count += 1

# def subscribe(client: mqtt_client):
#     def on_message(client, userdata, msg):
#         print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

#     client.subscribe(topic1)
#     client.on_message = on_message


# def run():
#     client = connect_mqtt()
#     client.loop_start()
#     publish(client)
#     subscribe(client)
#     client.loop_forever()


# if __name__ == '__main__':
#     run()
