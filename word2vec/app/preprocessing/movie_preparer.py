from os import path


class MoviePreparer(object):
    delimiter = ' +++$+++ '
    new_line = '\r\n'

    def __init__(self, movie_lines, movie_conversations):
        self.conversation_lines = []
        self.lines = dict()
        self.conversations = []
        dir_name = path.dirname(__file__)
        self.movie_scripts = path.join(dir_name, movie_lines)
        self.conversation_file = path.join(dir_name, movie_conversations)

    def parse_movie_files(self):
        dir_name = path.dirname(__file__)
        prepared_data_file = path.join(dir_name, '../../data/preprocessing/prepared_movie_data.txt')
        if not path.exists(prepared_data_file):
            with open(self.conversation_file) as mc:
                for line in mc:
                    line = line.rstrip(MoviePreparer.new_line)
                    line = line.split(MoviePreparer.delimiter)[3]
                    self.conversation_lines.append(line)

            with open(self.movie_scripts, encoding='utf-8', errors='ignore') as ml:
                for line in ml:
                    line = line.rstrip(MoviePreparer.new_line)
                    line = line.split(MoviePreparer.delimiter)
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
                    prepared_data.write('\n')

        return prepared_data_file
