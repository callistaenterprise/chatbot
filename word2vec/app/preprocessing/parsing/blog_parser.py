import yaml
import re
from os import path, listdir
import logging


class BlogParser(object):
    logging.basicConfig(level=logging.INFO)

    def __init__(self, blog_dir, dry_run=False):
        dir_name = path.dirname(__file__)
        self.logger = logging.getLogger(__name__)
        self.blog_directory = path.join(dir_name, blog_dir)
        self.dry_run = dry_run

    def _tag_remover(self, line):
        opening_tag_index = line.find('<')
        closing_tag_index = line.find('>')
        if 0 <= opening_tag_index < closing_tag_index:
            if opening_tag_index > 0:
                return self._tag_remover(line[:opening_tag_index - 1] + line[closing_tag_index + 1:])
            else:
                return self._tag_remover(line[closing_tag_index + 1:])
        return line

    def _link_remover(self, line):
        open_bracket_index = line.find('[')
        close_bracket_index = line.find(']')
        if 0 <= open_bracket_index < close_bracket_index:
            open_parenthesis_index = line[close_bracket_index:].find('(')
            close_parenthesis_index = line[close_bracket_index:].find(')')
            if 0 <= open_parenthesis_index < close_parenthesis_index:
                return self._link_remover(line[:close_bracket_index + open_parenthesis_index] +
                                          line[close_bracket_index + close_parenthesis_index + 1:])
        return line

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
        self.logger.info(f"Parsing blog file: {blog_file}")
        with open(blog_file, "r", encoding="utf-8", errors="ignore") as blog_data:
            blog_lines = (line.rstrip() for line in blog_data if line)
            parsed_blog_lines = []
            for blog_line in blog_lines:
                is_comment_code_block_sep = re.match("^(`|-|~){3}.*$", blog_line)
                if is_comment_code_block_sep and include_line:
                    include_line = False
                elif is_comment_code_block_sep and not include_line:
                    include_line = True
                    continue
                if include_line:
                    # replace NBSP with normal space
                    blog_line = " ".join(blog_line.split())
                    # remove links:
                    blog_line = self._link_remover(blog_line)
                    # remove html tags
                    blog_line = self._tag_remover(blog_line)
                    # remove quotes and stars, parenthesis and brackets
                    # blog_line = re.sub(r"`\"\'\*\[\]\(\)", "", blog_line)
                    parsed_blog_lines.append(blog_line)
            if self.dry_run:
                return parsed_blog_lines
            with open(target_file, "w") as prepared_data:
                for parsed_blog_line in parsed_blog_lines:
                    prepared_data.write(parsed_blog_line.strip())
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
