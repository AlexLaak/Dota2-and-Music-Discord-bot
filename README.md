# Discord Dota2 / Music player bot

Search other player profiles, display your own or someone elses profile, check TI8 prize pool, check if you have played before against same people in the last match

Play short music clips preadded or add your own, play straight from youtube with either youtube link or just search for it with the bot, or just play radio.

For full command list use !commands


Pre req: Python v3.4.5 or higher

Windows (using git bash):
```
Dependencies:

download ffmpeg from https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20180708-3a2d21b-win64-static.zip
move ffmpeg.exe to Dota2-and-Music-Discord-bot/python              #located in /bin folder inside zip
cd python
py -3 -m pip install discord
py -3 -m pip install beautifulsoup4
py -3 -m pip install PyNaCl
py -3 -m pip install youtube-dl
    
Running on bash:
cd Dota2-and-Music-Discord-bot/python
python Discord.py
```

Ubuntu:
```
cd Dota2-and-Music-Discord-bot
sudo chmod +x setup.sh
Use 'setup.sh' to setup bot environment.
./setup.sh
```

Unix:
```
1. Clone repo `git clone https://github.com/AlexLaak/Dota2-and-Music-Discord-bot.git`
2. Install python-pip3 if not already installed. `sudo apt install python3-pip`
3. Install dependencies:
	sudo apt-get ffmpeg
	pip3 install discord.py
	pip3 install beautifulsoup4
	pip3 install PyNaCl
	pip3 install youtube-dl
4. Insert your discord bot token into last row in Discord.py
5. cd python && python3 Discord.py
```	

