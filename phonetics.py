
import os
import codecs
import re




def transcribe_song_fr(text):
    import epitran
    import codecs
    epi = epitran.Epitran('fra-Latn')

    # f = codecs.open(filename, 'r', 'utf8')
    # text = f.read()
    # f.close()

    transcribed_song = epi.transliterate(text)
    # print(text, transcribed_song)
    return transcribed_song
