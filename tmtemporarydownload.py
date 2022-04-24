import os
import tempfile
import urllib.request, urllib.error

class TemporaryDownload:

    def __init__(self):
        self.tmpdir = tempfile.TemporaryDirectory()
    def __del__(self):
        self.tmpdir.cleanup()

    def gettmpdir(self):
        return self.tmpdir.name

    def download(self,path):
        try:
            response = urllib.request.urlopen(url=path)
            tmppath = os.path.join(self.tmpdir.name,os.path.basename(path))
            with open(tmppath,"wb") as f:
                f.write(response.read())
        except  urllib.error.URLError as e:
            print(e.reason)
        return tmppath
