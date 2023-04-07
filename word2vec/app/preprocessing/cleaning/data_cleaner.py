import sys
import re
from os import path, listdir


def clean_line(dirty_line, stop_words):
    a_line = dirty_line.lower()  # We are not interested in lower or upper case
    a_line = re.sub("\t", " ", a_line)  # tabs to single space
    a_line = re.sub(" +", " ", a_line)  # remove superfluous whitespaces
    a_line = re.sub(r"-\[readmore\]-", "", a_line)
    a_line = re.sub(" ' ", "'", a_line)
    a_line = re.sub("'m", " am", a_line)
    a_line = re.sub("`m", " am", a_line)
    a_line = re.sub(" 'n ", " and ", a_line)
    a_line = re.sub(" `n ", " and ", a_line)
    a_line = re.sub(" n' ", " and ", a_line)
    a_line = re.sub("'s", " is", a_line)
    a_line = re.sub("`s", " is", a_line)
    a_line = re.sub("´s", "", a_line)  # genitive-s: ignore
    a_line = re.sub("isn't", "is not", a_line)
    a_line = re.sub("isn`t", "is not", a_line)
    a_line = re.sub("'ll", " will", a_line)
    a_line = re.sub("`ll", " will", a_line)
    a_line = re.sub("’ll", " will", a_line)
    a_line = re.sub("'ve", " have", a_line)
    a_line = re.sub("`ve", " have", a_line)
    a_line = re.sub("’ve", " have", a_line)
    a_line = re.sub("'re", " are", a_line)
    a_line = re.sub("`re", " are", a_line)
    a_line = re.sub("’re", " are", a_line)
    a_line = re.sub("'d", " would", a_line)
    a_line = re.sub("`d", " would", a_line)
    a_line = re.sub("’d", " would", a_line)
    a_line = re.sub("'em", "them", a_line)
    a_line = re.sub("`em", "them", a_line)
    a_line = re.sub("'bout", "about", a_line)
    a_line = re.sub("`bout", "about", a_line)
    a_line = re.sub("aren't", "are not", a_line)
    a_line = re.sub("aren`t", "are not", a_line)
    a_line = re.sub("ain't", "am not", a_line)
    a_line = re.sub("ain`t", "am not", a_line)
    a_line = re.sub("can't", "cannot", a_line)
    a_line = re.sub("can`t", "cannot", a_line)
    a_line = re.sub("didn't", "did not", a_line)
    a_line = re.sub("didn`t", "did not", a_line)
    a_line = re.sub("doesn't", "does not", a_line)
    a_line = re.sub("doesn`t", "does not", a_line)
    a_line = re.sub("doin'", "doing", a_line)
    a_line = re.sub("don't", "do not", a_line)
    a_line = re.sub("don`t", "do not", a_line)
    a_line = re.sub("don’t", "do not", a_line)
    a_line = re.sub("haven't", "have not", a_line)
    a_line = re.sub("haven`t", "have not", a_line)
    a_line = re.sub("hasn't", "has not", a_line)
    a_line = re.sub("hasn`t", "has not", a_line)
    a_line = re.sub("hasn’t", "has not", a_line)
    a_line = re.sub("let's", "let us", a_line)
    a_line = re.sub("let`s", "let us", a_line)
    a_line = re.sub("let´s", "let us", a_line)
    a_line = re.sub("n’t", " not", a_line)
    a_line = re.sub("wasn't", "was not", a_line)
    a_line = re.sub("wasn`t", "was not", a_line)
    a_line = re.sub("wasn’t", "was not", a_line)
    a_line = re.sub("weren't", "were not", a_line)
    a_line = re.sub("weren`t", "were not", a_line)
    a_line = re.sub("won't", "will not", a_line)
    a_line = re.sub("won`t", "will not", a_line)
    a_line = re.sub("wouldn't", "would not", a_line)
    a_line = re.sub("wouldn`t", "would not", a_line)
    a_line = re.sub(" - ", " ", a_line)
    a_line = re.sub("’s", " is", a_line)  # should be last formatting line!
    # we are not interested in numbers, only words
    a_line = re.sub(r"[-+]?[0-9]+[,0-9]*(\.[0-9]+)?", "", a_line)
    # we are not interested in urls
    a_line = re.sub(r"http(s)?:\/\/([\.\-a-z]+)", "", a_line)
    # we are not interested in hyphens, unless they are binding together words
    a_line = re.sub(r"[\s][-]+[\s]+", " ", a_line)  # space, hyphen(s), space
    a_line = re.sub(
        r"[\s]+[-]+", " ", a_line
    )  # space(s) followed by (one or more) hyphen then word
    a_line = re.sub(r"[-]+[\s]+", " ", a_line)  # hyphen followed by space(s)
    # remove special characters, punctuation etc.
    a_line = re.sub(
        r'[()<>‘"”…#@/&%;:`\*\'{}+_\u200B\u2013=~§\$|.!?,\[\]\\]', "", a_line
    )
    # let's remove superfluous whitespaces, again (cleaning can have resulted in additional spaces between words)
    a_line = re.sub(" +", " ", a_line)
    cleaned_line = []
    for word in a_line.split(" "):
        # ignore some nonsense words with varied spelling
        if word not in stop_words:
            cleaned_line.append(word)
    return " ".join(cleaned_line)


class DataCleaner(object):
    def __init__(self, source_dir, target_dir, dry_run=False):
        self.dir_name = path.dirname(__file__)
        self.source_dir = path.join(self.dir_name, source_dir)
        self.target_dir = path.join(self.dir_name, target_dir)
        self.dry_run = dry_run
        stop_words_file = path.join(self.dir_name, "stop_words.txt")
        with open(stop_words_file, "r") as f:
            self.stop_words = [word for line in f for word in line.split()]

    def clean_line(self, dirty_line):
        clean_line(dirty_line=dirty_line, stop_words=self.stop_words)

    def clean_file(self, file_to_clean):
        cleaned_file = path.join(self.target_dir, path.basename(file_to_clean))
        if not path.exists(cleaned_file):
            cleaned_lines = []
            with open(file_to_clean, encoding="utf-8", errors="ignore") as dirty_data:
                for dirty_line in dirty_data:
                    cleaned_lines.append(self.clean_line(dirty_line))

            if self.dry_run:
                return cleaned_lines

            with open(cleaned_file, "w") as clean_data:
                for cleaned_line in cleaned_lines:
                    # If line is shorter than 3 words we ignore it as it doesn't give much to train on
                    if len(cleaned_line.split(" ")) > 2:
                        clean_data.write(cleaned_line)

    def clean_files(self):
        for dirty_file in listdir(self.source_dir):
            self.clean_file(path.join(self.source_dir, dirty_file))


def main():
    clean_directory = sys.argv[1]
    target_dir = path.join("../../../data/3_cleaned", path.basename(clean_directory))
    data_cleaner = DataCleaner(source_dir=clean_directory, target_dir=target_dir)
    data_cleaner.clean_files()


if __name__ == "__main__":
    main()
