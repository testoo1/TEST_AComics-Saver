import json
import re
import urllib.request as request

class Config:
    def __init__(self, file, type_='user'):
        self.type_ = type_
        try:
            self.load(file)
        except json.JSONDecodeError:
            raise
   
    def dump(self, fp):
        return json.dump(self.data, fp, ensure_ascii=False,
                                        indent=4,
                                        sort_keys=True)

    def save(self,file):
        with open(file,'w', encoding='utf-8') as fp:
            self.dump(fp)

    def load(self, file):
        try:
            self.data = json.load(open(file, encoding='utf-8'))
        except json.JSONDecodeError as error:
            raise
        except FileNotFoundError:
            self.generate_default()
            self.save(file)

    def generate_default(self):
        if self.type_ == 'user':
            self.data = [{"link": "https://acomics.ru/~4pairs",
                          "name": "4 пары",
                          "page_last": 10}]
        if self.type_ == 'prog':
            self.data = []

    def index(self, other_item):
        for i in range(len(self.data)):
            if self.data[i]['link'] == other_item['link']:
                return i
        return None

    def define_name(self, item):
        regex_name = re.compile("<meta property=\"og:title\" content=\"(.+)\"")
        try:
            page = request.urlopen(item['link']).read().decode('utf-8')
            name = regex_name.search(page).group(1)     
        except:
            raise
        return name

    def fill_fields(self, self_item, other_item):
        # 'page_current'
        # echo of the inelegant solution
        # (see description in the update_with function)
        if 'page_current' in self_item and 'page_current' in other_item:
            page_current = self_item['page_current']
        else:
            page_current = 1

        # 'domain' and 'relative_URL'
        regex_URL = re.compile(r"http[s]?://((\S+.\w+)/([~\S]+))")
        match_obj = regex_URL.match(self_item['link'])

        domain = match_obj.group(2)
        relative_URL = match_obj.group(3)

        # 'name'
        # echo of the inelegant solution
        # (see description in the update_with function)
        if 'name' in self_item and 'name' in other_item:
            name = self_item['name']
        else:
            try:
                name = self.define_name(self_item)
            except:
                # ~comics_name -> comics_name
                name = relative_URL[1:]

        # Result
        filler = {'page_first': None,
                  'page_current': page_current,
                  'page_last': None,
                  'downloaded_in_this_session': 0,
                  'domain': domain,
                  'relative_URL': relative_URL,
                  'page_last_exist': 0,
                  'name': name}

        self_item.update(filler)

    def update_with(self, other):
        for comics_item in other.data:

            item_index = self.index(comics_item)

            if item_index is None:
                self.data.insert(len(self.data), comics_item)
                item_index = -1 # point to the last element
             
            # inelegant problem solution:
                # if user delete field (e.g 'page_last') from the user.config
                # between separate program run, program need to reset value
                # to it's default value in this field in the program.config

                # yep, fields in prog.config would be updated
                # even if in user.config  were no changes  :(
            self.fill_fields(self.data[item_index], comics_item)
            self.data[item_index].update(comics_item)
