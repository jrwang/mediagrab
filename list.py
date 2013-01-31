from statistics import *

import cPickle
import sys
import requests
import cmd
from copy import deepcopy
from collections import Counter, defaultdict
from datetime import *

#TODO: are multi-disc albums handled correctly?
#TODO: make config file

RESULTS_LIMIT = 5
N = 5
CAT_N = 3


class Item:

    def __init__(self, title):
        self.title = title
        self.ident, self.details, self.star = None, None, False

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
    
    def statistics(self, item_type):
        '''Prints statistics for a list of items of the specified type'''
        pass
    #---------------------------------

    def standardize(self):
        '''Given a search term, fetch a list of possible results using title_to_ids() and let the user pick one.
        If an item is successfully picked, fetch the metadata for that item'''
        id_l = self.title_to_ids()
        if id_l == []:
            print "No results found. Try using a different title search."
            return None
        for ident in id_l:
            # set metadata as if this is the correct item (item is discarded if not chosen)
            self.ident = ident
            self.details = self.id_to_info()
            self.title = self.info_to_title()
            q = raw_input('{}. Is this correct? (y/n) '.format(self))
            if q == 'y': # metadata was already set, we can exit
                return True
        # we went through all the results and user didn't choose one
        print "No candidates were satisfactory. Try adding another item or searching using a different title."
        return None

class Movie(Item):

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

    def give_details(self):
        ret = {}
        keys = ['Rated', 'Title', 'Actors', 'Year', 'Genre', 'Runtime', 'imdbRating']
        for k in keys:
            ret[k] = self.details[k]
        return ret
            
    def statistics(self, movie_details):
        print "Count: {}".format(len(movie_details))
        top_rat = Counter([m['Rated'] for m in movie_details])
        print "Top {} ratings: {}".format(CAT_N, counter_top(top_rat, CAT_N))

        top_years = Counter([m['Year'] for m in movie_details])
        print "Top {} years: {}".format(CAT_N, counter_top(top_years, CAT_N))
        
        # little complicated here since we want the movies each actor was in
        top_actors = Counter()
        actor_movie_d = defaultdict(list)
        for actors, movie in [(m['Actors'], m['Title']) for m in movie_details]:
            for act in actors.split(', '):
                actor_movie_d[act].append(movie)
                top_actors.update([act])
        top_act_str = ''
        for act, count in top_actors.most_common(CAT_N):
            top_act_str += '{} - {} ({}), '.format(act, count, ', '.join(actor_movie_d[act]))
        print "Top {} actors: {}".format(CAT_N, top_act_str[:-2])

        top_genres = Counter(reduce(lambda a,b: a+b, [m['Genre'].split(', ') for m in movie_details]))
        print "Top {} genres: {}".format(CAT_N, counter_top(top_genres, CAT_N))

        total_t = timedelta()
        for m in movie_details:
            h, m = movie_details[0]['Runtime'].encode('ascii').strip(' min').split(' h ')
            total_t +=  timedelta(hours=int(h), minutes=int(m))
        days, hours, minutes = total_t.days, total_t.seconds/3600, (total_t.seconds/60) % 60
        print "Total runtime: {} days, {} hours, {} minutes".format(days, hours, minutes)

        ratings = [float(m['imdbRating']) for m in movie_details]
        print "Average IMDB rating: {:.2f}".format(sum(ratings)/len(ratings))
        print "-----------------------------"

    def __repr__(self):
        # "Up" (2009)
        star = '*' if self.star else ''
        return "\"{}\" ({}){}".format(self.title, self.details['Year'], star)

class Book(Item):

    def api_key(self):
        try:
            with open("my_google_api_key",'r') as f:
                return f.readline()
        except IOError:
            print "Google API key not found!"
            sys.exit()

    def title_to_ids(self):
        p = {'q' : self.title, 'key' : self.api_key(), 'printType' : 'books', 'langRestrict': 'en', 'maxResults' : RESULTS_LIMIT}
        r = requests.get("https://www.googleapis.com/books/v1/volumes", params=p)
        if 'items' not in r.json():
            return []
        else:
            return [result['id'] for result in r.json()['items']]

    def id_to_info(self):
        p = {'key' : self.api_key(), 'printType': 'books', 'langRestrict': 'en', 'maxResults' : RESULTS_LIMIT}
        r = requests.get("https://www.googleapis.com/books/v1/volumes/{}".format(self.ident), params=p)
        return r.json()

    def info_to_title(self):
        return self.details['volumeInfo']['title']

    def give_details(self):
        def try_lookup(d, *keys):
            '''Try a nested lookup. Return default value (None) if any part of lookup fails'''
            for k in keys:
                try:
                    d = d[k]
                except KeyError:
                    return None
            return d

        keys = { 
            'retailPrice': ['saleInfo', 'retailPrice', 'amount'], 
            'listPrice': ['saleInfo', 'listPrice', 'amount'], 
            'publishedDate': ['volumeInfo', 'publishedDate'], 
            'pageCount': ['volumeInfo', 'pageCount'], 
            'thickness': ['volumeInfo', 'dimensions', 'thickness'], 
            'authors': ['volumeInfo', 'authors', 0], 
            'title': ['volumeInfo', 'title'], 
            'averageRating': ['volumeInfo', 'averageRating'], 
            'categories': ['volumeInfo', 'categories', 0] 
        }
        return {k : try_lookup(self.details, *keys[k]) for k in keys}

    def statistics(self, book_details):
        print "Count: {}".format(len(book_details))
        print "Total cost (est.): ${:.2f}".format(sum_with_sub([b['listPrice'] for b in book_details])) # since "retail price" is for ebook
        print "Total pages (est.): {}".format(int(sum_with_sub([b['pageCount'] for b in book_details])))

        top_auth = Counter([b['authors'] for b in book_details])
        print "Top {} authors: {}".format(N, counter_top(top_auth, N))

        categories = []
        for b in book_details:
            if b['categories']:
                categories += b['categories'].split(' / ')
        print "Top {} genres: {}".format(CAT_N, counter_top(Counter(categories), CAT_N))

        ratings = filter(lambda x: x is not None, [b['averageRating'] for b in book_details])
        print "Average book rating (out of 5): {:.2f}".format(float(sum(ratings))/len(ratings))

        height_l = []
        for b in book_details:
            if b['thickness'] is not None:
                height_l.append(float(b['thickness'].strip(' cm').encode('ascii')))
            else:
                height_l.append(None)
        print "Height of books if stacked (est.): {} cm".format(sum_with_sub(height_l))
        print "-----------------------------"

    def __repr__(self):
        # "Animal Farm" - George Orwell
        star = '*' if self.star else ''
        return "\"{}\" - {}{}".format(self.title, self.details['volumeInfo']['authors'][0], star)

class Album(Item):

    def title_to_ids(self):
        p = {'term' : self.title, 'media' : 'music', 'entity' : 'album', 'attribute' : 'albumTerm', 'limit' : RESULTS_LIMIT}
        r = requests.get("https://itunes.apple.com/search", params=p)
        if r.json()['resultCount'] == 0:
            return []
        else:
            return [result['collectionId'] for result in r.json()['results']]

    def id_to_info(self):
        p = {'id' : self.ident, 'entity': 'song'}
        r = requests.get("https://itunes.apple.com/lookup", params=p)
        return r.json()['results']

    def info_to_title(self):
        return self.details['collectionName']

    def give_details(self):
        keys = ['trackCount', 'artistName', 'collectionName', 'releaseDate', 'primaryGenreName', 'collectionPrice']
        ret = {k : self.details[0][k] for k in keys}
        # get track details (list of dicts, each dict a subset of the track dicts in self.details)
        track_keys = ['trackId', 'trackName', 'discNumber', 'trackNumber', 'trackTimeMillis']
        ret['trackDetails'] = [{k : track[k] for k in track_keys} for track in self.details[1:]] # first is album info
        return ret

    def statistics(self, album_details):
        print "Total albums: {}".format(len(album_details))
        print "Total tracks: {}".format(sum([a['trackCount'] for a in album_details]))

        top_genres = Counter([a['primaryGenreName'] for a in album_details])
        print "Top {} genres: {}".format(CAT_N, counter_top(top_genres, CAT_N))

        print "Total cost (iTunes): ${}".format(sum([a['collectionPrice'] for a in album_details]))

        date_l = []
        for date in [a['releaseDate'] for a in album_details]:
            date_l.append(datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ'))
        years = [date.year for date in date_l] 
        avg_year = sum(years)/len(years) # just naively average years (integer division is fine)
        print "Average year: {}".format(avg_year)

        total_ms = sum([t['trackTimeMillis'] for t in a['trackDetails'] for a in album_details])
        total_t = timedelta(milliseconds=total_ms)
        days, hours, minutes = total_t.days, total_t.seconds/3600, (total_t.seconds/60) % 60
        print "Total time: {} days, {} hours, {} minutes".format(days, hours, minutes)
        print "-----------------------------"

    def __repr__(self):
        # "Make Believe" - Weezer (2005)
        star = '*' if self.star else ''
        return "\"{}\" - {} ({}){}".format(self.title, self.details[0]['artistName'], self.details[0]['releaseDate'][0:4], star)
        
class List:
    
    def __init__(self, name, item_type):
        self.name = name
        self.items = []
        self.item_type = item_type # item type

    def add(self, title):
        '''Add a media item to the list. We use Item.standardize() to pick the right one'''
        print "Adding to list \"{}\" (media type: {})".format(self.name, self.item_type.__name__)
        item = self.item_type(title)
        if item.standardize(): # make sure user picked an item 
            self.items.append(item)

    def statistics(self):
        print "{}, (media type: {})\n".format(self.name, self.item_type.__name__)
        self.item_type.statistics(self.item_type(''), [item.give_details() for item in self.items])

    def __repr__(self):
        ret = '---------------------------------\n'
        ret += "{}, (media type: {})\n\n".format(self.name, self.item_type.__name__)
        for i in self.items:
            ret += str(i) + '\n'
        ret += '---------------------------------\n'
        return ret


class Collection(cmd.Cmd):
    
    def __init__(self, name):
        cmd.Cmd.__init__(self)
        self.media_l = [Movie, Book, Album] # our allowed media types
        self.media_d = {m.__name__[0].lower() : m for m in self.media_l} # {'m' : Movie, 'b' : Book, ...}
        try: # load collection if it already exists
            self.load(name)
            print "Collection \"{}\" found, loading from save".format(name)
            self.do_switch_list(self.lists[self.cur_list].name)
        except IOError:
            print "Couldn't find collection \"{}\", creating new collection".format(name)
            self.name = name
            self.lists = []

    def do_add_list(self, list_name):
        '''Add a list of media items. All items in list have the same media type. Usage: "add_list (<list_name>)"'''
        #list_name = raw_input("Enter list name: ")

        if list_name in [l.name for l in self.lists]:
            print "A list called \"{}\" already exists!".format(list_name)
            return -1
        elif list_name == '':
            list_name = raw_input("Enter list name: ")

        list_type = None
        # make our nice media type string "(m)ovie, (b)ook, ..."
        media_str = ', '.join(["({}){}".format(k, self.media_d[k].__name__[1:]) for k in self.media_d.keys()])

        while list_type not in self.media_d.keys():
            list_type = raw_input("Enter list type - {}: ".format(media_str))
        self.lists.append(List(list_name, self.media_d[list_type]))
        # switch to the new list (user probably wanted to add item to this list)
        self.do_switch_list(list_name)
        print "Switched current list to new list \"{}\"".format(list_name)

    def do_switch_list(self, list_name):
        '''Change the active media list. Usage: "switch_list (<list_name>)"'''
        if list_name == '':
            list_name = raw_input("Switch to which list? ")
        if self.lists == []:
            print "Couldn't find any media lists. Add a list first (\"add_list\")."
            return -1

        found = False
        for i in range(len(self.lists)):
            if list_name == self.lists[i].name:
                found = True
                self.cur_list = i # list names can't be duplicated, so it's fine to finish the loop
        if not found:
            print "Couldn't find list \"{}\"".format(list_name)
            return -1
        # change name to reflect which list we're currently in
        if self.prompt == "(Cmd) ": # initialize
            self.prompt = self.prompt[:-2] + ':' + self.lists[self.cur_list].name + ') '
        else:
            self.prompt = self.prompt.split(':')[0] + ':' + self.lists[self.cur_list].name + ') '
        
    def do_add_item(self, line):
        '''Add a media item to a media list. Usage: "add_item (<item_name>)" to add to the active media list or "add_item (<list_name> <item_name>)" to add to any list.'''
        if self.lists == []:
            print "Couldn't find any media lists. Add a list first (\"add_list\")."
            return -1
        args = line.split()
        if len(args) == 0:
            title = raw_input('Enter item name: ')
        elif len(args) == 1:
            title = args[0]
        else:
            # "add_item list_name title"
            if self.do_switch_list(args[0]) != -1:
                title = ' '.join(args[1:])
            # "add_item title possibly in several words"
            else:
                title = ' '.join(args)
        self.lists[self.cur_list].add(title)

    def do_summary(self, line):
        '''Prints a summary of all lists and their items. Usage: "summary"'''
        print self

    def do_EOF(self, line):
        '''Saves, then exits. (Overrides Ctrl+D)'''
        s = raw_input("Save before exiting? (y/n) ")
        if s == 'y':
            self.do_save('')
        return True

    def do_toggle_star(self, title):
        '''Toggle an item between star/unstarred. Usage: "toggle_star (<item_name>)"'''
        if title == '':
            title = raw_input("Which item to star/unstar? ")
        desc, i, j = self.find(title)
        if desc:
            if self.lists[i].items[j].star:
                print "Unstarred {}.".format(desc)
            else:
                print "Starred {}.".format(desc)
            self.lists[i].items[j].star = not self.lists[i].items[j].star

    def do_remove(self, title):
        '''Delete an item completely from a list. Usage: "remove (<item_name>)"'''
        if title == '':
            title = raw_input("Which item to remove? ")
        desc, i, j = self.find(title)
        if desc:
            q = raw_input("Sure you want to delete {}? (y/n) ".format(desc))
            if q == 'y':
                del self.lists[i].items[j]
                print "Deleted {}.".format(desc)
            else:
                print "Leaving {} alone.".format(desc)
        
    def do_modify(self, title):
        '''Modify an item's title, refetching all metadata. Usage: "modify (<item_name>)"'''
        if title == '':
            title = raw_input("Modify which item: ")
        desc, i, j = self.find(title)
        if desc:
            print "Modifying {}".format(desc)
            new_title = raw_input("Enter new title: ")
            item = self.lists[i].items[j]
            backup = deepcopy(item)
            item.title = new_title
            # if user didn't like the choices, revert to original
            if not item.standardize():
                print "Leaving {} alone.".format(desc)
                item = backup

    def do_save(self, line):
        '''Saves collection. Usage: "save"'''
        # back these up
        stdin, stdout = self.__dict__['stdin'], self.__dict__['stdout']
        del self.__dict__['stdin']
        del self.__dict__['stdout']
        with open(self.name + ".pkl", 'w') as f:
            cPickle.dump(self.__dict__, f)
        # now restore them
        self.__dict__['stdin'], self.__dict__['stdout'] = stdin, stdout

    def do_details(self, title):
        '''Displays the details for a particular item. Usage: "details (<item_name>)'''
        if title == '':
            title = raw_input("Details for which item: ")
        item, i, j = self.find(title)
        if item:
            print self.lists[i].items[j].give_details()

    def do_statistics(self, line):
        '''Prints statistics for every list in the collection. Usage: "statistics"'''
        print "---------STATISTICS----------"
        for l in self.lists:
            l.statistics()

    def find(self, title):
        '''Given a search string, first finds all the items that match that search string (exact substring match).
        Then gets user to pick just one of those items and returns (item, item_description)'''
        res = []
        for i in range(len(self.lists)):
            for j in range(len(self.lists[i].items)):
                if title.lower() in self.lists[i].items[j].title.lower():
                    res += [("{} from list \"{}\"".format(self.lists[i].items[j], self.lists[i].name), i, j)]
        # if only one search result, we can just assume it's right
        if len(res) == 1:
            return res[0]
        else:
            for desc, i, j in res:
                q = raw_input("Perform this operation on {}? (y/n) ".format(desc))
                if q == 'y': 
                    return desc, i, j
        # if we're still here, no results were satisfactory!
        print "Couldn't find item \"{}\" (has to match exactly). Try searching again.".format(title)
        return None, None, None

    def load(self, name):
        '''Given a name, load a collection of that name'''
        with open(name + ".pkl", 'r') as f:
            self.__dict__ = cPickle.load(f)
            self.__dict__['stdin'], self.__dict__['stdout'] = sys.stdin, sys.stdout

    def __repr__(self):
        return ''.join([str(l) for l in self.lists])


if __name__ == '__main__':
    # "python list.py"
    if len(sys.argv) == 1:
        name = raw_input("Enter name of collection: ")
        c = Collection(name).cmdloop()
    # "python list.py collection_name"
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        c = Collection(name).cmdloop()
    # "python list.py collection_name some_commands"
    else:
        name = sys.argv[1]
        c = Collection(name)
        cmd.Cmd.onecmd(c, ' '.join(sys.argv[2:]))
        c.do_save('') # if we entered a one-liner, we want to save



