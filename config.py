# if you want change config files format (to YAML for example)
# you should change load and dump methods realization below
# Imortant: new realization must ensure call with following arguments:
# 	load (obj)
# 	dump (obj, fp)

import json

def load(obj):
    return json.load(obj)
def dump(obj, fp):
    return json.dump(obj, fp, ensure_ascii=False,
                              indent=4,
                              sort_keys=True)