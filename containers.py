'''
Library Container Classes

** to be removed when py-plex api work is finished **
** Show/Movie/etc. classes already replaced by api **
'''

# ---------------------------------------------------- #
#              Library Container Classes               #
# ---------------------------------------------------- #

# Info class: contains select keys from MediaContainer tag
class Info(object):
    def __init__(self, tag=None):
        if tag:
            self.title = tag.get("title1", default=False)
            self.subtitle = tag.get("title2", default=False)
            #self.thumb = tag.get("thumb").replace('=','%3D') # TODO: default plex image if thumb not found?
            self.mixedParents = tag.get("mixedParents", default=False)
        else:
            self.title = False
            self.subtitle = False
            self.mixedParents = False

# Directory class: contains select keys from various Directory and Video tags
class Directory(object):
    def __init__(self, tag, **kwargs):
        self.title = tag.get("title").encode('ascii', 'xmlcharrefreplace')
        key = tag.get("key")
        if not key.startswith("/") and kwargs.get('prefix') != None:
            self.key = kwargs.get('prefix').split("?",1)[0] + "/" + key
        else:
            self.key = key
        self.type = "directory"