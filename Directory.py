import os

class Directory:
    def __init__(self):
        self.cwd = os.getcwd()

    def GetCurrentDirectory(self):
        return self.cwd

    def CreateDirectory(self, foldername):  # TradeLogs
        if not os.path.exists(self.cwd+'\\'+foldername):
            return os.makedirs(self.cwd+'\\'+foldername)
