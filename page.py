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
        self.body += (string + end)