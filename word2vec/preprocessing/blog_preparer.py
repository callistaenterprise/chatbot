import re
import os


class BlogPreparer(object):

    def __init__(self, blog_dir):
        self.blog_directory = blog_dir

    def parse_blog_files(self):
        prepared_data_file = 'data/preprocessing/prepared_blog_data.txt'
        blogs = []
        # blog_files = [file for file in os.listdir(self.blog_directory)]
        for filename in os.listdir(self.blog_directory):
            # print(f'processing file: {filename}')
            include_line = True
            with open(os.path.join(self.blog_directory, filename), 'r') as blog_data:
                blog_lines = (line.rstrip() for line in blog_data if line)
                cleaned_blog_lines = []
                for blog_line in blog_lines:
                    is_comment_code_block_sep = re.match('^(`|-|~){3}.*$', blog_line)
                    if is_comment_code_block_sep and include_line:
                        include_line = False
                        # print(f'\"{blog_line}\" turns include_line: {include_line}')
                    elif is_comment_code_block_sep and not include_line:
                        include_line = True
                        # print(f'\"{blog_line}\" turns include_line: {include_line}')
                        continue
                    if re.match('^#+.*$', blog_line):
                        continue
                    if include_line:
                        # replace NBSP with normal space
                        blog_line = ' '.join(blog_line.split())
                        # remove anything within parenthesis, usually url:s
                        blog_line = re.sub(r'\(.*\)', '', blog_line)
                        # remove some markup code
                        blog_line = re.sub(r'\{.*\}', '', blog_line)
                        # remove quoted words
                        blog_line = re.sub(r'`[^\s]*`', '', blog_line)
                        cleaned_blog_lines.append(blog_line)
                # print(f'blog lines from {filename}: {len(cleaned_blog_lines)}')
                blog_as_string = ' '.join(cleaned_blog_lines)
            blogs.append(blog_as_string)
        with open(prepared_data_file, "w") as prepared_data:
            for blog in blogs:
                prepared_data.write(blog)
                prepared_data.write('\n')

        return prepared_data_file