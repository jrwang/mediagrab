
#MediaGrab

MediaGrab easily creates organized lists of books, albums or movies. Once given the title of the work, MediaGrab will grab the full metadata for that item. The currently supported media types are albums, books, and movies (classes "Album," "Book," and "Movie" respectively). 

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
## Using MediaGrab
```bash
python -i list.py
>>> c = Collection()
Enter name of collection: Book & Movie Club 2000
Creating new collection "Book & Movie Club 2000"
>>> c = Collection()
Enter name of collection: Book & Movie Club - 2012
Creating new collection "Book & Movie Club - 2012"
>>> c.add_list()
Enter list type - (a)lbum, (b)ook, (m)ovie: b
Enter list name: books
Switched current list to new list "books"
>>> c.add_item()
Adding to list "books" (media type: Book)
Enter title of item: harry potter
"Harry Potter and the Goblet of Fire" (J.K. Rowling). Is this correct? (y/n) y
>>> c.add_list()
Enter list type - (a)lbum, (b)ook, (m)ovie: m
Enter list name: movies
Switched current list to new list "movies"
>>> c.add_item()
Adding to list "movies" (media type: Movie)
Enter title of item: harry potter
"Harry Potter and the Sorcerer's Stone" (2001). Is this correct? (y/n) y
>>> c.switch_list()
Which list to make active? books(0) movies(1) 0
>>> c.add_item()
Adding to list "books" (media type: Book)
Enter title of item: game of thrones
"A Game of Thrones" (George R.R. Martin). Is this correct? (y/n) y
>>> c
books, (media type: Book)
----------------------
"Harry Potter and the Goblet of Fire" (J.K. Rowling)
"A Game of Thrones" (George R.R. Martin)
----------------------
movies, (media type: Movie)
----------------------
"Harry Potter and the Sorcerer's Stone" (2001)
----------------------
>>> c.exit()

```

