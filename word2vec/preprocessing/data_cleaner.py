import re
from os import path


class DataCleaner(object):

    def __init__(self):
        self.stop_words = ['a', 'an', 'and', 'ah', 'as', 'ahh', 'eh', 'ehh', 'ha', 'haa', 'haaa', 'haha', 'hahaha',
                           'hee', 'hehe', 'hehehe', 'heee', 'hoo', 'huh', 'for', 'in', 'of', 'on', 'or', 'oh', 'ohh',
                           'ooh', 'uh', 'uhh', 'er', 'err', 'mm', 'mmm', 'mmmm', 'mmmmm', 'the', 'to', 'whoo', 'woo',
                           'xxxxxx', 'ye', 'yea', 'yeah']

    def __data_cleaner(self, line):
        a_line = line.lower()  # We are not interested in lower or upper case
        a_line = re.sub('\t', ' ', a_line)  # tabs to single space
        a_line = re.sub(' +', ' ', a_line)  # remove superfluous whitespaces
        a_line = re.sub(r'-\[readmore\]-', ' ', a_line)
        a_line = re.sub(' \' ', '\'', a_line)
        a_line = re.sub('\'m', ' am', a_line)
        a_line = re.sub('`m', ' am', a_line)
        a_line = re.sub(' \'n ', ' and ', a_line)
        a_line = re.sub(' `n ', ' and ', a_line)
        a_line = re.sub(' n\' ', ' and ', a_line)
        a_line = re.sub('let\'s', 'let us', a_line)
        a_line = re.sub('let`s', 'let us', a_line)
        a_line = re.sub('let´s', 'let us', a_line)
        a_line = re.sub('\'s', ' is', a_line)
        a_line = re.sub('`s', ' is', a_line)
        a_line = re.sub('´s', '', a_line) # genitive-s: ignore
        a_line = re.sub('isn\'t', 'is not', a_line)
        a_line = re.sub('isn`t', 'is not', a_line)
        a_line = re.sub('\'ll', ' will', a_line)
        a_line = re.sub('`ll', ' will', a_line)
        a_line = re.sub('’ll', ' will', a_line)
        a_line = re.sub('\'ve', ' have', a_line)
        a_line = re.sub('`ve', ' have', a_line)
        a_line = re.sub('’ve', ' have', a_line)
        a_line = re.sub('\'re', ' are', a_line)
        a_line = re.sub('`re', ' are', a_line)
        a_line = re.sub('\'d', ' would', a_line)
        a_line = re.sub('`d', ' would', a_line)
        a_line = re.sub('’d', ' would', a_line)
        a_line = re.sub('aren\'t', 'are not', a_line)
        a_line = re.sub('aren`t', 'are not', a_line)
        a_line = re.sub('ain\'t', 'am not', a_line)
        a_line = re.sub('ain`t', 'am not', a_line)
        a_line = re.sub('won\'t', 'will not', a_line)
        a_line = re.sub('won`t', 'will not', a_line)
        a_line = re.sub('wouldn\'t', 'would not', a_line)
        a_line = re.sub('wouldn`t', 'would not', a_line)
        a_line = re.sub('wasn\'t', 'was not', a_line)
        a_line = re.sub('wasn`t', 'was not', a_line)
        a_line = re.sub('wasn’t', 'was not', a_line)
        a_line = re.sub('weren\'t', 'were not', a_line)
        a_line = re.sub('weren`t', 'were not', a_line)
        a_line = re.sub('don\'t', 'do not', a_line)
        a_line = re.sub('don`t', 'do not', a_line)
        a_line = re.sub('don’t', 'do not', a_line)
        a_line = re.sub('doesn\'t', 'does not', a_line)
        a_line = re.sub('doesn`t', 'does not', a_line)
        a_line = re.sub('didn\'t', 'did not', a_line)
        a_line = re.sub('didn`t', 'did not', a_line)
        a_line = re.sub('can\'t', 'cannot', a_line)
        a_line = re.sub('can`t', 'cannot', a_line)
        a_line = re.sub('hasn\'t', 'has not', a_line)
        a_line = re.sub('hasn`t', 'has not', a_line)
        a_line = re.sub('hasn’t', 'has not', a_line)
        a_line = re.sub('n’t', ' not', a_line)
        a_line = re.sub('’re', ' are', a_line)
        a_line = re.sub('haven\'t', 'have not', a_line)
        a_line = re.sub('haven`t', 'have not', a_line)
        a_line = re.sub('\'bout', 'about', a_line)
        a_line = re.sub('`bout', 'about', a_line)
        a_line = re.sub('doin\'', 'doing', a_line)
        a_line = re.sub('let’s', 'let us', a_line)
        a_line = re.sub('\'em', 'them', a_line)
        a_line = re.sub('`em', 'them', a_line)
        a_line = re.sub(' - ', ' ', a_line)
        a_line = re.sub('’s', ' is', a_line)  # should be last formatting line!
        # we are not interested in numbers, only words
        a_line = re.sub(r'[-+]?[0-9]+[,0-9]*(\.[0-9]+)?', '', a_line)
        # we are not interested in hyphens, unless they are binding together words
        a_line = re.sub(r'[\s][-]+[\s]+', ' ', a_line)  # space, hyphen(s), space
        a_line = re.sub(r'[\s][-]+[\S]+', ' ', a_line)  # space followed by (one or more) hyphen then word
        a_line = re.sub(r'[\S]+[-]+[\s]', ' ', a_line)  # word ending with hyphen and then space
        # we are not interested in http urls
        a_line = re.sub(r'http(\S)+', '', a_line)  # "@”
        a_line = re.sub(r'www(\S)+', '', a_line)
        # remove special characters, punctuation etc.
        a_line = re.sub(r'[()‘"”…#@/&%;:`\*\'<>{}+_\u200B\u2013=~§\$|.!?,\[\]\\]', '', a_line)
        # let's remove superfluous whitespaces, again (cleaning can have resulted in additional spaces between words)
        a_line = re.sub(' +', ' ', a_line)
        cleaned_line = []
        for word in a_line.split(' '):
            # ignore some nonsense words with varied spelling
            if word not in self.stop_words:
                cleaned_line.append(word)
        return ' '.join(cleaned_line)

    def clean_lines(self, file_to_clean, append=False):
        cleaned_file = 'data/cleaned_data.txt'
        if not path.exists(cleaned_file) or append:
            clean_lines = []
            with open(file_to_clean) as dirty_data:
                for dirty_line in dirty_data:
                    clean_lines.append(self.__data_cleaner(dirty_line))

            with open(cleaned_file, "a") as clean_data:
                for clean_line in clean_lines:
                    clean_data.write(clean_line)

        return cleaned_file
