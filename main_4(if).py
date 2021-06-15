#-*- coding:utf-8 -*-
import random
import time
from paho.mqtt import client as mqtt_client

############################################################
# JSON 데이터 사용하기 위해 json 라이브러리를 import
import json

############################################################
import Adafruit_DHT # 온습도센서 라이브러리
import RPi.GPIO as GPIO
sensor = Adafruit_DHT.DHT11

GPIO.setmode(GPIO.BCM)  #GPIO(?)
GPIO.setwarnings(False)

ON = True
OFF = False

#온습도센서와 연결된 핀 번호
dht11_Pin = 20

#릴레이를 연결한 핀 번호
relay_Pin = 4

#릴레이 핀을 OUTPUT으로 설정
GPIO.setup(relay_Pin, GPIO.OUT) 

############################################################
# 네오픽셀을 설정합니다.
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
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

brightness_1 = 10   #네오픽셀 밝기 1단계
brightness_2 = 100  #네오픽셀 밝기 2단계
brightness_3 = 250  #네오픽셀 밝기 3단계

############################################################
broker = '114.71.241.151'
#broker = "broker.emqx.io"
port = 1883
############################################################

#Topic
#파이에서 어플로 온습도 값 보내기
Pi_to_Flutter = "jb/shilmu/csle/smenco/mdlp/dht"

#파이에서 서버로 온습도, 미세먼지 토픽 보내기
Pi_to_Server_dht = "jb/shilmu/scle/smenco/apsr/1/input/dht"
Pi_to_Server_pms = "jb/shilmu/scle/smenco/apsr/1/input/pms"

# 어플에서 파이로 Led 제어하기
Flutter_to_Pi = "jb/shilmu/csle/smenco/mdlp/neo"

#어플에서 파이로 가습기 모듈 제어하기 (자동모드) AutoOn, AutoOFf
Flutter_Pi_Humid_Auto = 'jb/shilmu/csle/smenco/mdlp/humidAuto';

#어플에서 파이로 가습기 모듈 제어하기 (수동모드) HumidOn, HumidOff
Flutter_Pi_Humid = 'jb/shilmu/csle/smenco/mdlp/humid';

# pubtopic_key = "jb/shilmu/csle/smenco/mdlp/key"

# generate client ID with pub prefix randomly
#client_id = f'python-mqtt-{random.randint(0, 1000)}'
client_id = "python-mqtt-1234"
username = 'inguk'
password = 'ccit2'


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

############################################################
# 전역변수 사용을 위해 선언
# 가습기 모드 상태 AutoOn, AutoOFf
humidAutoCtrl = "HumidAutoOn" 

#가습기 상태 HumidOn, HumidOff
humidCtrl = "HumidOn"
############################################################

def on_message(client, userdata, msg):
    if (str(msg.payload.decode("utf-8")) == "HumidAutoOn"):
        print("가습기 제어를 자동모드로 변경합니다.")
        global humidAutoCtrl
        humidAutoCtrl = "HumidAutoOn"

    if (str(msg.payload.decode("utf-8")) == "HumidAutoOff"):
        print("가습기 제어를 수동모드로 변경합니다.")
        humidAutoCtrl = "HumidAutoOff"
    
    if (str(msg.payload.decode("utf-8")) == "HumidOn"):
        print("가습기 켬")
        GPIO.output(relay_Pin, ON) # 가습기 On
    
    if (str(msg.payload.decode("utf-8")) == "HumidOff"):
        print("가습기 끔")
        GPIO.output(relay_Pin, OFF) # 가습기 On

    if (str(msg.payload.decode("utf-8")) == "LedOn"):
        print("LED on")
        GPIO.output(4, GPIO.HIGH)
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(255,255,255))
            strip.show()
        time.sleep(50/1000.0)
    
    if (str(msg.payload.decode("utf-8")) == "LedOff"):
        print("LED off")
        GPIO.output(4, GPIO.LOW)
        colorWipe(strip, Color(0,0,0), 0)
        
    
    if (str(msg.payload.decode("utf-8")) == "ylw1"):
        print("ylw1 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_1)
            strip.setPixelColor(i, Color(255,211,26))
            strip.show()
        time.sleep(50/1000.0)
    
    if (str(msg.payload.decode("utf-8")) == "ylw2"):
        print("ylw2 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_2)
            strip.setPixelColor(i, Color(255,211,26))
            strip.show()
        time.sleep(50/1000.0)
    
    if (str(msg.payload.decode("utf-8")) == "ylw3"):
        print("ylw3 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_3)
            strip.setPixelColor(i, Color(255,211,26))
            strip.show()
        time.sleep(50/1000.0)

    if (str(msg.payload.decode("utf-8")) == "grn1"):
        print("grn1 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_1)
            strip.setPixelColor(i, Color(0,255,0))
            strip.show()
        time.sleep(50/1000.0)

    if (str(msg.payload.decode("utf-8")) == "grn2"):
        print("grn2 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_2)
            strip.setPixelColor(i, Color(0,150,0))
            strip.show()
        time.sleep(50/1000.0)

    if (str(msg.payload.decode("utf-8")) == "grn3"):
        print("grn3 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_3)
            strip.setPixelColor(i, Color(0,30,0))
            strip.show()
        time.sleep(50/1000.0)

    if (str(msg.payload.decode("utf-8")) == "blu1"):
        print("blu1 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_1)
            strip.setPixelColor(i, Color(0,0,255))
            strip.show()
        time.sleep(50/1000.0)

    if (str(msg.payload.decode("utf-8")) == "blu2"):
        print("blu2 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_2)
            strip.setPixelColor(i, Color(0,0,255))
            strip.show()
        time.sleep(50/1000.0)
    
    if (str(msg.payload.decode("utf-8")) == "blu3"):
        print("blu3 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_3)
            strip.setPixelColor(i, Color(0,0,255))
            strip.show()
        time.sleep(50/1000.0)
    
    if (str(msg.payload.decode("utf-8")) == "ppl1"):
        print("ppl1 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_3)
            strip.setPixelColor(i, Color(201, 58, 226))
            strip.show()
        time.sleep(50/1000.0)
    
    if (str(msg.payload.decode("utf-8")) == "ppl2"):
        print("ppl2 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_3)
            strip.setPixelColor(i, Color(201, 58, 226))
            strip.show()
        time.sleep(50/1000.0)
    
    if (str(msg.payload.decode("utf-8")) == "ppl3"):
        print("ppl3 on")
        for i in range(LED_COUNT):
            strip.setBrightness(brightness_3)
            strip.setPixelColor(i, Color(201, 58, 226))
            strip.show()
        time.sleep(50/1000.0)

############################################################
client = connect_mqtt()
client.loop_start()
client.on_subscribe = on_subscribe
client.on_message = on_message
############################################################

# 어플로 보낼 데이터를 만드는 함수
def Json_to_Flutter(tmp, hum, msg):
    DhtData_Flutter = {}
    DhtData_Flutter['tmp'] = tmp
    DhtData_Flutter['hum'] = hum
    DhtData_Flutter['alert'] = msg

    data = json.dumps(DhtData_Flutter)
    
    return data

# 서버로 보낼 JSON데이터를 만드는 함수
def Json_to_Server(tmp, hum):
    DhtData_Server = {}
    DhtData_Server['tmp'] = tmp
    DhtData_Server['hum'] = hum
    DhtData_Server['key'] = "1"

    PmsData_Server = {}
    PmsData_Server['dust'] = 1
    PmsData_Server['key'] = "1"

    data1 = json.dumps(DhtData_Server)
    data2 = json.dumps(PmsData_Server)
    
    return data1, data2

############################################################

try:
    client.subscribe(Flutter_to_Pi, 0)
    client.subscribe(Flutter_Pi_Humid, 0)
    client.subscribe(Flutter_Pi_Humid_Auto, 0)


    #네오픽셀에서 색을 없앰, 빛을 끔
    # colorWipe(strip, Color(0,0,0), 10) 

    while True :
        humidity, temperature = Adafruit_DHT.read_retry(sensor, dht11_Pin)
        if humidity is not None and temperature is not None :
            print("▶Temperature = {0:0.1f}*C Humidity = {1:0.1f}%".format(temperature, humidity))
        else :
            print('Read error')

        if (temperature <= 15):          # 온도가 15이하라면
            if(humidity < 70):           # 습도가 70미만이면
                
                if (humidAutoCtrl == "HumidAutoOff"):
                    print("가습기 모듈 수동 모드\n")
                else:
                    print("가습기 모듈 자동 모드\n(수동으로 제어할 수 없습니다)\n.")
                    print("습도 70까지 가습기를 작동합니다\n")
                    GPIO.output(relay_Pin, ON) # 가습기 On  

                ###############################################
                Json_DhtData_Flutter = Json_to_Flutter(temperature, humidity, '습도 70까지 가습기를 작동합니다')
                Json_DhtData_Server, Json_PmsData_Server = Json_to_Server(temperature, humidity)
                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                ###############################################

                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)

            else:
                
                if (humidAutoCtrl == "HumidAutoOff"):
                    print("가습기 모듈 수동 모드\n")
                else:
                    print("가습기 모듈 자동 모드\n(수동으로 제어할 수 없습니다.)\n")
                    print("습도가 현재 실내 온도(15도 이하)에서\n 적당하거나 다습합니다\n")
                    GPIO.output(relay_Pin, OFF) # 가습기 Off
                
                ###############################################
                Json_DhtData_Flutter = Json_to_Flutter(temperature, humidity, '습도가 현재 실내 온도(15도 이하)에서\n 적당하거나 다습합니다')
                Json_DhtData_Server, Json_PmsData_Server = Json_to_Server(temperature, humidity)
                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                ###############################################

                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)

        elif (temperature > 15 and temperature <= 21):     
            # 온도가 15초과 21이하라면
            if(humidity < 60):                              
                # 습도가 60미만이라면
                
                if (humidAutoCtrl == "HumidAutoOff"):
                    print("가습기 모듈 수동 모드\n")
                else:
                    print("가습기 모듈 자동 모드\n 수동으로 제어할 수 없습니다.\n")
                    print("습도 60까지 가습기를 작동합니다\n")
                    GPIO.output(relay_Pin, ON)  # 가습기 On
                

                ###############################################
                Json_DhtData_Flutter = Json_to_Flutter(temperature, humidity, '습도 60까지 가습기를 작동합니다')
                Json_DhtData_Server, Json_PmsData_Server = Json_to_Server(temperature, humidity)
                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                ###############################################

                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)

            else:
                
                if (humidAutoCtrl == "HumidAutoOff"):
                    print("가습기 모듈 수동 모드\n")
                else:
                    print("가습기 모듈 자동 모드\n 수동으로 제어할 수 없습니다.\n")
                    print("습도가 현재 실내 온도(16~21도)에서\n 적당하거나 다습합니다\n")
                    GPIO.output(relay_Pin, OFF) # 가습기 Off
                

                ###############################################
                Json_DhtData_Flutter = Json_to_Flutter(temperature, humidity, '습도가 현재 실내 온도(16~21도)에서\n 적당하거나 다습합니다')
                Json_DhtData_Server, Json_PmsData_Server = Json_to_Server(temperature, humidity)
                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                ###############################################

                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)

        elif (temperature > 21 and temperature <= 23):
            if(humidity < 50):
                
                if (humidAutoCtrl == "HumidAutoOff"):
                    print("가습기 모듈 수동 모드\n")
                else:
                    print("가습기 모듈 자동 모드\n 수동으로 제어할 수 없습니다.\n")
                    print("습도 50까지 가습기를 작동합니다\n")
                    GPIO.output(relay_Pin, ON)  # 가습기 On
                

                ###############################################
                Json_DhtData_Flutter = Json_to_Flutter(temperature, humidity, '습도 50까지 가습기를 작동합니다')
                Json_DhtData_Server, Json_PmsData_Server = Json_to_Server(temperature, humidity)
                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                ###############################################

                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)

            else:
                
                if (humidAutoCtrl == "HumidAutoOff"):
                    print("가습기 모듈 수동 모드\n")
                else:
                    print("가습기 모듈 자동 모드\n 수동으로 제어할 수 없습니다.\n")
                    print("습도가 현재 실내 온도(22~23도)에서\n 적당하거나 다습합니다\n")
                    GPIO.output(relay_Pin, OFF) # 가습기 Off
                
                ###############################################
                Json_DhtData_Flutter = Json_to_Flutter(temperature, humidity, '습도가 현재 실내 온도(22~23도)에서\n 적당하거나 다습합니다')
                Json_DhtData_Server, Json_PmsData_Server = Json_to_Server(temperature, humidity)
                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                ###############################################

                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)

        elif (temperature >= 24):
            if(humidity < 40):
                
                if (humidAutoCtrl == "HumidAutoOff"):
                    print("가습기 모듈 수동 모드\n")
                else:
                    print("가습기 모듈 자동 모드\n 수동으로 제어할 수 없습니다.\n")
                    print("습도 40까지 가습기를 작동합니다\n")
                    GPIO.output(relay_Pin, ON)  # 가습기 On

                ###############################################
                Json_DhtData_Flutter = Json_to_Flutter(temperature, humidity, '습도 40까지 가습기를 작동합니다')
                Json_DhtData_Server, Json_PmsData_Server = Json_to_Server(temperature, humidity)
                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                ###############################################

                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                
            else:
                
                if (humidAutoCtrl == "HumidAutoOff"):
                    print("가습기 모듈 수동 모드\n")
                else:
                    print("가습기 모듈 자동 모드\n 수동으로 제어할 수 없습니다.\n")
                    print("습도가 현재 실내 온도(24도 이상)에서\n 적당하거나 다습합니다\n")
                    GPIO.output(relay_Pin, OFF) # 가습기 Off

                ###############################################
                Json_DhtData_Flutter = Json_to_Flutter(temperature, humidity, '습도가 현재 실내 온도(24도 이상)에서\n 적당하거나 다습합니다')
                Json_DhtData_Server, Json_PmsData_Server = Json_to_Server(temperature, humidity)
                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
                ###############################################

                client.publish(Pi_to_Flutter, Json_DhtData_Flutter, 0)
                client.publish(Pi_to_Server_dht, Json_DhtData_Server, 0)
                client.publish(Pi_to_Server_pms, Json_PmsData_Server, 0)
    
        time.sleep(5)

except KeyboardInterrupt: # Ctrl + C 누르면 프로그램을 종료한다.
    GPIO.cleanup() #핀 설정들을 모두 '청소'(clean up)해주는 기능
    colorWipe(strip, Color(0,0,0), 10) #네오픽셀에서 색을 없앰, 빛을 끔
    print("Terminated by Keyboard")  
 
finally:
    print("End of Program")
