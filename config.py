import json
import re
import urllib.request as request

class Config:
    def __init__(self, file, type_='user'):
        self.type_ = type_
        try:
            self.load(file)
        except:
            self.data = None

    def __contains__(self, item):
        for element in self.data:
            if element['link'] == item['link']:
                return True 
        return False

    def generate_default(self):
        if self.type_ == 'user':
            self.data = [{"link": "https://acomics.ru/~4pairs",
                          "name": "4 пары",
                          "page_last": 10}]
        if self.type_ == 'prog':
            self.data = []

    def save(self,file):
        with open(file,'w', encoding='utf-8') as fp:
            self.dump(fp)

    def load(self, file):
        try:
            self.data = json.load(open(file, encoding='utf-8'))
        except FileNotFoundError:
            self.generate_default()
            self.save(file)

    def dump(self, fp):
        return json.dump(self.data, fp, ensure_ascii=False,
                                        indent=4,
                                        sort_keys=True)

    def index(self, key, value):
        for index, item in enumerate(self.data):
            if item[key] == value:
                return index
        return -1


    def generate_comics_data(self, item):
        # 'domaint' and 'relative_URL' fields
        regex_URL = re.compile(r"http[s]?://((\S+.\w+)/([~\S]+))")
        match_obj = regex_URL.match(item['link'])

        domain = match_obj.group(2)
        relative_URL = match_obj.group(3)

        # 'name' field
        if 'name' not in item:
            regex_Name = re.compile("<meta property=\"og:title\" content=\"(.+)\"")
            page = request.urlopen("http://{domain}/{relUrl}".format(domain=domain,
                                                                     relUrl=relative_URL)).read().decode('utf-8')
            name = regex_Name.search(page).group(1)
        else:
            name = ''

        # Result
        genreated = {'page_first': None,
                     'page_current': 1,
                     'page_last': None,
                     'downloaded_in_this_session': 0,
                     'domain': domain,
                     'relative_URL': relative_URL,
                     'page_last_exist': 0,
                     'name': name}

        item.update(genreated)

    def append(self,item):
        self.data.append({})
        self.data[-1]['link'] = item['link']

    def update(self, other):
        for item in other.data:
            if item in self:
                index = self.index('link', item['link'])
            else:
                self.append(item)
                index = -1

            self.generate_comics_data(self.data[index])
            self.data[index].update(item)

# ----------------------------------------------------------------------------

