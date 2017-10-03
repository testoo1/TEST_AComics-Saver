import urllib.request as request

class Image:
    def __init__(self):
        self._relUrl = None
        self._url    = None
        self._ext    = None
        self._data   = None

    def find(self, page, regex):
        result = regex.search(page)
        
        self._relUrl = result.group(1)
        self._ext    = result.group(2)

    def url(self, url):
        self._url = url

    def get(self):
        self._data = request.urlopen(self._url).read()
    
    def save(self, path):
        with open(path,'wb') as file:
            file.write(self._data)