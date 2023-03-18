import unittest


class DocClassifierTrainingBuilderTest(unittest.TestCase):
    def test_build_paragraphs_from_text(self):
        text = """this is a multiline test text from which
        I will try to generate a number of equal length paragraph word-lists
        each containing five consecutive words from this text"""
        self.assertEqual(True, True)  # add assertion here

    def test_line_concatenator(self):
        line1 = "one two three"
        line2 = "four five six"
        line3 = "seven eight nine"
        expected = "one two three four five six seven eight nine"
        space = " "
        all_lines = ""
        all_lines += line1
        all_lines += space
        all_lines += line2
        all_lines += space
        all_lines += line3
        self.assertEqual(all_lines, expected)

if __name__ == '__main__':
    unittest.main()
