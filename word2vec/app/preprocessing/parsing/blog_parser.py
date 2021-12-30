import yaml
import re
from os import path, listdir


class BlogParser(object):
    def __init__(self, blog_dir):
        dir_name = path.dirname(__file__)
        self.blog_directory = path.join(dir_name, blog_dir)

    def parse_blog_files(self):
        dir_name = path.dirname(__file__)
        for filename in listdir(self.blog_directory):
            parsed_blog_file = path.join(
                dir_name, "../../../data/2_parsed/blogs", filename
            )
            if not path.exists(parsed_blog_file):
                self.parse_blog_file(filename, parsed_blog_file)

    # Remove code blocks and blog meta tags
    def parse_blog_file(self, source_file, target_file):
        include_line = True
        blog_file = path.join(self.blog_directory, source_file)
        with open(blog_file, "r", encoding="utf-8", errors="ignore") as blog_data:
            blog_lines = (line.rstrip() for line in blog_data if line)
            cleaned_blog_lines = []
            for blog_line in blog_lines:
                is_comment_code_block_sep = re.match("^(`|-|~){3}.*$", blog_line)
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
            blog_as_string = " ".join(cleaned_blog_lines)
            with open(target_file, "w") as prepared_data:
                # write each sentence on a single line
                for blog_sentence in blog_as_string.split("."):
                    prepared_data.write(blog_sentence.strip())
                    prepared_data.write("\n")


def main():
    dir_name = path.dirname(__file__)
    config_file = path.join(dir_name, "../../../config.yaml")
    config_dict = None
    with open(config_file) as config:
        config_dict = yaml.load(config, Loader=yaml.Loader)
    blog_directory = config_dict["blog_directory"]
    blog_preparer = BlogParser(blog_directory)
    blog_preparer.parse_blog_files()


if __name__ == "__main__":
    main()
