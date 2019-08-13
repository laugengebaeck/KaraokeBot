# KaraokeBot - Sings Karaoke like a god
![KaraokeBot](https://upload.wikimedia.org/wikipedia/de/thumb/d/d9/Vogue_DV_14_006_Petula_Clark.jpg/240px-Vogue_DV_14_006_Petula_Clark.jpg)

KaraokeBot is a Telegram bot that sings karaoke with you. You will take turns with KaraokeBot writing or saying song lines. The bot can use the Genius API to look up lyrics. Also, KaraokeBot shows you cute pictures of animals and random GIFs from Giphy. 

Message him [@KaraokeGodBot](https://t.me/KaraokeGodBot) when he's running.

KaraokeBot is currently **not running**, but he will in the near future.

## Caution!
At the moment, KaraokeBot can only handle one user at a time. If you're experiencing problems, it's most likely because of this. I will try to fix this. Meanwhile, please write **/home** to KaraokeBot to reset him when he's not working as expected.

## Installing and running KaraokeBot

0. Download and install Python 3 (if you haven't already done that).

1. Download [ffmpeg](https://ffmpeg.org/download.html) and add it's _/bin_ folder to the PATH of your local machine.

2. Install all the libraries from [_requirements.txt_](requirements.txt) using `pip3 install -r requirements.txt`.

3. Get your API keys/tokens for [Genius](https://genius.com/api-clients/new), [Giphy](https://developers.giphy.com/dashboard/?create=true) and [Telegram](https://t.me/BotFather) and put them into the files `api/genius_key.txt`, `api/giphy_key.txt` and `api/TOKEN`, respectively.

4. Start the bot using `python main.py`.

## Extending KaraokeBot
Feel free to put your own GIFs, cute animal pictures or song lyrics in the respective folders of your local copy. If you want to improve KaraokeBot's code, you can use pull requests.

## How KaraokeBot works

TODO

## Thanks!
This bot was developed during the "Sommercamp 2019" at the Hasso Plattner Institute Potsdam. Thanks to all my team mates who helped developing this bot!
