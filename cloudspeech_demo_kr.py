#!/usr/bin/env python3

import argparse
import locale
import logging
import subprocess
import os, random, time
import urllib.request

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient


from pygame import mixer
from gtts import gTTS
from google.cloud import texttospeech

playing = False
filename = ''
filepath = ''

def say(text):
    #gtts_say(text)     # gTTS Speech
    #naver_say(text)     # Naver Clova API
    google_say(text)    # Google Text-to-Speech

def play_text(freq):
    global playing

    if (playing):
        old_pos = mixer.music.get_pos()
        mixer.quit()

    mixer.init(frequency=freq)
    mixer.music.load('temp.mp3')
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(1)
    mixer.quit()

    if (playing):
        mixer.init()
        mixer.music.load(filepath)
        mixer.music.play(-1, (old_pos / 1000))

def gtts_say(text):
    gtts = gTTS(text=text, lang='ko')
    gtts.save('temp.mp3')

    play_text(24000)

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
        with open('temp.mp3', 'wb') as f:
            f.write(response_body)

        play_text(16000)
    else:
        print("Error Code:" + rescode)

def google_say(text):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.types.SynthesisInput(text=text)

    voice = texttospeech.types.VoiceSelectionParams(
        language_code='ko-KR',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    with open('temp.mp3', 'wb') as out:
        out.write(response.audio_content)

    play_text(22100)

def get_hints(language_code):
    if language_code.startswith('ko_'):
        return ('불 켜',
                '불 꺼',
                '반짝반짝',
                '동화',
                '멈춰',
                '다시',
                '굿바이')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def main():
    global playing
    global filename
    global filepath

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()

    with Board() as board:
        mixer.pre_init(frequency=44100)
        say('안녕 윤진! 반짝반짝 버튼을 눌러줘')

        while True:
            # wait for the button input
            board.button.wait_for_press()
            board.led.state = Led.BLINK

            # stop music for better recognition
            if  playing == True:
                mixer.music.pause()
                text = client.recognize(language_code=args.language, hint_phrases=hints)
                mixer.music.unpause()
            else:
                text = client.recognize(language_code=args.language, hint_phrases=hints)

            board.led.state = Led.OFF

            if text is None:
                logging.info('You said nothing.')
                say('미안해! 무슨 말인지 잘 모르겠어.')
                continue

            logging.info('You said: "%s"' % text)
            text = text.lower()

            if '불 켜' in text:
                board.led.state = Led.ON
                say('윤진아! 불이 켜졌어')

            elif '불 꺼' in text:
                board.led.state = Led.OFF
                say('윤진아! 불이 꺼졌어')

            elif '반짝반짝' in text:
                board.led.state = Led.BLINK
                say('윤진아! 불이 반짝반짝거려')

            elif '동화' in text:
                say('윤진아! 동화를 들려줄께')
                filename = random.choice(os.listdir('/home/pi/Music'))
                filepath = "/home/pi/Music/{0}".format(filename)

                mixer.init()
                mixer.music.load(filepath)
                mixer.music.play()
                playing = True

            elif '멈춰' in text:
                if playing == True:
                    old_pos = mixer.music.get_pos()
                    mixer.quit()
                    playing = False
                    say('알았어 잠시 기다릴께. 다시 듣고 싶으면 다시라고 말해줘')
                else:
                    say('지금은 재생중이 아니야.')

            elif '다시' in text:
                say('윤진아! 다시 동화를 들려줄께')

                if (filepath != '') and (playing == False):
                    mixer.init()
                    mixer.music.load(filepath)
                    mixer.music.play(-1, (old_pos / 1000))
                    playing = True

            elif '굿바이' in text:
                say('바이바이 윤진! 다음에 또 만나')
                subprocess.call('sudo shutdown now', shell=True)


if __name__ == '__main__':
    main()