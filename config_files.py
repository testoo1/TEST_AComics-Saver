import config

def create_default_user_config(user):
    DEFAULT_USER_CONFIG = \
    [
        {
            "link": "https://acomics.ru/~4pairs",
            "name": "4 пары"
        },
        {
            "link": "[mandatory field] link to the comics",
            "name": "[optional  field] name for the folder to which comics will be saved",
            "page_first": "[optional field] save comics from this page",
            "page_last" : "[optional field] to this"
        }
    ]

    with open(user, 'w', encoding='utf-8') as fp:
        config.dump(DEFAULT_USER_CONFIG, fp)
    return DEFAULT_USER_CONFIG

def create_empty_prog_config():
	return []
    
def load_user_config(file):
    try:
        return (config.load(open(file, encoding='utf-8')))
    except FileNotFoundError:
        return (create_default_user_config(file))


def load_prog_config(file):
    try:
        return (config.load(open(file, encoding='utf-8')))
    except FileNotFoundError:
        return (create_empty_prog_config())

def load(user, prog):
    return(load_user_config(user), load_prog_config(prog))