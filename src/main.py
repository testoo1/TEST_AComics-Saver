from config import Config
from error  import Error
from image  import Image
from path   import Path

import os
import re
import time
import urllib.request as request

from threading import Thread
from queue import Queue

from json import JSONDecodeError
# small temporary hack:
# allow to change error handling implementation
# without changing the ERROR function call
TEMP_ERROR_OBJ = Error()
ERROR = TEMP_ERROR_OBJ.ERROR

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
            file_name  ="{name}_{counter:04}.{ext}".format(name=item['name'],
                                                           counter=item['page_current'],
                                                           ext=image._ext))
        image.save(path)
    except:
        ERROR("Can't save the image")
        return False

    return True


def check_last(item):
    url = "http://{domain}/{relUrl}/1".format(domain=item['domain'],
                                            relUrl=item['relative_URL'])
    try:
        page = request.urlopen(url).read().decode('utf-8')
        regex_issueNumber = re.compile("<span class=\"issueNumber\">(\d+)/(\d+)</span>")
        item['page_last_exist'] = int(regex_issueNumber.search(page).group(2))
        return True
    except:
        return False

def get_start_page(item):
    return item['page_first'] if item['page_first'] is not None \
      else item['page_current']

def get_stop_page(item):
    return item['page_last'] if item['page_last'] is not None \
                            and item['page_last'] < item['page_last_exist'] \
      else item['page_last_exist']


def download_comics(item):
# Set directory for saving comisc images
    path = Path("{domain}/{name}/".format(domain = item['domain'],
                                          name   = item['name']))
    if not path.set():
        ERROR("Can't set save path for comics \"{name}\"".format(name=item['name']))
        return

# Set first and last pages of download range
    if not check_last(item):
        ERROR("Can't check last issue in comics \"{name}\"".format(name=item['name']))

    start = get_start_page(item)
    stop  = get_stop_page(item)

    if item['page_current'] == stop:
        return

    # TODO: Move all regex dependent from domain into separate function
    regex_Image = re.compile(r"id=\"mainImage\" src=\"(\S+\.(\w+))\"")

# Start download comiсs
    for item['page_current'] in range(start, stop + 1):
        url = "https://{domain}/{name}/{page}".format(domain=item['domain'],
                                                      name  =item['relative_URL'],
                                                      page  =item['page_current'])
        
        try:
            page  = request.urlopen(url).read().decode('utf-8')
        except:
            ERROR("Can't load page \"{url}\"".format(url=url))
            return

        if process_image(page, regex_Image, item):
            item['downloaded_in_this_session'] += 1

def thread_download_comics(threadQueue):
    while not stop:
        download_comics(threadQueue.get())
        threadQueue.task_done()

def show_UI(config, delay):
    while not stop:
        # 79 - console width
        # 17 - width of "xxxx/yyyy (+zzzz)", where:
        # xxxx - current page, 
        # yyyy - last existing page
        # zzzz - new in this session
        block_width = 79 - 17

        os.system('cls')
        # small hack: we use "output" string to reduce console flickering
        #             but we lose in perfomance
        output = ''

        for item in config.data:
            output += ('{name:.<{block_width}}{current:.>4}/{last_existing:>4} ({new:>+4})\n'.format(
                            block_width=block_width,
                            name=item['name'],
                            current=item['page_current'],
                            last_existing=item['page_last_exist'],
                            new=item['downloaded_in_this_session']))
        print(output)
        time.sleep(delay)

def open_file_error(file_name, error_obj):
    error_msg = ("CRITICAL ERROR:\n"
                 "\tfile \"{file_name}\" contain invalid json and can't be open."
                 .format(file_name = file_name))
    print(error_msg)
    ERROR(("{msg}\n\n"
           "\tJSON msg:\n"
           "\t\tline {json_lineno}: {json_msg}"
           .format(msg=error_msg,
                   json_lineno = error_obj.lineno,
                   json_msg    = error_obj.msg)))

# ----------------------------------------------------------------------------

def main():
# Set constants
    USER_CONFIG_FILE = "user.config"
    PROG_CONFIG_FILE = "prog.config"
    
    MAX_THREADS = 5

    UI_delay = 1    # one second

# Work with config files
    # Open
    try:
        file_name = USER_CONFIG_FILE
        user_config = Config(file_name,'user')

        file_name = PROG_CONFIG_FILE
        prog_config = Config(file_name,'prog')

    except JSONDecodeError as error:
        open_file_error(file_name, error)
        exit = input("\nPress enter for exit...")
        return

    # Update
    prog_config.update_with(user_config)

    # Save prog.config
    with open(PROG_CONFIG_FILE,'w', encoding='utf-8') as fp:
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

    # small hack: UI have time to show updated information before thread stop
    time.sleep(UI_delay)

    stop = True
    # small temporary hack:
    # if not set to zero 'downloaded_in_this_session' field - UI show wrong information
    # at the first iteration
    for item in prog_config.data:
        item['downloaded_in_this_session'] = 0

# Save config files
    with open('prog.config','w', encoding='utf-8') as fp:
        prog_config.dump(fp)

    # small hack to enshure that UI thread stop it's working
    time.sleep(UI_delay)

    exit = input("\nPress enter for exit...")
# ----------------------------------------------------------------------------


if __name__ == '__main__':
    main()
