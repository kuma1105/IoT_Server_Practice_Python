# 15℃에서는 70%, 18~20℃에서는 60%, 21~23℃에서는 50%, 24℃이상일 때는 40%가 적당한 습도이다.
# 15 이하 습도 70%까지, 16~21에서 습도 60%, 22~23에서 습도 50%, 24이상 습도 40%까지
import random
import time
import paho.mqtt.client as mqtt
import json

# GPIO 공부

def on_connect(client, userdata, flags, rc):
    # 연결이 성공적으로 된다면 완료 메세지 출력
    if rc == 0:
        print("completely connected")
    else:
        print("Bad connection Returned code=", rc)

# 연결이 끊기면 출력
def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)


# 새로운 클라이언트 생성
client = mqtt.Client()

# 내가 함수를 호출하는 것이 아니라 다른 함수에서 호출하는 것: 콜백함수(callback)
# 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_publish(메세지 발행)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# 로컬 아닌, 원격 mqtt broker에 연결
# address : broker.hivemq.com
# port: 1883 에 연결
client.connect('broker.hivemq.com', 1883)
# client.connect('192.168.0.26', 1883) # 라즈베리파이 mosquitto
# client.connect('192.168.111.100', 1883)

client.loop_start()

while(1):
    temperature = random.randrange(13, 37)
    humidity = random.randrange(30, 80)
    print("%d℃" % (temperature))  # 온도값 출력
    print(humidity, "%")           # 습도값 출력

    if (temperature <= 15):          # 온도가 15이하라면
        if(humidity < 70):           # 습도가 70미만이면
            print("습도 70까지 가습기를 작동합니다.\n")
            client.publish('mdhdr', "On", 1) # 가습기 On
        else:
            print("습도가 현재 실내 온도(15도 이하)에서 적당하거나 다습합니다\n")
            client.publish('mdhdr', "Off", 1) # 가습기 Off
    elif (temperature > 15 and temperature <= 21):      # 온도가 15초과 21이하라면
        if(humidity < 60):                              # 습도가 60미만이라면
            print("습도 60까지 가습기를 작동합니다.\n")
            client.publish('mdhdr', "On", 1)  # 가습기 On
        else:
            print("습도가 현재 실내 온도(16~21도)에서 적당하거나 다습합니다.\n")
            client.publish('mdhdr', "Off", 1) # 가습기 Off
    elif (temperature > 21 and temperature <= 23):
        if(humidity < 50):
            print("습도 50까지 가습기를 작동합니다.\n")
            client.publish('mdhdr', "On", 1)  # 가습기 On
        else:
            print("습도가 현재 실내 온도(22~23도)에서 적당하거나 다습합니다.\n")
            client.publish('mdhdr', "Off", 1) # 가습기 Off
    elif (temperature >= 24):
        if(humidity < 40):
            print("습도 40까지 가습기를 작동합니다.\n")
            client.publish('mdhdr', "On", 1)  # 가습기 On
        else:
            print("습도가 현재 실내 온도(24도 이상)에서 적당하거나 다습합니다.\n")
            client.publish('mdhdr', "Off", 1) # 가습기 Off
    time.sleep(4)

    # 웹페이지에서 버튼을 눌러 LED 색깔, 밝기를 제어하기
    # 웹페이지에 온습도값 보내기

client.loop_stop()

# 연결 종료
client.disconnect()