class Page():
    def __init__(self, init_str=''):
        self.body = init_str

    def press(self, str, end='\n'):
        self.body = self.body + (str+end)