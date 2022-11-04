# Calculate the TF-IDF for a given artist dir
# Partial Credit for TF_IDF implementation:
# https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76

import glob
import os
import json
import math

from scrape import Song
from process import object_decoder

def computeTF(wordDict, bagOfWords):
    # computes term frequency for a given document
    # Returns a dictionary {"word": term_frequency,...}
    tfDict = {}
    bagOfWordsCount = len(bagOfWords)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict

def computeIDF(documents):
    N = len(documents)

    # Get a set of all unique words
    allwords = all_keys(documents)
    
    # Convert set to a dictionary with values 0
    idfDict = dict.fromkeys(allwords, 0)

    for document in documents.values(): # For every Song
        for word, values in document.items(): # For every song and Term Freq
            if values > 0:
                idfDict[word] += 1
    
    for word, val in idfDict.items():
        idfDict[word] = math.log(N / float(val))
    return idfDict

def computeTFIDF(tfBagOfWords, idfs):
    tfidf = {}
    for word, val in tfBagOfWords.items():
        tfidf[word] = val * idfs[word]
    return tfidf

def all_keys(dictlist):
    # Takes a dictionary of dictionaries
    # Returns all the keys of the inner dicts
    unique_keys = set()
    for value in dictlist.values():
        words = [*value]
        unique_keys.update(words)
    return unique_keys

def get_tf_idf(artist_path):
    """
    Calculates the tf_idf on an artist basis, by taking all json documents in the folders & subfolders
    Takes the artists path as input
    Writes directly to the input files
    """

    # Grab song_paths
    all_songs = glob.glob(os.path.join(artist_path,"**","*json"), recursive=True)

    term_frequency_dicts = {} # song_path to term_frequency

    # Compute term frequency for all songs
    for song_path in all_songs:
        with open (song_path, "r", encoding = "utf-8") as json_read:

            # Load Song
            song = json.load(json_read, object_hook=object_decoder)

            # Calculate term frequency dict for song
            song_term_frequency = computeTF(song.lemma_frequency, song.lemmas)

            # Append term frequency dictionary to all dictionaries
            term_frequency_dicts[song_path] = song_term_frequency
            
    
    # Compute document frequency
    inverse_document_frequencies = computeIDF(term_frequency_dicts)

    # Compute TF_IDF for all Documents
    tf_idfs_all = {}
    for document_name, document in term_frequency_dicts.items():
        tf_idfs_all[document_name]=(computeTFIDF(document, inverse_document_frequencies))


    # Save tf_idfs to file
    for song_path, tf_idfs in tf_idfs_all.items():
        with open (song_path, "r+", encoding = "utf-8") as json_file:
        
            # Load Song
            song = json.load(json_file, object_hook=object_decoder)

            # Append tf_idfs
            song.tf_idfs = tf_idfs

        # Write Song to File
        song.to_json(song_path)

if __name__ == "__main__":
    artist_path = "songcrawler/data/Moses_Sumney"
    get_tf_idf(artist_path)
