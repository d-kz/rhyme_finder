# -*- coding: utf-8 -*-

import codecs
import re
import numpy as np
import os

import phonetics as ph


class Word:
    def __init__(self, text, vowel_str):
        self.new_line = False
        if '\n' in text:
            text = text[0:-1]
            self.new_line = True
        self.word = text
        self.transcription = ph.transcribe_song_fr(self.word)
        self.vowels = []
        self.consonants = []
        for char in self.transcription:
            if char in vowel_str:
                self.vowels.append(char)
            else:
                self.consonants.append(char)

    def __str__(self):
        return self.word.encode('utf8') + "_" + self.transcription.encode('utf8') + "_" +\
        ''.join(self.vowels).encode('utf8') + ''.join(self.consonants).encode('utf8')






class Lyrics:
    """
    # Vowel source: https://www.lawlessfrench.com/pronunciation/ipa-vowels/
    """
    def __init__(self, filename, language='fi',
                 lookback=10, vowel_CM=None, consotant_CM=None, vowel_string=u'aɑeɛəœøioɔuyɑ̃ɛ̃ɔ̃œ̃jwɥ',
                 special_chars=u'éêèéœçâîôûàìòùëïü'):


        # Confusion Matrices:
        self.vowel_CM = vowel_CM
        self.consotant_CM = consotant_CM

        # Language vowels
        self.vowels = vowel_string
        # Characters to not remove during cleaning
        self.rx_letters_to_keep = re.compile(u"[^\w{}'’\.\?!\n]+".format(special_chars)) # '^' - not. '+' - one or more.

        self.lookback = lookback
        self.filename = filename

        self.language = language  # to pass to transcriber
        self.lookback = lookback  # How many previous words are checked for a rhyme.

        # Read song and transcribe it
        self.filename = filename
        f = codecs.open(filename, 'r', 'utf8')
        text_raw = f.read()
        f.close()
        self.text = self.clean_text(text_raw)
        self.process_transcription()

        self.rhyme_map = {}  # to keep track of rhymes



        # Start analysis, if parsed text exists:
        # if self.text_raw is not None:
        #     cleaning_ok = self.clean_text(self.text_raw)
        #     self.compute_vowel_representation()
        #     self.avg_rhyme_length, self.longest_rhyme = self.rhyme_stats()


    def clean_text(self, text):
        '''
        Preprocess text by removing unwanted characters and duplicate rows.
        '''
        # replace all non-chars with spaces
        text = self.rx_letters_to_keep.sub(' ', text)

        # If there are more than 2 consecutive newlines, remove some of them
        text = re.sub('\n\n+', '\n\n', text)

       # Remove duplicate lines
        lines = text.split('\n')
        uniq_lines = set()
        new_text = ''
        for l in lines:
            l = l.strip()
            if len(l) > 0 and l in uniq_lines:
                continue
            # Remove lines that are within brackets/parenthesis
            if len(l) >= 2 and ((l[0] == '[' and l[-1] == ']') or (l[0] == '(' and l[-1] == ')')):
                continue
            uniq_lines.add(l)
            new_text += l + '\n'

        new_text = re.sub('\n', '\n ', new_text)
        return new_text


    def process_transcription(self):
        words = re.split(" ", self.text)

        self.words = []
        for word in words:
            new_word = Word(word, self.vowels)
            self.words.append(new_word)
            print new_word



