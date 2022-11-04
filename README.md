# SongCrawler
Crawl Spotify and Genius for all the songs of your favourite artist!


# BACKUP
This branch is mostly for easy access to an old implementation of this project. Most of it is not wanted or required, but who knows, maybe I'll need it...
I am aware that I could just use version history, but this is just convenient.

## About
This repo is fairly old and I wrote this before I had any real idea about how to code. I will be the first to admit that this is horribly written.  

| ❗️This program is not representative of my current coding skills.❗️  

Save for a few manual adjustments, like creating a few folders, the code works pretty well.

Currently, my main motivation is to use this code for a project, not to use it to demonstrate my engineering skills. Therefore I decided to take on the technical debt of this repo being a bit messy.  

[Spotify audio features reference](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)

## How It Works
Explain :)

## Requirements
SongCrawler requires [nltk](https://github.com/nltk/nltk), [lyricgenius](https://github.com/johnwmillr/LyricsGenius) and [spotipy](https://github.com/plamere/spotipy). <br/>
To process the audio_features into csv format <code>pandas</code> is required too.
All requirements can be installed with the following command: <br/>
  ` pip install -r requirements.txt`

NLTK requires three additional libraries:
<code>
nltk.download('stopwords')  
nltk.download('punkt')  
nltk.download('wordnet')
</code>

## Contribute
I'm happy about any feedback, contribution, etc.


