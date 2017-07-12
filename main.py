import config_files
import re
import urllib.request as request
import os

reg_URL = re.compile(r"http[s]?://((\w+.\w+)/([~\w]+))")

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
    add_field(prog_item, 'page_first'  , 1)
    add_field(prog_item, 'page_current', 1)
    add_field(prog_item, 'page_last'   , None)

    match_obj         = reg_URL.match(prog_item['link'])

# small hack: replace already existing link  to link with discarded page number
# example: https://acomics.ru/~4pairs/134 ->
#          https://acomics.ru/~4pairs
    prog_item['link'] = match_obj.group(0)

    domain       = match_obj.group(2)
    relative_URL = match_obj.group(3)
    add_field(prog_item, 'domain', domain)
    add_field(prog_item, 'relative_URL', relative_URL)
    
    # TODO  
    # if "name" not in prog_item:
    #   download page and get name for comics

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
            print('-'*78)
            print("ERROR: Can't create \"{}\" folder".format(name))
            print('-'*78)
            return None
    return name

def set_save_path(domain, name):
    if set_directory(domain) != None:
        path = "{domain}/{name}/".format(domain = domain, name = name)
        if set_directory(path) != None:
            return path
    return None


def get_page():
    pass
def get_image():
    pass
def save_image():
    pass
def get_next_page_URL():
    pass


def download_comics():
    set_save_path()

    is_next_page = True
    while is_next_page:    
        get_page()

        get_image()
        save_image()
        
        get_next_page_URL()
        # temp ->
        is_next_page = False
        # temp <-

# ----------------------------------------------------------------------------

def main():
    # USER_CONFIG_FILE = "user.config"
    # PROG_CONFIG_FILE = "prog.config"

    # user_config, prog_config = config_files.load(USER_CONFIG_FILE,
    #                                              PROG_CONFIG_FILE)
    # update_config(user_config, prog_config)

    # # temp ->
    # config_files.config.dump(prog_config, open('prog.config','w', encoding='utf-8'))
    # # temp <-
    # # -----------------
    # download_comics()
    
    # temp ->
    temp_domain = "acomics.ru"
    temp_link   = "https://acomics.ru/~4pairs"
    temp_name   = "4 пары"
    # temp <-

    path = set_save_path(temp_domain, temp_name)

if __name__ == '__main__':
    main()