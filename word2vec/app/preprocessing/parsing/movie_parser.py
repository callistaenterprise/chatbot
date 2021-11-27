from os import path
import yaml


class MovieParser(object):
    DELIMITER = " +++$+++ "
    NEW_LINE = "\r\n"

    def __init__(self, movie_lines, movie_conversations):
        # List of strings. Each string is in turn a list of utterance-IDs that make up a conversation
        self.conversation_lines = []
        # Dictionary: key is an ID of the utterance, value is a string with the utterance
        self.lines = dict()
        # List of strings. Each string is a conversation in a movie
        self.conversations = []
        dir_name = path.dirname(__file__)
        self.movie_scripts = path.join(dir_name, movie_lines)
        self.conversation_file = path.join(dir_name, movie_conversations)

    def parse_movie_lines(self):
        dir_name = path.dirname(__file__)
        prepared_data_file = path.join(
            dir_name, "../../../data/2_parsed/movies/parsed_movie_lines.txt"
        )
        if not path.exists(prepared_data_file):
            with open(
                self.movie_scripts, "r", encoding="utf-8", errors="ignore"
            ) as ml, open(prepared_data_file, "w") as fw:
                for line in ml:
                    line = line.rstrip(MovieParser.NEW_LINE)
                    line = line.split(MovieParser.DELIMITER)
                    if len(line) == 5:
                        fw.write(line[4])
                        fw.write("\n")
        return prepared_data_file

    def parse_movie_files(self):
        dir_name = path.dirname(__file__)
        prepared_data_file = path.join(
            dir_name, "../../../data/2_parsed/movies/parsed_movie_data.txt"
        )
        if not path.exists(prepared_data_file):
            with open(self.conversation_file) as mc:
                for line in mc:
                    line = line.rstrip(MovieParser.NEW_LINE)
                    line = line.split(MovieParser.DELIMITER)[3]
                    self.conversation_lines.append(line)

            with open(self.movie_scripts, encoding="utf-8", errors="ignore") as ml:
                for line in ml:
                    line = line.rstrip(MovieParser.NEW_LINE)
                    line = line.split(MovieParser.DELIMITER)
                    if len(line) == 5:
                        key = line[0]
                        value = line[4]
                        self.lines[key] = value

            for conversation_line in self.conversation_lines:
                conversation_list = eval(conversation_line)
                conversation = []
                for line_ref in conversation_list:
                    if line_ref in self.lines:
                        conversation.append(self.lines[line_ref])
                self.conversations.append(" ".join(conversation))

            with open(prepared_data_file, "w") as prepared_data:
                for line in self.conversations:
                    prepared_data.write(line)
                    prepared_data.write("\n")

        return prepared_data_file


def main():
    dir_name = path.dirname(__file__)
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    movie_lines = config_dict["movie_lines"]
    movie_conversations = config_dict["movie_conversations"]
    movie_preparer = MovieParser(movie_lines, movie_conversations)
    movie_preparer.parse_movie_files()
    movie_preparer.parse_movie_lines()


if __name__ == "__main__":
    main()