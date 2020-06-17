from lyrics import Lyrics
from colored import fg, bg, attr
import random

file_name = 'lyrics_fr/Feu_Zoe_short.txt'

language = 'fr'
print_stats = True
lookback = 30
rhyme_cutoff = 2
l = Lyrics(file_name, language=language, lookback=lookback)





def generate_color(number_of_colors):
    color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(number_of_colors)]
    return color


def get_text_in_color(text, color):
    '''
    :param text: text that you're planning to print in color
    :param color: Hex color
    :return: str
    '''
    color = fg(color) + bg("#FFFFFF") # white background is kept constant.
    res = attr('reset')
    return color + text + res




def print_lyrics(words, rhymes, newlines):
    """
    Print original lyrics with rhymes color-coded.
    Longer rhymes take priority
    :param words:
    :param rhymes:
    :return:
    """

    # Color coding rhymes (rhyme_key: color)
    colors = generate_color(len(rhymes))
    rhyme_color_map = {rhyme_tuple[0]: colors[i] for i, rhyme_tuple in enumerate(rhymes)}

    # Keep track of each word's corresponding rhyme. Overwrite with longer rhyme is occurs.
    words_rhymes = {} # [[], None, [], ..]
    for rhyme_str, word_pairs in rhymes:
        for word_pair in word_pairs:
            wor_syl_i, wor_syl_j, l = word_pair # TODO: make this a list


            def _color_word_syllables(words_rhymes, words, word_i, syllable_i, rhyme_length, rhyme_str):
                """
                Check length of word's syllables. If rhyme rhyme_length exceeds, proceed to color next word in words.
                :return: words_rhymes edited
                """
                words_rhymes[word_i] = {}
                _rhyme_length = rhyme_length
                syllables = words[word_i].word_splits
                n_word_syllables = len(syllables)
                while _rhyme_length > 0:
                    syllable = syllables[syllable_i]
                    words_rhymes[word_i][syllable] = rhyme_str
                    syllable_i += 1
                    _rhyme_length -= 1
                    # start on next word, from first syllable
                    if syllable_i >= n_word_syllables - 1:
                        word_i += 1
                        syllable_i = 0
                        syllables = words[word_i].word_splits
                        n_word_syllables = len(syllables)
                        words_rhymes[word_i] = {}

                return words_rhymes

            _color_word_syllables(words_rhymes, words, wor_syl_i['word'], wor_syl_i['syl'], l, rhyme_str)
            _color_word_syllables(words_rhymes, words, wor_syl_j['word'], wor_syl_j['syl'], l, rhyme_str)

            # if #vowels in a word != len(rhyme), previous word needs to be included too
            # if word[i]

    printout = ''
    last_line_word = 0
    for i, word_instance in enumerate(words):
        # color rhymed words
        word_str = word_instance.word
        # check if this word is in rhyme map
        if i in words_rhymes:
            word_syllables = word_instance.word_splits
            word_str = ''
            for syllable in word_syllables:
                if syllable in words_rhymes[i]:
                    rhyme_str = words_rhymes[i][syllable]
                    word_str += get_text_in_color(syllable, rhyme_color_map[rhyme_str])
                else:
                    word_str += syllable
        printout += word_str + ' '
        if i in newlines:
            printout += '\n'

            # print transcription
            for word_i in range(last_line_word, i+1):
                printout += get_text_in_color(words[word_i].transcription, '#C0C0C0') + ' '
            printout += '\n'
            last_line_word = i + 1

    print printout








rhymes = l.get_rhymes()
print rhymes

print_lyrics(l.words, rhymes, l.new_lines)




