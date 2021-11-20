import re
from os import path, listdir


def get_blog_as_string(directory, filename):
    include_line = True
    blog_file = path.join(directory, filename)
    with open(
            blog_file, "r", encoding="utf-8", errors="ignore"
    ) as blog_data:
        blog_lines = (line.rstrip() for line in blog_data if line)
        cleaned_blog_lines = []
        for blog_line in blog_lines:
            is_comment_code_block_sep = re.match(
                "^(`|-|~){3}.*$", blog_line
            )
            if is_comment_code_block_sep and include_line:
                include_line = False
            elif is_comment_code_block_sep and not include_line:
                include_line = True
                continue
            if re.match("^#+.*$", blog_line):
                continue
            if include_line:
                # replace NBSP with normal space
                blog_line = " ".join(blog_line.split())
                # remove anything within parenthesis, usually url:s
                blog_line = re.sub(r"\(.*\)", "", blog_line)
                # remove some markup code
                blog_line = re.sub(r"\{.*\}", "", blog_line)
                # remove quoted words
                blog_line = re.sub(r"`[^\s]*`", "", blog_line)
                cleaned_blog_lines.append(blog_line)
        return " ".join(cleaned_blog_lines)


class BlogPreparer(object):
    def __init__(self, blog_dir):
        dir_name = path.dirname(__file__)
        self.blog_directory = path.join(dir_name, blog_dir)

    def parse_blog_files(self):
        dir_name = path.dirname(__file__)
        prepared_data_file = path.join(
            dir_name, "../../data/preprocessing/prepared_blog_data.txt"
        )
        blogs = []
        if not path.exists(prepared_data_file):
            for filename in listdir(self.blog_directory):
                blog_as_string = get_blog_as_string(self.blog_directory, filename)
                blogs.append(blog_as_string)
            with open(prepared_data_file, "w") as prepared_data:
                for blog in blogs:
                    blog_sentences = blog.split(".")
                    for blog_sentence in blog_sentences:
                        prepared_data.write(blog_sentence)
                        prepared_data.write("\n")

        return prepared_data_file
