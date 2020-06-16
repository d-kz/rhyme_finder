from lyrics import Lyrics
from colored import fg, bg, attr
import random

file_name = 'lyrics_fr/Feu_Zoe.txt'

language = 'fr'
print_stats = True
lookback = 15
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
    words_rhymes = [None for i in range(len(words))]
    for rhyme, word_pairs in rhymes:
        for word_pair in word_pairs:
            i, j, l = word_pair
            print i, j, len(words_rhymes)
            for offset in range(l): # overwrite with longest rhymes
                words_rhymes[i+offset] = rhyme
                words_rhymes[j+offset] = rhyme

            # if #vowels in a word != len(rhyme), previous word needs to be included too
            # if word[i]

    printout = ''
    line = 0
    for i, word_instance in enumerate(words):
        # color rhymed words
        word = word_instance.word
        if words_rhymes[i] != None:
            rhyme_str = words_rhymes[i]
            word = get_text_in_color(word, rhyme_color_map[rhyme_str])
        printout += word + ' '
        if i in newlines:
            printout += '\n'
        # # print transcription
        # if '\n' in word:
        #     print line
        #     printout += get_text_in_color(transcription_lines[line], '#C0C0C0') + '\n'
        #     # printout += transcription_lines[line] + '\n'
        #     if line < len(transcription_lines) - 2:
        #         line += 1


    print printout








rhymes = l.get_rhymes()
print rhymes

print_lyrics(l.words, rhymes, l.new_lines)




