import pprint

import numpy
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from lyricsgenius import Genius, genius
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from scipy.sparse.bsr import bsr_matrix
from scipy.spatial import distance
from scipy.sparse import csr_matrix

import API_Keys
import Lyrics
from modelBuilder import MODEL_LOCATION


# gets the lyrics of a song
def getLyrics(title, artist, genius):
    lyrics = Lyrics.getSongLyrics(title, artist, genius)
    if lyrics is None:
        return None
    doc = tokenizeLyrics(lyrics)
    return(doc)


# clean songs just like the corpus
def tokenizeLyrics(lyrics):
    tokenizer = RegexpTokenizer(r'\w+')
    lemmatizer = WordNetLemmatizer()

    lyrics = Lyrics.removeGeniusTags(lyrics)
    doc = Lyrics.tokenizeSong(lyrics, tokenizer, lemmatizer)
    return(doc)


def toDenseArrays(dist1, dist2):
    mx = max([dist1[-1][0]+1, dist2[-1][0]+1])
    dist1Dense = [0] * mx
    dist2Dense = [0] * mx
    for i in dist1:
        dist1Dense[i[0]] = i[1]
    for i in dist2:
        dist2Dense[i[0]] = i[1]
    return(dist1Dense, dist2Dense)


# computes the jensen-shannon divergence of 2 song
def getSongDivergence(model, docs):
    dictionary = Dictionary(docs)
    newSongs = [dictionary.doc2bow(doc) for doc in docs]
    song1TopicDist = model[newSongs[0]]
    song2TopicDist = model[newSongs[1]]
    song1TopicDist, song2TopicDist = toDenseArrays(
        song1TopicDist, song2TopicDist)
    return(distance.jensenshannon(song1TopicDist, song2TopicDist))


def songComparison(model, song1, artist1, song2, artist2):
    genius = Genius(API_Keys.genius_access_token)
    genius.timeout = 15
    genius.sleep_time = 2

    lyrics1 = getLyrics(song1, artist1, genius)
    lyrics2 = getLyrics(song2, artist2, genius)
    if lyrics1 is None:
        print(song1)
        return(None)
    if lyrics2 is None:
        print(song2)
        return(None)
    docs = [lyrics1, lyrics2]
    dist = getSongDivergence(model, docs)
    return(dist)


if __name__ == '__main__':
    song1 = 'panini'
    artist1 = 'lil nas x'
    song2 = 'panini'
    artist2 = 'lil nas x'
    model = LdaModel.load(MODEL_LOCATION)

    dist = songComparison(model, song1, artist1, song2, artist2)
