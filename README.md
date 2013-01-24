
#MediaGrab

MediaGrab easily creates organized lists of books, albums or movies. Once given the title of the work, MediaGrab will grab the full metadata for that item. Then you can see information about groups of items at a glance, and even get cool aggregate statistics. This can be used to keep track of books you read last year, or movies you want to see, or your personal CD collection.

The currently supported media types are albums, books, and movies (classes "Album," "Book," and "Movie" respectively). 

## Getting Started

### Install requests

If you have pip installed:
```bash
pip install requests
```

If not: 
```bash
easy_install requests
```
### Get API keys

You'll need a Google API Key, which you can get here: https://developers.google.com/books/docs/v1/using#APIKey

Save that in a file named "my_google_api_key" in the mediaGrab directory. Now you're ready to start!

## Using MediaGrab
It's as easy as: 

```bash
python list.py
(Cmd) help
```

You can also load an existing collection: 

```bash
python list.py media_of_2012
```

You can also do one-liners instead of entering the interactive shell: 

```bash
python list.py media_of_2012 statistics
(Cmd) help
```
