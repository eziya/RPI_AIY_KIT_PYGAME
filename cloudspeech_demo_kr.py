#!/usr/bin/env python3

import argparse
import locale
import logging
import subprocess
import os, random, time

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
from aiy.voice import tts

from pygame import mixer
from gtts import gTTS


def gtts_say(text):
    gtts = gTTS(text=text, lang='ko')
    gtts.save('temp.mp3')
    mixer.music.load('temp.mp3')
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(1)

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
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()

    with Board() as board:
        # initialize mixer
        mixer.init()
        #tts.say('Hello lovely pumpkin! press the button and say something.')
        gtts_say('안녕 윤진! 반짝반짝 버튼을 눌러줘')

        while True:

            # wait for the button input
            board.button.wait_for_press()

            board.led.state = Led.BLINK

            # stop music for better recognition
            if mixer.music.get_busy() == True:
                mixer.music.pause()
                text = client.recognize(language_code=args.language, hint_phrases=hints)
                mixer.music.unpause()
            else:
                text = client.recognize(language_code=args.language, hint_phrases=hints)

            board.led.state = Led.OFF

            if text is None:
                logging.info('You said nothing.')
                continue

            logging.info('You said: "%s"' % text)
            text = text.lower()

            if '불 켜' in text:
                board.led.state = Led.ON
                #tts.say('lovely pumpkin! light is on')
                gtts_say('윤진아! 불이 켜졌어')

            elif '불 꺼' in text:
                board.led.state = Led.OFF
                #tts.say('lovely pumpkin! light is off')
                gtts_say('윤진아! 불이 꺼졌어')

            elif '반짝반짝' in text:
                board.led.state = Led.BLINK
                #tts.say('lovely pumpkin! light is blinking')
                gtts_say('윤진아! 불이 반짝반짝거려')

            elif '동화' in text:
                #tts.say('lovely pumpkin! I will tell you a story')
                gtts_say('윤진아! 동화를 들려줄께')
                filename = random.choice(os.listdir('/home/pi/Music'))
                filepath = "/home/pi/Music/{0}".format(filename)
                mixer.music.load(filepath)
                mixer.music.play()

            elif '멈춰' in text:
                mixer.music.pause()
                old_pos = mixer.music.get_pos()
                #tts.say('Okay I can wait for a while. Please say DA-SI if you want to listen again')
                gtts_say('알았어 잠시 기다릴께. 다시 듣고 싶으면 다시라고 말해줘')

            elif '다시' in text:
                #tts.say('lovely pumpkin! I will tell you a story again')
                gtts_say('윤진아! 다시 동화를 들려줄께')
                mixer.music.load(filepath)
                mixer.music.set_pos(old_pos)
                mixer.music.play()

            elif '굿바이' in text:
                #tts.say('lovely pumpkin! see you again')
                gtts_say('바이바이 윤진! 다음에 또 만나')
                subprocess.call('sudo shutdown now', shell=True)

if __name__ == '__main__':
    main()