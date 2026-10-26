'''
audio player
'''

# import library
import os
from subprocess import call

# global variables
os_name = 'windows' if os.name == 'nt' else 'linux'

# play audio
def play_audio(audio_name):
    try:
        if os_name == 'linux':
            call('mpg321 ' + audio_name, shell=True) # use mpg321
        
        elif os_name == 'windows':
            try:
                from playsound import playsound
                playsound(audio_name) # pip install playsound
            except Exception:
                # Windows 下没有 playsound 时退化为系统默认播放器
                os.startfile(audio_name)
        
        else:
            print('Opearating System name is misspelled')
    except KeyboardInterrupt as e:
        print(e)
    finally:
        pass

if __name__ == '__main__':
    play_audio('voices/bibi.mp3')
    
    
    
