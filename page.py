
from typing import List

class Page():
    """
    A class representing a simple text page.
    """

    def __init__(self, init_str: str = ''):
        """
        Initialize a Page object with the given initial string as its body.

        Parameters:
        - init_str (str): The initial string to set as the body of the page. Defaults to an empty string.
        """

        self.body = init_str

    def press(self, string: str, end: str = '\n') -> None:
        """
        Append the given string and the end character(s) to the body of the page.

        Parameters:
        - string (str): The string to append to the body of the page.
        - end (str): The character(s) to append after the string. Defaults to a newline character.

        Returns:
        - None
        """
        self.body = self.body + string + end

class StyledPage():
    """
    A class representing a simple text page.
    """
    def __init__(self):
        self.body = ''

    def _escape(self, text: str) -> str:
        markdown_chars = ["_", "*", "`", "[", "]", "(", ")", "#", "+", "-", ".", "!", "$"]
        for i in range(len(markdown_chars)):
            text = text.replace(markdown_chars[i], '\\' + markdown_chars[i])
        return text

    def h1(self, string: str) -> None:
        string = self._escape(string)
        self.body = self.body + f'\n# {string}\n\n'
    
    def h2(self, string: str) -> None:
        string = self._escape(string)
        self.body = self.body + f'\n## {string}\n\n'

    def h3(self, string: str) -> None:
        string = self._escape(string)
        self.body = self.body + f'\n### {string}\n\n'

    def h4(self, string: str) -> None:
        string = self._escape(string)
        self.body = self.body + f'\n#### {string}\n\n'

    def add_heading(self, string: str, h_level: int, end='\n\n') -> None:
        string = self._escape(string)
        self.body = self.body + f"{'#'*h_level} {string}{end}"
    
    def add_paragraph(self, string: str) -> None:
        string = self._escape(string)
        self.body = self.body + string + '\n\n'
    
    def add_blockquote(self, string:str) -> None:
        string = self._escape(string)
        self.body = self.body + '> ' + string + '\n\n'
    
    def add_link(self, url, title):
        title = self._escape(title)
        self.body = self.body + f'[{title}]({url}) \n\n'
    
    def add_raw_text(self, string: str, end='') -> None:
        self.body = self.body + string + end
    
    def add_unordered_list(self, list: list) -> None:
        output = ''
        for i, item in enumerate(list):
            item = self._escape(str(item))
            output = output + f'{i+1}. {item}\n'

        self.body = self.body + output + '\n\n'

    def add_ordered_list(self, list: list) -> None:
        output = ''
        for item in list:
            item = self._escape(str(item))
            output = output + f'- {item}\n'

        self.body = self.body + output + '\n\n'
    
    def divider(self):
        self.body = self.body + '---\n\n'
