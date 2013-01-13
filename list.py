import cPickle
import sys
import requests

RESULTS_LIMIT = 5

class Item:

    def __init__(self, title):
        self.title = title
        self.ident, self.details = None, None

    #---------------------------------
    # subclasses must implement these methods
    def title_to_ids(self):
        '''Using self.title as a search term, return a list of unique IDs that may be our item'''
        pass

    def id_to_info(self):
        '''Return metadata details for item with ID self.ident.
        We assume that if we have a valid ID we can find info'''
        pass

    def info_to_title(self):
        '''Return just the title from self.details'''
        pass
    #---------------------------------

    def standardize(self):
        '''Given a search term, fetch a list of possible results using title_to_ids() and let the user pick one.
        If an item is successfully picked, fetch the metadata for that item'''
        id_l = self.title_to_ids()
        if id_l == []:
            print "No results found. Try adding another item"
            return -1
        for ident in id_l:
            # set metadata as if this is the correct item (item will be discarded if user doesn't choose it anyway)
            self.ident = ident
            self.details = self.id_to_info()
            self.title = self.info_to_title()
            q = raw_input('{}. Is this correct? (y/n) '.format(self))
            if q == 'y': # metadata was already set, we can exit
                break
        if q != 'y': # we went through all the results and user didn't choose one
            print "No candidates were satisfactory. Try adding another item"
            return -1

class Movie(Item):

    #
    # use omdbapi to gather data
    #
    def title_to_ids(self):
        p = {'s' : self.title}
        r = requests.get("http://www.omdbapi.com", params=p)
        if 'Error' in r.json():
            return []
        else:
            return [result['imdbID'] for result in r.json()['Search'][0:RESULTS_LIMIT]]

    def id_to_info(self):
        p = {'i' : self.ident}
        r = requests.get("http://www.omdbapi.com", params=p)
        return r.json()

    def info_to_title(self):
        return self.details['Title']

    def __repr__(self):
        # "Up" (2009)
        return "\"{}\" ({})".format(self.title, self.details['Year'])

class Book(Item):

    def api_key(self):
        try:
            with open("my_google_api_key",'r') as f:
                return f.readline()
        except IOError:
            print "Google API key not found!"
            sys.exit()

    #
    # use the google books API to gather data
    #
    def title_to_ids(self):
        p = {'q' : self.title, 'key' : self.api_key(), 'printType' : 'books', 'langRestrict': 'en', 'maxResults' : RESULTS_LIMIT}
        r = requests.get("https://www.googleapis.com/books/v1/volumes", params=p)
        if 'items' not in r.json():
            return []
        else:
            return [result['id'] for result in r.json()['items']]
            #return [result['volumeInfo']['industryIdentifiers'][0]['identifier'] for result in r.json()['items']]

    def id_to_info(self):
        #p = {'q' : '+isbn:{}'.format(self.ident), 'key' : self.api_key(), 'printType': 'books', 'langRestrict': 'en', 'maxResults' : RESULTS_LIMIT}
        #r = requests.get("https://www.googleapis.com/books/v1/volumes", params=p)
        p = {'key' : self.api_key(), 'printType': 'books', 'langRestrict': 'en', 'maxResults' : RESULTS_LIMIT}
        r = requests.get("https://www.googleapis.com/books/v1/volumes/{}".format(self.ident), params=p)
        #return r.json()['items'][0]
        return r.json()

    def info_to_title(self):
        return self.details['volumeInfo']['title']

    def __repr__(self):
        # "Animal Farm" (George Orwell)
        return "\"{}\" ({})".format(self.title, self.details['volumeInfo']['authors'][0])

class Album(Item):

    #
    # use iTunes API to gather data
    #
    def title_to_ids(self):
        p = {'term' : self.title, 'media' : 'music', 'entity' : 'album', 'attribute' : 'albumTerm', 'limit' : RESULTS_LIMIT}
        r = requests.get("https://itunes.apple.com/search", params=p)
        if r.json()['resultCount'] == 0:
            return []
        else:
            return [result['collectionId'] for result in r.json()['results']]

    def id_to_info(self):
        p = {'id' : self.ident}
        r = requests.get("https://itunes.apple.com/lookup", params=p)
        return r.json()['results'][0]

    def info_to_title(self):
        return self.details['collectionName']

    def __repr__(self):
        # "Make Believe" - Weezer (2005)
        return "\"{}\" - {} ({})".format(self.title, self.details['artistName'], self.details['releaseDate'][0:4])
        
class List:
    
    def __init__(self, name, item_type):
        self.name = name
        self.items = []
        self.item_type = item_type # item type

    def add(self):
        '''Add a media item to the list. We use Item.standardize() to pick the right one'''
        print "Adding to list \"{}\" (media type: {})".format(self.name, self.item_type.__name__)
        title = raw_input("Enter title of item: ")
        item = self.item_type(title)
        if item.standardize() != -1: # make sure user picked an item before adding it
            self.items.append(item)

    def modify(self):
        '''Replace an existing media item by fetching another'''

    def __repr__(self):
        ret = ""
        ret += "{}, (media type: {})\n".format(self.name, self.item_type.__name__)
        ret += '----------------------\n'
        for i in self.items:
            ret += str(i) + '\n'
        ret += '----------------------\n'
        return ret


class Collection():
    
    def __init__(self):
        # set up media lists (used later)
        self.media_l = [Movie, Book, Album]
        self.media_d = {} # {'m' : Movie, 'b' : Book, ...}
        for m in self.media_l:
            self.media_d[m.__name__[0].lower()] = m

        name = raw_input("Enter name of collection: ")
        try: # load collection if it already exists
            self.load(name)
            print "Collection {} found, loading from save".format(name)
        except IOError:
            print "Creating new collection \"{}\"".format(name)
            self.name = name
            self.lists = []
        self.cur_list = 0

    def add_list(self):
        '''Add a list of media items. All items in list have the same media type.'''
        list_type = '-1'
        # make our nice media type string "(m)ovie, (b)ook, ..."
        media_str = ', '.join(["({}){}".format(k, self.media_d[k].__name__[1:]) for k in self.media_d.keys()])

        while list_type not in self.media_d.keys():
            list_type = raw_input("Enter list type - {}: ".format(media_str))
        list_name = raw_input("Enter list name: ")
        self.lists.append(List(list_name, self.media_d[list_type]))
        # switch to the new list (user probably wanted to add item to this list)
        self.cur_list = len(self.lists) - 1
        print "Switched current list to new list \"{}\"".format(list_name)

    def switch_list(self):
        '''Change the active media list.'''
        if self.lists == []:
            print "Add a list first."
            return -1
        choices_str = ''
        for i in range(len(self.lists)):
            choices_str += self.lists[i].name + '({}) '.format(i)
        i = -1
        while not (0 <= i < len(self.lists)):
            i = input("Which list to make active? {}".format(choices_str))
        self.cur_list = i
        
    def add_item(self):
        '''Add a media item to a media list.'''
        if self.lists == []:
            print "Add a list first."
            return -1
        self.lists[self.cur_list].add()

    def exit(self):
        '''saves collection and exits'''
        def save():
            with open(self.name + ".pkl", 'w') as f:
                cPickle.dump(self.lists, f)
        save()
        sys.exit()


    def load(self, name):
        '''Given a name, load a collection of that name'''
        with open(name + ".pkl", 'r') as f:
            self.name = name
            self.lists = cPickle.load(f)

    def __repr__(self):
        return ''.join([str(l) for l in self.lists])

