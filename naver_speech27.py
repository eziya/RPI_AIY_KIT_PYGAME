# -*- coding: utf-8 -*-
import os
import sys
import urllib
import urllib2
import time
from pygame import mixer


reload(sys)
sys.setdefaultencoding('utf-8')
client_id = "" # 애플리케이션 클라이언트 아이디값"
client_secret = "" # 애플리케이션 클라이언트 시크릿값"
text = unicode("Clova Speech Synthesis API(이하 CSS API)는 음성으로 변환할 텍스트를 입력받은 후 "
               "파라미터로 지정된 음색과 속도로 음성을 합성하여 그 결과를 반환합니다.")
speaker = "mijin" # 음성 합성에 사용할 목소리 종류
speed = "0" # 음성 재생 속도
val = {
    "speaker": speaker,
    "speed":speed,
    "text":text
}
data = urllib.urlencode(val)
url = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"
headers = {
    "X-NCP-APIGW-API-KEY-ID" : client_id,
    "X-NCP-APIGW-API-KEY" : client_secret
}
request = urllib2.Request(url, data, headers)
response = urllib2.urlopen(request)
rescode = response.getcode()
if(rescode==200):
    print("TTS mp3 save")
    response_body = response.read()
    with open('temp.mp3', 'wb') as f:
        f.write(response_body)

    mixer.init(frequency=16000)
    mixer.music.load('temp.mp3')
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(1)
else:
    print("Error Code:" + rescode)