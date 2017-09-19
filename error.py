class Error:
    def __init__(self):
        self.target = open("error.log", 'w')

    def ERROR(self, message):
        self.target.write(message + '\n')
        self.target.flush();
