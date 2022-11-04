# SongCrawler
Crawl Spotify and Genius for all the songs of your favourite artist!

## :exclamation: Requirements
This program was built using <code>Python 3.10</code>.  
Older versions may work, but are currently not supported.  

You will also need to setup access to the Spotify and Genius APIs. More on that below.

## About
This program is a tool for data scientists and NLP enthusiasts who would like to gather data on music. It gathers two types of data: Spotify audio features and lyrics.

Spotify audio features are metrics about songs which were generated by Spotify and are accessible through their API. As the name implies, the features are audio related and include some interesting measurements, such as *dancability* or *acousticness*. A full list of features the API provides can be found [here](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/).

The lyrics are gathered through the Genius API.

## :robot: Setup
#### 1. Install the Required Dependencies  
    pip install -r requirements.txt
#### 2. Setup YouTube API

__TODO__ Change this to match this repo (One for Spotify and one for genius)

  > :heavy_exclamation_mark: This step is only necessary if you want to source the data yourself:heavy_exclamation_mark:   
  The dataset used to train the model is included under [/data/](/data/). It was collected 23.09.2022.  
    
  The data for this project is gathered through the [YouTube Data API v3](https://developers.google.com/youtube/v3).
  Setting up this API can roughly be divided into the following steps:  
  <ol>  
    <li>Create a Google Developer Account
    <li>Create a new project
    <li>Enable the YouTube Data API v3
    <li>Create credentials
    <li>Make the credentials accessible to your environment 
  </ol>  
    
  For in-depth guidance, please refer to this excellent [HubSpot Article](https://blog.hubspot.com/website/how-to-get-youtube-api-key).   
<br>
  


## How It Works

Explain :)

Here on usage as:
1. CLI
2. Python class

Main use-case is CLI, so elaborate more on that.


## Contribute

I'm happy about any feedback, contribution, etc.


