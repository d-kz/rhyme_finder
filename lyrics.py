# -*- coding: utf-8 -*-

import codecs
import re
import numpy as np
import phonetics as ph

"""
TODOs:
(need)
- Confusion matrices for sounds
    - input
    - cutoff logic
- Heuristic for rhyme computation: vowel alignment, consonant similarity
    - not only 2 words can rhyme. Rhyme are transitive: if a -> b and b -> c, then a -> c.
    Add a 1-step travelrsal (1 matrix self multiply to be transitivity exactly - reachable in 1 step)
(nice)
- rhyme pattern symbolic at the end of the line (to see how the rhyming pattern mixes)
- breakup rhyme highlighting by syllable: map transcription to original
- filter 'bad' rhymes
- what was their annealing for printing?
DONE:
- breakup rhyme highlighting by syllable: map transcription to original
    -  might need text syllables too
- rhyming: center around vowel, then consonant
- assemble lyrics back with highlighting (from previous version)
- Sliding window across syllables
- Syllable breakup
"""

class Word:
    def __init__(self, text, transcribed_word, vowel_str):
        self.new_line = False
        if '\n' in text:
            text = text[0:-1]
            self.new_line = True
        self.word = text
        self.transcription = transcribed_word
        self.vowels = []
        self.consonants = []
        is_cons = lambda char: char not in vowel_str

        # Syllable analysis, adding vowels/consonants to arrays.
        syllable = ''
        self.syllables = []
        i = 0
        vowel_offset = 0
        length = len(self.transcription)
        while i < length:
            char = self.transcription[i]
            # collect chars until vowel is found, then +1 consonant
            if is_cons(char):
                self.consonants.append(char)
                syllable += char
                vowel_offset += 1
                i += 1
            # vowel found
            else:
                self.vowels.append(char)
                syllable += char
                i += 1
                # if char after is a consonant, add that too
                # only update if yes, otherwise, just continue as normal
                if (i < length) and is_cons(self.transcription[i]):
                    char = self.transcription[i]
                    self.consonants.append(char)
                    syllable += char
                    i += 1

                self.syllables.append({'syl':syllable, 'vow':vowel_offset})
                syllable = ''
                vowel_offset = 0
        self.get_word_splits()


    def __str__(self):
        """
        Overwrite for printing
        :return:
        """
        return self.word.encode('utf8') + "_" + self.transcription.encode('utf8') + "_" +\
        ''.join(self.vowels).encode('utf8') + ''.join(self.consonants).encode('utf8')


    def get_word_splits(self):
        diff = len(self.word) - len(self.transcription)
        if diff < 0:
            print "ALERT, diff is less than 0"

        n_syl = len(self.syllables)
        a = [0]
        word_split = 0
        for i in range(n_syl-1):
            l = len(self.syllables[i]['syl'])
            word_split = l
            # add 1 char from each syllable if excess
            if diff > 0:
                word_split += 1
                diff -= 1
            a.append(word_split)
        a.append(len(self.word))
        self.word_splits = [self.word[a[i]:a[i+1]] for i in range(len(a) - 1)]





class Lyrics:
    """
    # Vowel source: https://www.lawlessfrench.com/pronunciation/ipa-vowels/
    Model example from WSF:
        - https://graphics.wsj.com/hamilton-methodology/
            - As we did with vowel sounds, we score syllable pairs based on how similar their suffixes sound
        - http://graphics.wsj.com/hamilton/
    """
    def __init__(self, filename, language='fi',
                 lookback=10, vowel_CM=None, consotant_CM=None, vowel_string=u'aɑeɛəœøioɔuyɑ̃ɛ̃ɔ̃œ̃jwɥ',
                 special_chars=u'éêèéœçâîôûàìòùëïü'):
        """

        :param filename:
        :param language:
        :param lookback: minimum number of syllables to look at (whatever exceeds from the same word is kept)
        :param vowel_CM:
        :param consotant_CM:
        :param vowel_string:
        :param special_chars:
        """


        # Confusion Matrices:
        self.vowel_CM = vowel_CM
        self.consotant_CM = consotant_CM

        # Language vowels
        self.vowels = vowel_string
        # Characters to not remove during cleaning
        self.rx_letters_to_keep = re.compile(u"[^\w{}'’\n]+".format(special_chars)) # '^' - not. '+' - one or more.

        self.language = language  # to pass to transcriber
        self.lookback = lookback  # How many previous words are checked for a rhyme.

        # Read song and transcribe it
        self.filename = filename
        f = codecs.open(filename, 'r', 'utf8')
        text_raw = f.read()
        f.close()
        self.text = self.clean_text(text_raw)
        self.transcribed_text = ph.transcribe_song_fr(self.text)
        self.process_transcription()

        self.rhyme_map = {}  # to keep track of rhymes



        # Start analysis, if parsed text exists:
        self.slide_window_across_words(self.rhyme_heuristic)
        # if self.text_raw is not None:
        #     cleaning_ok = self.clean_text(self.text_raw)
        #     self.compute_vowel_representation()
        #     self.avg_rhyme_length, self.longest_rhyme = self.rhyme_stats()

    def vowel_similarity(self, thresh):
        """
        Cutoff histogram at thresh percentage of values
        :return: hashmap of similar sounding transcription sounds, with scores.
        """
        return 1.0

    def consonant_similairty(self, thresh):
        return 1.0



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

        # add extra space after newline for cohesive spacing
        new_text = re.sub('\n', '\n ', new_text)
        self.record_new_lines(new_text)

        new_text = re.sub('\n', ' ', new_text) # new line replace
        new_text = re.sub('  ', ' ', new_text) # double space replace
        return new_text

    def record_new_lines(self, text):
        words = re.split(" ", text)
        newlines = []
        for i, word in enumerate(words):
            if '\n' in word:
                newlines.append(i)
        self.new_lines = newlines

    def process_transcription(self):
        words = re.split(" ", self.text)
        transcribed_words = re.split(" ", self.transcribed_text)

        self.words = []
        for i in range(len(words)):
            new_word = Word(words[i], transcribed_words[i], self.vowels)
            self.words.append(new_word)
            print new_word

    def slide_window_across_words(self, rhyme_evaluator):
        """
        Slide through word list using [window X window] comparison word matrix.
        Could do syllabus instead too?
        :return:
        """
        syllable_window_q = []
        # mimics syllable queue, but only with word ids (needed to match words to syllables later)
        word_id_q = []
        i = 0
        while i < len(self.words):
            if len(syllable_window_q) < self.lookback:
                word = self.words[i]
                # insert length of syllables to know how much to remove later
                for syl_i, syllable in enumerate(word.syllables):
                    # push into queue
                    word_id_q.insert(0, {'word': i, 'syl': syl_i})
                    syllable_window_q.insert(0, syllable)
                i += 1
            else:

                # print "Before", "_".join(syllable_window_q).encode('utf8'), '_'.join([str(num) for num in word_id_q])

                # send for rhyme analysis , reverse both queues for more intuitive structure
                syllable_list = [el for el in reversed(syllable_window_q)]
                word_list = [el for el in reversed(word_id_q)]
                self.get_best_rhymes(i, syllable_list, word_list, rhyme_evaluator)

                # keep popping 1 word at a time until the lookback is not below needed again
                # get word_id of the first word that was pushed onto queue
                first_word_id = word_id_q[-1]['word']
                # delete queue until the whole word is removed.
                while len(word_id_q) > 0:
                    word_id = word_id_q[-1]['word']
                    # stop if next word encountered
                    if word_id != first_word_id:
                        break
                    else:
                        word_id_q.pop()
                        syllable_window_q.pop()

                # print "After", "_".join(syllable_window_q).encode('utf8'), '_'.join([str(num) for num in word_id_q]), '\n'


    def get_best_rhymes(self, word_id_offset, syllable_list, word_list, rhyme_evaluator):
        """
        Construct a matrix of rhyme values.
        Pick the strongest, longest candidates and return them.
        :param syllable_list:
        :param word_list:
        :return:
        """
        n = len(syllable_list)
        rhyme_values_mat = np.full((n, n),-1)

        for i in range(n):
            for j in range(n):
                # ignore diagonal (can't rhyme with itself)
                if i == j:
                    continue
                # matrix is symmetric, so ignore if already computed
                elif rhyme_values_mat[j,i] != -1:
                    rhyme_values_mat[i, j] = rhyme_values_mat[j,i]
                # finally, compute actual rhyme score
                else:
                    syl1 = syllable_list[i]
                    syl2 = syllable_list[j]
                    rhyme_values_mat[i,j] = rhyme_evaluator(syl1, syl2)

        # TODO: multiple rhymes are possible in one window, include all above threshold.
        # pick the longest continuous rhyme, starting with strongest (argmax) rhyming syllable
        i, j = np.unravel_index(rhyme_values_mat.argmax(), rhyme_values_mat.shape) # gets 2d coordinates, not flat
        rhyme_length = 0 # how long does the rhyme continue for
        while (i + rhyme_length < n - 1) and (j + rhyme_length < n - 1) and rhyme_values_mat[i+rhyme_length, j+rhyme_length] > 0: #TODO: another threshold place?
            rhyme_length += 1




        # Ignore rhymes with length 1
        # if rhyme_length >= self.rhyme_cutoff:
        if rhyme_length > 0:
            syllables_strings = [syl['syl'] for syl in syllable_list]
            word_i, word_j = word_list[i], word_list[j]
            rhyme_syllables = ''.join(syllables_strings[i:i+rhyme_length]) # TODO: just pick one variant of syllable sounds
            # save word ids with this rhyme
            rhymes = self.rhyme_map.get(rhyme_syllables, [])
            rhymes.append([word_i, word_j, rhyme_length])
            self.rhyme_map[rhyme_syllables] = rhymes


    def rhyme_heuristic(self, syl1_tuple, syl2_tuple):
        """

        :param syl1: (syllable, vowel_offset)
        :param syl2:
        :return: int
        """
        syl1, vow1 = syl1_tuple['syl'], syl1_tuple['vow']
        syl2, vow2 = syl2_tuple['syl'], syl2_tuple['vow']

        l1,l2 = len(syl1), len(syl2)
        rhyme = 0.0
        if syl1[vow1] == syl2[vow2]:
            rhyme += 1
            # cons ahead of vowel
            if vow1+1 < l1 and vow2+1 < l2:
                if syl1[vow1+1] == syl2[vow2+1]:
                    rhyme += 0.0

            # cons behind vowel
            if vow1-1 >= 0 and vow2-1 >= 0:
                if syl1[vow1-1] == syl2[vow2-1]:
                    rhyme += 0.0


        # rhyme_val_mat = np.full((l1, l2), -0.1) #TODO: should it be neutral or punishing?
        # for i in range(l1):
        #     for j in range(l1):
        #         a = syl1[i]
        #         b = syl2[j]
        #         if a == b:
        #             rhyme_val_mat = 1.0
        #         # TODO: add confusion matrix similar sounds
        #         # elif
        # sum of all rhyming sounds
        # rhyme = np.sum(rhyme_val_mat)

        return rhyme





                    # 1) Vowels
        # Exact matching
        # Weak matching

        # Consonants

    def get_rhymes(self):
        """
        Longer rhymes take priority
        :return:
        """
        rhymes = sorted(self.rhyme_map.items(), key=lambda x: len(x[0]))  # sort by increasing length of rhyme
        return rhymes

