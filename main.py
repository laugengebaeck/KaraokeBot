import telegram.ext
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
import os
import random
import time
import urllib.request

from gtts import gTTS
import speech_recognition as sr
import subprocess
import lyricsgenius
from shutil import copy
import wave
from pydub import AudioSegment
import giphypop


global toleration_percentage
toleration_percentage = 0.4

def initVars():
    global NEUTRAL, SINGING, CHOOSEGENIUSARTIST, CHOOSEGENIUSSONG, CHOOSELANGUAGE
    NEUTRAL, SINGING, CHOOSEGENIUSARTIST, CHOOSEGENIUSSONG, CHOOSELANGUAGE = range(5)

    global SONG_STR
    SONG_STR = ""
    global SONG
    SONG = []

    global VERS
    VERS = -1

    global IDs
    IDs = []

    global ARTIST, TITLE
    ARTIST = ''
    TITLE = ''

    global LANG_RESP_CODE
    LANG_RESP_CODE = ''

    
    f_lst = os.listdir("sound_data")
    for f in f_lst:
        os.remove('sound_data/'+f)


def main():

    dispatcher = updater.dispatcher

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

def mistake_toleration(expected, response):
    global toleration_percentage
    expected_arr = expected.split(" ")
    response_arr = response.split(" ")
    counter = 0
    for i in range(len(expected_arr)):
        if i >= len(response_arr):
            break
        if expected_arr[i] != response_arr[i]:
            counter += 1
    percentage = float(counter) / float(len(expected_arr))
    return percentage < toleration_percentage    

def start(bot, update):
    global IDs
    #add ID if new
    if not update.message.chat_id in IDs:
        IDs += [update.message.chat_id]
    return NEUTRAL

def home(bot, update):
    initVars()
    return NEUTRAL

def sing(bot, update):
    update.message.reply_text("Which song would you like to sing?")

    return NEUTRAL

def chooseSong(bot, update):
    global SONG, SONG_STR, VERS
    try:
        with open('songs/'+update.message.text+'.txt') as song_file:
            SONG_STR = song_file.read()
    except:
        with open('songs/song1.txt') as song_file:
            SONG_STR = song_file.read()
    SONG = SONG_STR.split('\n')
    SONG = [x for x in SONG if x]

    update.message.reply_text('Which language would you like to hear?')

    return CHOOSELANGUAGE

def startSinging(bot, update):
    global VERS
    VERS += 1
    sayVers(bot, update, VERS)

def singing(bot, update):
    global SONG, VERS
    #if(VERS+1 == len(SONG)-1):
    #    finishSong(bot, update)
    #    return  NEUTRAL

    response = update.message.text.lower()

    tts = gTTS(response, lang=LANG_RESP_CODE)
    tts.save('sound_data/voice'+str(VERS+1)+'.wav')

    evaluateResponse(bot, update, response)
    return SINGING

def showPic(bot, update):
    bot.send_photo(update.effective_chat.id, open('pics/'+getRandomPic(), 'rb'), caption="That's an animal   .")
    
def singing_voice(bot, update):
    global SONG, VERS
    print('type: ', type(update.message.voice))
    file_id = update.message.voice.file_id
    audioFile = bot.get_file(file_id)
    audioFile.download('voice.ogg')

    os.remove('voice.wav')
    src_filename = 'voice.ogg'
    dest_filename = 'voice.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])

    if process.returncode != 0:
        raise Exception("Couldn't convert sound data")
    
    
    os.remove('voice.mp3')
    src_filename = 'voice.wav'
    dest_filename = 'voice.mp3'

    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])

    if process.returncode != 0:
        raise Exception("Couldn't convert sound data")

    newfilename = 'sound_data/voice'+str(VERS+1)+'.mp3'
    copy('voice.mp3', newfilename)

    # speech to text
    r = sr.Recognizer()

    sound = sr.AudioFile('voice.wav')
    with sound as source:
        audio = r.record(source)
    type(audio)
    response = r.recognize_google(audio, language=LANG_RESP_CODE)
    evaluateResponse(bot, update, response)

def evaluateResponse(bot, update, response):
    global VERS, SONG, NEUTRAL
    response_original = response
    expected = SONG[VERS+1].lower()
    expected_original = expected
    response = response.lower()
    special_chars = ['\'',  '!', '?', '-', '\n', '\"', ','] # '\’',
    for c in special_chars:
        response = response.replace(c, '')
        expected = expected.replace(c, '')
    print('response: ' , response)
    print('expected: ', expected)
    if mistake_toleration(expected, response):
        if expected != response:
            update.message.reply_text("Mostly right!"+'\nresponse: '+response_original+'\nexpected: '+expected_original+'\nLet\'s continue!')
        if(VERS+1 == len(SONG)-1):
            finishSong(bot, update)
            return  NEUTRAL
        else:
            sayVers(bot, update, VERS+2)
            if(VERS+2 == len(SONG)-1):
                finishSong(bot, update)
                return  NEUTRAL
        VERS = VERS + 2
    else:
        gif_file = getRandomGifGiphy("laughing")
        bot.send_animation(update.effective_chat.id, open(os.getcwd()+"/gifs/"+gif_file,'rb'), caption='response: '+response_original+'\nexpected: '+expected_original)
    

def genius(bot, update):
    update.message.reply_text('Artist name?')
    return CHOOSEGENIUSARTIST

def chooseArtist_genius(bot, update):
    global ARTIST
    ARTIST = update.message.text
    update.message.reply_text('Song name?')
    return CHOOSEGENIUSSONG

def chooseSong_genius(bot, update):
    global ARTIST, TITLE, SONG
    TITLE = update.message.text
    update.message.reply_text('searching...')
    key = ''
    with open('api/genius_key.txt') as key_file:
        key = key_file.read()
    genius = lyricsgenius.Genius(key)
    song = genius.search_song(TITLE, ARTIST)
    SONG = editLyrics(song.lyrics)
    
    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)

    file_name = "cover_art." + song.song_art_image_url.split('.')[-1]

    urllib.request.urlretrieve(song.song_art_image_url, file_name)
    
    bot.send_photo(update.effective_chat.id, open(file_name, 'rb'), caption=TITLE)

    update.message.reply_text('Which language would you like to hear?')

    return CHOOSELANGUAGE

def choose_language(bot, update):
    global SINGING, LANG_RESP_CODE
    r = update.message.text.lower()
    if r == 'französisch' or r == 'french' or r == 'fr':
        LANG_RESP_CODE = 'fr-FR'
    elif r == 'japanisch' or r == 'japanese' or r == 'ja':
        LANG_RESP_CODE = 'ja'
    elif r == 'deutsch' or r == 'german' or r == 'de':
        LANG_RESP_CODE = 'de'
    else:
        LANG_RESP_CODE = 'en'
    
    startSinging(bot, update)
    return SINGING

def editLyrics(lyrics):
    lines = lyrics.split('\n')
    lines2 = []
    for l in lines:
        if not l or l.find('[') != -1 or l.find('{') != -1:
            continue
        l = l.replace('(', '')
        l = l.replace(')', '')
        lines2 += [l]
    return lines2

def sayVers(bot, update, index):
    update.message.reply_text(SONG[index])
    tts = gTTS(SONG[index], lang=LANG_RESP_CODE)
    tts.save('vers.mp3')

    os.remove('vers.wav')
    src_filename = 'vers.mp3'
    dest_filename = 'vers.wav'
    
    sound = AudioSegment.from_mp3(src_filename)
    sound.export(dest_filename, format="wav")

    newfilename = 'sound_data/voice'+str(index)+'.mp3'
    copy('vers.mp3', newfilename)

    bot.send_audio(update.effective_chat.id, open('vers.mp3', 'rb'))

def finishSong(bot, update):
    update.message.reply_text('Well done!')
    time.sleep(2)

    bot.send_photo(update.effective_chat.id, open('pics/'+getRandomPic(), 'rb'), caption="That's an animal.")
    send_merged_sound(bot, update)
    initVars()

def send_merged_sound(bot, update):
    path = 'sound_data'
    sounds = []
    f_lst = os.listdir(path)
    for f in f_lst:
        sounds += [AudioSegment.from_mp3(path+'/'+f)]
    combined = sum(sounds)
    
    combined.export(path+'/merged.mp3', format='mp3')

    #speed up
    src_filename = path+'/merged.mp3'
    dest_filename = path+'/merged_fast.mp3'
    process = subprocess.run('ffmpeg -i '+src_filename+' -filter:a \"atempo=2.0\" -vn '+dest_filename)
    
    bot.send_audio(update.effective_chat.id, open(path+'/merged_fast.mp3', 'rb'))

def setToleration(bot, update, args):
    global toleration_percentage
    try:
        perc = int(args[0])
        toleration_percentage = perc/100.0
        update.message.reply_text('Tolerance set successfully to '+ str(perc)+"% !")
    except:
        update.message.reply_text('Only numbers until 100 expected!')
    return NEUTRAL
    
def sound_speed_change(sound, speed=1.0):
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
        })
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def getRandomGif():
    gif_list = []
    f_lst = os.listdir(os.getcwd() + "/gifs")
    for f in f_lst:
        if f.endswith(".gif"):
            gif_list += [f]
    return random.choice(gif_list)

def getRandomGifGiphy(tagtag):
    with open('api/giphy_key.txt') as key_file:
        key = key_file.read().strip()
    g = giphypop.Giphy(api_key=key)
    gif = g.random_gif(tag=tagtag)
    urllib.request.urlretrieve(gif.media_url, os.getcwd() + "/gifs/random.gif")
    return "random.gif"

def getRandomGifGiphyWrapper(bot,update,args):
    gif_file = getRandomGifGiphy(args[0])
    bot.send_animation(update.effective_chat.id, open(os.getcwd()+"/gifs/"+gif_file,'rb'),caption="Here's your gif.")
    return NEUTRAL

def getRandomPic():
    pic_list = []
    f_lst = os.listdir(os.getcwd() + "/pics")
    for f in f_lst:
        if f.endswith(".jpg") or f.endswith('.jpeg') or f.endswith('.png'):
            pic_list += [f]
    return random.choice(pic_list)

# program

initVars()

with open('api/TOKEN') as token_file:
    TOKEN = token_file.read().strip()

conv_handler = ConversationHandler(
    entry_points = [CommandHandler('start', start)],

    states = {
        NEUTRAL: [CommandHandler('genius', genius),
                CommandHandler('sing', sing),
                CommandHandler('pic', showPic),
                CommandHandler('gif',getRandomGifGiphyWrapper,pass_args=True),
                CommandHandler('tolerance', setToleration, pass_args=True),
                MessageHandler(Filters.text, chooseSong)],
        CHOOSEGENIUSARTIST: [MessageHandler(Filters.text, chooseArtist_genius)],
        CHOOSEGENIUSSONG: [MessageHandler(Filters.text, chooseSong_genius)],
        CHOOSELANGUAGE: [MessageHandler(Filters.text, choose_language)],
        SINGING: [CommandHandler('home', home),
                MessageHandler(Filters.text, singing),
                MessageHandler(Filters.voice, singing_voice)]
    },

    fallbacks = []
)

updater = Updater(token=TOKEN)



if __name__ == '__main__':
    main()