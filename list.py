#!/usr/bin/env python
import cPickle
import sys
import cmd
from copy import deepcopy
from datetime import *

from media import *
import grab


#TODO: add other methods of adding, e.g. discs through mediamonkey
#TODO: do not allow duplicates
#TODO: are multi-disc albums handled correctly?
#TODO: make config file
#TODO: "python list.py future add_item men in black 3" fails

class List:
    
    def __init__(self, name, item_type):
        self.name = name
        self.items = []
        self.item_type = item_type # item type

    def add(self, title):
        '''Add a media item to the list. We use Item.standardize() to pick the right one.'''
        print "Adding \"{}\" to list \"{}\" (media type: {})".format(title, self.name, self.item_type.__name__)
        # allow users to add a star in input
        starred = False
        if title.endswith('*'):
            title = title.rstrip('*')
            starred = True
        item = self.item_type(title)
        if item.standardize(): # make sure user picked an item 
            item.star = starred
            self.items.append(item)

    def add_mb(self, title):
        item = Album('')
        item.mb_shit(title)
        self.items.append(item)

    def get(self):
        '''Get first undownloaded item of list'''
        for item in self.items:
            if item.dl != 1:
                grab.grab(item)
                break # grab first only

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
        '''Add a media item to a media list. Usage: "add_item (<item_name>)" to add to the active media list or "add_item (<list_name> <item_name>)" to add to any list. If there is a trailing asterisk (*), the item will be starred.'''
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

    def do_add_mb(self, line):
        '''BAD BAD BAD - for hacky music brainz items'''
        try:
            self.lists[self.cur_list].add_mb(line)
        except IOError:
            pass
            print e
            print e.args
            print 'yer fucked'

    def do_refresh_mb(self, line):
        for i in range(len(self.lists)):
            for j in range(len(self.lists[i].items)):
                item = self.lists[i].items[j]
                try:
                    item.mb_shit(item.mb)
                except:
                    pass
        

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

    def do_get(self, line):
        '''Get (download) the first media item from a list. Usage: "get" to use the active media list or "get <list_name>" to use a specfic media list'''
        if line:
            self.do_switch_list(line)
        self.lists[self.cur_list].get()
        print "Getting item {} from list {}".format(self.lists[self.cur_list].items[0], self.lists[self.cur_list].name)

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
        '''Given a collection name or a .pkl file, load a collection of that name'''
        if name.endswith(".pkl"): # treat .pkl files normally
            name.rstrip(".pkl")
        with open(name + ".pkl", 'r') as f:
            self.__dict__ = cPickle.load(f)
            self.__dict__['stdin'], self.__dict__['stdout'] = sys.stdin, sys.stdout

    def __repr__(self):
        return ''.join([str(l) for l in self.lists])

    def help_help(self):
        print 'show this help'


        


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



