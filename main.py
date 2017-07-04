import config_files

def update_config():
    # for item in user_config:
    #   if item in prog_config:
    #       update_prog_config()
    pass

def set_save_path():
    # if not folder on path item.domain + item.name exist
    # create folder
    # return path to folder
    pass

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
    USER_CONFIG_FILE = "user.config"
    PROG_CONFIG_FILE = "prog.config"

    user_config, prog_config = config_files.load(USER_CONFIG_FILE,
                                                 PROG_CONFIG_FILE)
    update_config()
    # -----------------
    download_comics()

if __name__ == '__main__':
    main()