# -*- coding: utf-8 -*-
import os
import sys
import time
import urllib.request
from pygame import mixer

def naver_say(text):
    
    client_id = ""
    client_secret = ""
    encText = urllib.parse.quote(text)
    data = "speaker=mijin&speed=0&text=" + encText
    url = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"      
    
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)    
    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        with open('naver.mp3', 'wb') as f:
            f.write(response_body)

        mixer.init(frequency=16000)
        mixer.music.load('naver.mp3')
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(1)
        mixer.quit()
    else:
        print("Error Code:" + rescode)


def main():
    naver_say('안녕하세요. 저는 네이버 Clova 입니다.')

if __name__ == '__main__':
    main()