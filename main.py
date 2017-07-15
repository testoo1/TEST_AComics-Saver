import config_files
import re
import urllib.request as request
import os
from threading import Thread
from queue import Queue
import time
reg_URL = re.compile(r"http[s]?://((\S+.\w+)/([~\S]+))")

def ERROR(text):
    print('-'*78)
    print("ERROR: {}".format(text))
    print('-'*78)    

def item_in_prog_config(user_item,prog_item):
    user_link = reg_URL.match(user_item['link'])
    prog_link = reg_URL.match(prog_item['link'])

    if not user_link or not prog_link:
        return False
    return True if user_link.group(1) == prog_link.group(1) else False

def add_field(item, key, value):
    if key not in item:
        item[key] = value

def add_missing_field(prog_item):
    add_field(prog_item, 'page_first'  , None)
    add_field(prog_item, 'page_current', 1)
    add_field(prog_item, 'page_last'   , None)

    add_field(prog_item, 'downloaded_in_this_session', 0)

    match_obj         = reg_URL.match(prog_item['link'])
    # small hack: replace already existing link  to link with discarded page number
    # example: https://acomics.ru/~4pairs/134 ->
    #          https://acomics.ru/~4pairs
    prog_item['link'] = match_obj.group(0)

    domain       = match_obj.group(2)
    relative_URL = match_obj.group(3)
    add_field(prog_item, 'domain', domain)
    add_field(prog_item, 'relative_URL', relative_URL)
    
    if 'name' not in prog_item:
        page = request.urlopen("http://{domain}/{relUrl}".format(domain=domain,
                                                                 relUrl=relative_URL)).read().decode('utf-8')
        reg  = re.compile("<meta property=\"og:title\" content=\"(.+)\"")
        try:
            name = reg.search(page).group(1)
        except:
            name = prog_item['relative_URL'][1:]
        add_field(prog_item, 'name', name)

def update_config(user_config, prog_config):
    for user_item in user_config:
        need_append = True
        for prog_item in prog_config:
            if item_in_prog_config(user_item,prog_item):
                prog_item.update(user_item)
                need_append = False
                break
        # user_item['link'][:4] == 'http' 
        # It's temporary hack (to discard example data block)
        if need_append and user_item['link'][:4] == 'http':
            prog_config.append(user_item)
            add_missing_field(prog_config[-1])

def set_directory(name):
    if not os.path.isdir(name):
        try:
            os.mkdir(name)
        except:
            ERROR("Can't create \"{}\" folder".format(name))
            return None
    return name

def set_save_path(item):
    if set_directory(item['domain']) is not None:
        path = "{domain}/{name}/".format(domain = item['domain'],
                                         name   = item['name'])
        if set_directory(path) is not None:
            return path
    return None


def get_page(url):
    try:
        return request.urlopen(url).read().decode('utf-8')
    except:
        return None

class Image:
    def __init__(self, data, extension):
        self.data      = data
        self.extension = extension

def get_image(page,item):
    reg = re.compile(r"id=\"mainImage\" src=\"(\S+\.(\w+))\"")
    try:
        result = reg.search(page)
        image_URL = "http://{domain}{rel_URL}".format(domain =item['domain'],
                                                      rel_URL=result.group(1))
        extension = result.group(2)
        return(Image(request.urlopen(image_URL).read(),extension))
    except:
        ERROR("Can't get image from the page")
        return Image(None, None)

def save_image(image,item):
    try:
        file = open("{domain}/{comics_name}/{file_name}".format(
            domain     =item['domain'],
            comics_name=item['name'],
            file_name  ="{name}_{counter:03}.{ext}".format(name=item['name'],
                                                           counter=item['page_current'],
                                                           ext=image.extension)),'wb')
        file.write(image.data)
        file.close()
    except:
        ERROR("Can't save image \"{file_name}\"".format(\
            file_name  ="{name}_{counter:03}.{ext}".format(name=item['name'],
                                                           counter=item['page_current'],
                                                           ext=image.extension)))

def get_next_page_URL(page):
    try:
        reg = re.compile(r"<a href=\"(\S+)\" class=\"button large comic-nav-next\">")
        return reg.search(page).group(1)
    except:
        return None

def download_comics(item):
    if not set_save_path(item):
        ERROR("Can't set path for comics \"{name}\"".format(name=item['name']))
        return

    if item['page_first'] is not None:
        item['page_current'] = item['page_first']

    item['downloaded_in_this_session'] = 0

    # small hack: when we start download page we set url with last saved
    #             page value. It's help us to check that next page exist
    #             (or we downloaded entire comics in previous session)
    url = "https://{domain}/{name}/{page}".format(domain=item['domain'],
                                                  name  =item['relative_URL'],
                                                  page  =item['page_current'])
    while url:
        if item['page_last'] is None or item['page_current'] <= item['page_last']:
            page  = get_page(url)
            if page is None:
                ERROR("Can't load page \"{url}\"".format(url=url))
                return
            # temp ->
            # print(url)
            # temp <-
            url = get_next_page_URL(page)

            if url or item['downloaded_in_this_session'] != 0:
                # if not url - we on the last page
                # item['downloaded_in_this_session'] != 0 -- small hack:
                #   if value == 0: we stop at this page in previous session
                #                  and downlad image from it already
                #   else: it's last page and we need to download it
                image = get_image(page,item)
                if image.data is not None and image.extension is not None:
                    save_image(image,item)
                    item['page_current'] += 1
                    item['downloaded_in_this_session'] += 1
        else:
            break

    

def thread_download_comics(threadQueue):
    while not stop:
        download_comics(threadQueue.get())
        threadQueue.task_done()

def show_UI(config):
    while not stop:
        # 80 - console width
        # 12 - width of "xxxx (+yyyy)"
        # where xxxx - current page, yyyy - new in this session
        block_width = 80 - 12
        os.system('cls')
        for item in config:
            print('{name:.<{block_width}}{current:.>4}({new:>+4})'.format(
                block_width=block_width,
                name=item['name'],
                current=item['page_current'],
                new=item['downloaded_in_this_session']))
        time.sleep(1)
# ----------------------------------------------------------------------------

def main():
    USER_CONFIG_FILE = "user.config"
    PROG_CONFIG_FILE = "prog.config"
    
    MAX_THREADS = 5
    # ------------------------------------------------------------------------
    try:
        user_config, prog_config = config_files.load(USER_CONFIG_FILE,
                                                     PROG_CONFIG_FILE)
    except:
        ERROR("Can't open (or create) config files")
        return        
    
    update_config(user_config, prog_config)

    # ------------------------------------------------------------------------
    threadQueue = Queue()
    global stop
    stop = False

    for i in range(MAX_THREADS):
        Thread(target=thread_download_comics, args=(threadQueue,), daemon=True).start()
    
    for item in prog_config:
        threadQueue.put(item)
    
    UI = Thread(target=show_UI, args=(prog_config,), daemon=True).start()

    threadQueue.join()
    
    stop = True
    # ------------------------------------------------------------------------
    config_files.config.dump(prog_config, open('prog.config','w', encoding='utf-8'))

    exit = input("\nPress enter for exit...")
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
