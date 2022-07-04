import json, os, re
#import numpy as np
from scrape import find_missing_lyrics

#with open ("songcrawler/errors.txt", "r") as errors_file:
#    errors = errors_file.readlines()

#for error_message in errors.split(","):
#print(error_message)
#print(errors)
find_missing_lyrics()

errors2 =np.genfromtxt(r'songcrawler/errors.json', delimiter=',')