from config import Config
from error  import ERROR
from image  import Image

import json
import re
import urllib.request as request

import os
from threading import Thread
from queue import Queue
import time
# reg_URL = re.compile(r"http[s]?://((\S+.\w+)/([~\S]+))")

# def item_in_prog_config(user_item,prog_item):
#     user_link = reg_URL.match(user_item['link'])
#     prog_link = reg_URL.match(prog_item['link'])

#     if not user_link or not prog_link:
#         return False
#     return True if user_link.group(1) == prog_link.group(1) else False

# def add_field(item, key, value):
#     if key not in item:
#         item[key] = value

# def add_missing_field(prog_item):
#     add_field(prog_item, 'page_first'  , None)
#     add_field(prog_item, 'page_current', 1)
#     add_field(prog_item, 'page_last'   , None)

#     add_field(prog_item, 'downloaded_in_this_session', 0)

#     match_obj         = reg_URL.match(prog_item['link'])
#     # small hack: replace already existing link  to link with discarded page number
#     # example: https://acomics.ru/~4pairs/134 ->
#     #          https://acomics.ru/~4pairs
#     prog_item['link'] = match_obj.group(0)

#     domain       = match_obj.group(2)
#     relative_URL = match_obj.group(3)
#     add_field(prog_item, 'domain', domain)
#     add_field(prog_item, 'relative_URL', relative_URL)

#     add_field(prog_item, 'page_last_exist', 0)
    
#     if 'name' not in prog_item:
#         page = request.urlopen("http://{domain}/{relUrl}".format(domain=domain,
#                                                                  relUrl=relative_URL)).read().decode('utf-8')
#         reg  = re.compile("<meta property=\"og:title\" content=\"(.+)\"")
#         try:
#             name = reg.search(page).group(1)
#         except:
#             name = prog_item['relative_URL'][1:]
#         prog_item['name'] = name

 
# def update_prog_config(user_config, prog_config):
#     for user_item in user_config:
#         need_append = True
#         for prog_item in prog_config:
#             if item_in_prog_config(user_item,prog_item):
#                 prog_item.update(user_item)
#                 need_append = False
#                 break
#         # user_item['link'][:4] == 'http' 
#         # It's temporary hack (to discard example data block)
#         if need_append and user_item['link'][:4] == 'http':
#             prog_config.append(user_item)
#             add_missing_field(prog_config[-1])

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

def update_page_last_exist(prog_item):
    page = request.urlopen("http://{domain}/{relUrl}".format(domain=prog_item['domain'],
                                                             relUrl=prog_item['relative_URL'])).read().decode('utf-8')
    reg = re.compile("<span class=\"issueNumber\">(\d+)/(\d+)</span>")
    prog_item['page_last_exist'] = int(reg.search(page).group(2))

def get_page(url):
    try:
        return request.urlopen(url).read().decode('utf-8')
    except:
        return None

# class Image:
#     def __init__(self, data, extension):
#         self.data      = data
#         self.extension = extension

# def get_image(page,item):
#     reg = re.compile(r"id=\"mainImage\" src=\"(\S+\.(\w+))\"")
#     try:
#         result = reg.search(page)
#         image_URL = "http://{domain}{rel_URL}".format(domain =item['domain'],
#                                                       rel_URL=result.group(1))
#         extension = result.group(2)
#         return(Image(request.urlopen(image_URL).read(),extension))
#     except:
#         ERROR("Can't get image from the page")
#         return Image(None, None)

# def save_image(image,item):
#     try:
#         file = open("{domain}/{comics_name}/{file_name}".format(
#             domain     =item['domain'],
#             comics_name=item['name'],
#             file_name  ="{name}_{counter:03}.{ext}".format(name=item['name'],
#                                                            counter=item['page_current'],
#                                                            ext=image.extension)),'wb')
#         file.write(image.data)
#         file.close()
#     except:
#         ERROR("Can't save image \"{file_name}\"".format(\
#             file_name  ="{name}_{counter:03}.{ext}".format(name=item['name'],
#                                                            counter=item['page_current'],
#                                                            ext=image.extension)))

def process_image(page, regex, item):
    image = Image()

    try:
        image.find(page, regex)
    except:
        ERROR("Can't find image relative url on the page")
        return False

    try:
        image.url("http://{domain}{relUrl}".format(domain =item['domain'],
                                                   relUrl =image._relUrl))
    except:
        ERROR("Can't generate full url for the image")
        return False        

    try:
        image.get()
    except:
        ERROR("Can't get image by the url")
        return False

    try:
        path = "{domain}/{comics_name}/{file_name}".format(
            domain     =item['domain'],
            comics_name=item['name'],
            file_name  ="{name}_{counter:03}.{ext}".format(name=item['name'],
                                                           counter=item['page_current'],
                                                           ext=image._ext))
        image.save(path)
    except:
        ERROR("Can't save the image")
        return False

    return True

def download_comics(item):
    if not set_save_path(item):
        ERROR("Can't set path for comics \"{name}\"".format(name=item['name']))
        return

    update_page_last_exist(item)

    regex_Image = re.compile(r"id=\"mainImage\" src=\"(\S+\.(\w+))\"")

    start_page = 0
    stop_page = 0

    start_page = item['page_first'] if   item['page_first'] is not None \
                                    else item['page_current']
    stop_page  = item['page_last'] if item['page_last'] is not None \
                                   and item['page_last'] <= item['page_last_exist'] \
                                   else item['page_last_exist']

    item['downloaded_in_this_session'] = 0

    for item['page_current'] in range(start_page, stop_page + 1):
        url = "https://{domain}/{name}/{page}".format(domain=item['domain'],
                                              name  =item['relative_URL'],
                                              page  =item['page_current'])
        page  = get_page(url)
        if page is None:
            ERROR("Can't load page \"{url}\"".format(url=url))
            return

        # image = get_image(page,item)
        # if image.data is not None and image.extension is not None:
        #     save_image(image,item)
        #     item['downloaded_in_this_session'] += 1
        if process_image(page, regex_Image, item):
            item['downloaded_in_this_session'] += 1

def thread_download_comics(threadQueue):
    while not stop:
        download_comics(threadQueue.get())
        threadQueue.task_done()

def show_UI(config, delay):
    while not stop:
        # 80 - console width
        # 17 - width of "xxxx/yyyy (+zzzz)", where:
        # xxxx - current page, 
        # yyyy - last existing page
        # zzzz - new in this session
        block_width = 80 - 17
        os.system('cls')
        for item in config.data:
            print('{name:.<{block_width}}{current:.>4}/{last_existing:>4} ({new:>+4})'.format(
                block_width=block_width,
                name=item['name'],
                current=item['page_current'],
                last_existing=item['page_last_exist'],
                new=item['downloaded_in_this_session']))
        time.sleep(delay)

# ----------------------------------------------------------------------------

def main():
# Set constants
    USER_CONFIG_FILE = "user.config"
    PROG_CONFIG_FILE = "prog.config"
    
    MAX_THREADS = 5

    UI_delay = 1    # one second

# Open, read and update config files
    user_config = Config(USER_CONFIG_FILE)
    prog_config = Config(PROG_CONFIG_FILE)

    if user_config.data is None or \
       prog_config.data is None:
        ERROR("Can't open (or create) config files")
        return        

    prog_config.update(user_config)
    with open('prog.config','w', encoding='utf-8') as fp:
        prog_config.dump(fp)
    
# Download comics (using multithreading)
    threadQueue = Queue()
    global stop
    stop = False

    for i in range(MAX_THREADS):
        Thread(target=thread_download_comics, args=(threadQueue,), daemon=True).start()
    
    for item in prog_config.data:
        threadQueue.put(item)
    
    UI = Thread(target=show_UI, args=(prog_config,UI_delay), daemon=True).start()

    threadQueue.join()
    
    stop = True

# Save config files
    with open('prog.config','w', encoding='utf-8') as fp:
        prog_config.dump(fp)

    # small hack to enshure that UI thread stop it's working
    time.sleep(UI_delay)
    exit = input("\nPress enter for exit...")
# ----------------------------------------------------------------------------


if __name__ == '__main__':
    main()
