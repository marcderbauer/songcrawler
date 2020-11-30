import glob
import json
import os
import re
import string
from collections import Counter

from scrape import Song

import pandas as pd
from nltk import ngrams
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from textblob import TextBlob


def tf_idf(artist_dir):
    # TODO
    pass

def document_frequency(word_list): # Freqlist
    word_counts = [word_list.count(p) for p in word_list]
    helper_dict = dict(list(zip(word_list,word_counts)))
    freqdict = {k: v for k, v in sorted(helper_dict.items(), key=lambda item: item[1], reverse= True)}
    return freqdict

def lemmatize(word_list):
    """
    Takes a list of words and lemmatizes them.
    Returns a list.
    """
    return [WordNetLemmatizer().lemmatize(word) for word in word_list]

def tokenize(text, remove_stopwords=True):
    """
    Tokenize string and return a list of strings (tokens).
    By default removes stopwords, but it has an option to leave them in.
    """
    if remove_stopwords == True:
        stop_words = set(stopwords.words('english'))
        return [word for word in word_tokenize(text)if not word in stop_words]
    else:
        return [word for word in word_tokenize(text)]

def normalize(text):
    """
    Normalizes a string for easier processing.
    Removes annotations, converts to lowercase, removes punctuation and newlines.
    Returns a string.
    """
     # Remove verse / artist annotations
    try:
        text = re.sub(r'\[.*\]', '', text)
    except:
        print: "Song has no lyrics"
        return
    

    text = text.lower() # Lowercase
    text = text.translate(str.maketrans('', '', string.punctuation)) # Remove punctuation
    text = ' '.join([line.strip() for line in text.strip().splitlines() if line.strip()]) # Remove Newlines
    
    return text

def get_top_ngrams(text, n = 2, top = 5):
    """
    Takes a string and returns a list of the most common n-grams.
    n determines the length of the n-grams.
    top determines how many should get returned
    """

    help_grams = ngrams(text.split(), n)
    ngram_counts = Counter(help_grams)
    return ngram_counts.most_common(top)

def song_statistics(song, lyrics):
    # TODO: Figure out what to do with token extra info? Save to new file?
    word_info_song = {}
    # Normalize Lyrics
    normalized_lyrics = normalize(lyrics)
    tokens = tokenize(normalized_lyrics)
    lemmas = lemmatize(tokens)
    
    token_frequency = document_frequency(tokens)
    lemma_frequency = document_frequency(lemmas)

    # Statistics
    song.word_count              = len(lyrics.split(" "))
    song.unique_word_count       = len(lemma_frequency)
    song.lyricality              = song.unique_word_count / song.word_count
    song.line_count              = len(lyrics.split('\n'))
    song.char_count              = len(lyrics)
    song.avg_wordlength          = song.char_count / song.word_count

    # Sentiment Analysis using Textblob
    song.sentiment_polarity      = TextBlob(lyrics).sentiment.polarity
    song.sentiment_subjectivity  = TextBlob(lyrics).sentiment.subjectivity

    # Add to word_song_info
    word_info_song["token_frequency"] = token_frequency
    word_info_song["lemma_frequency"] = lemma_frequency
    word_info_song["top_bigrams"]     = get_top_ngrams(lyrics, n = 2, top = 10) # bigrams 
    word_info_song["top_trigrams"]    = get_top_ngrams(lyrics, n = 3, top = 10) # trigrams


    return song, word_info_song

def object_decoder(obj):
    # Decode JSON Object // object_hook for json.loads
    if '__type__' in obj and obj['__type__'] == 'song':
        song = Song(obj["_name"], obj["_uri"],obj["_artists"])
        song.fill_from_file(obj)
        return song
    return obj

def combine_json_dir_to_csv(album_dir, overwrite=False):

    temp = pd.DataFrame()
    file_list = glob.glob(os.path.join(album_dir, "*json"))

    # Iterate through album
    for file_name in file_list:

        with open (file_name, "r", encoding = "utf-8") as json_read:
            json_file = json.load(json_read)
        data = pd.json_normalize(json_file)
        temp = temp.append(data, ignore_index = True)
    
    #temp.drop_duplicates(inplace=True) # Necessary?
    
    # Write to CSV
    album_path = os.path.join(album_dir, os.path.split(album_dir)[1] + ".csv")
    if not os.path.isfile(album_path):
        try:
            with open (album_path, "w") as csv:
                temp.to_csv(csv)
                print(album_dir + " sucessfully written to csv. \n")
        except OSError:
            print("Couldn't write album to csv.")
    else:
        # Check for Overwrite Flag
        if overwrite == False:
            print(album_dir + " already exists. \n Set flag to overwrite... \n")

        else:
            try:
                with open (album_path, "w") as csv:
                    temp.to_csv(csv)
                    print(album_dir + " sucessfully written to csv. \n")
            except OSError:
                print("Couldn't write album to csv.")



def combine_csvs(input_dir, overwrite=False):
    try:
        # TODO: Implement overwrite
        write_path = os.path.join(input_dir, os.path.split(input_dir)[1]) +  ".csv"

        file_list = glob.glob(os.path.join(input_dir,"**","*csv"), recursive=True)
        if write_path in file_list:
            file_list.remove(write_path)

        #combine all files in the list
        combined_csv = pd.concat([pd.read_csv(f) for f in file_list ]).drop_duplicates()

        #export to csv
        combined_csv.to_csv(write_path, index=False, encoding='utf-8')
        print("Succesfully combined CSVs.")
    except:
        print("Error while trying to combine CSVs.")
    

if __name__ == "__main__":
    """

    input_artist_path = "songcrawler/data/Kid_Cudi"

    # Iterate through albums
    for album in os.listdir(input_artist_path):
    
        album_dir = os.path.join(input_artist_path, album)
        if not os.path.isdir(album_dir):
            continue
        print("\n\nALBUM: " + album)
        
        # iterate through songs
        for song in os.listdir(album_dir):
            if os.path.splitext(song)[1] == ".json": 
                song_path = os.path.join(album_dir, song)

                # Process Song
                with open (song_path, "r") as song_json: # No need to open twice

                    # Load Song
                    # TODO: Is it actually type dict???
                    song = json.load(song_json ,object_hook=object_decoder)
                    # Get Song Statistics
                    song = song_statistics(song) #return anything?

                # Write to file
                song.to_json(song_path)

                print("SONG: " + song.name)
        
        combine_json_dir_to_csv(album_dir, overwrite=True)

    combine_csvs(input_artist_path)
    """