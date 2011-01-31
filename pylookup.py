#!/usr/bin/env python

"""
Pylookup is to lookup entries from python documentation, especially within
emacs. Pylookup adopts most of ideas from haddoc, lovely toolkit by Martin
Blais.

(usage)
  ./pylookup.py -l ljust
  ./pylookup.py -u http://docs.python.org
  
"""

import sys
import re
import pickle
import urllib
import urlparse
import htmllib
import formatter

from os.path import join, dirname, exists, abspath, expanduser
from contextlib import closing

FORMATS = {
             "Emacs" : "{entry}\t({desc})\t[{book}];{url}",
             "Terminal" : "{entry}\t({desc})\t[{book}]\n{url}"
           }

def build_book(s, num):
    """
    Build book identifier from `s`, with `num` links.
    """
    for matcher, replacement in (("library", "lib"),
                                ("c-api", "api"),
                                ("reference", "ref"),
                                ("", "etc")):
        if matcher in s:
            return replacement if num == 1 else "%s/%d" % (replacement, num)

def trim(s):
    """
    Add any globle filtering rules here
    """
    s = s.replace( "Python Enhancement Proposals!", "")
    s = s.replace( "PEP ", "PEP-")
    return s

class Element(object):
    def __init__(self, entry, desc, book, url):
        self.book = book
        self.url = url
        self.desc = desc
        self.entry = entry

    def __format__(self, format_spec):
        return format_spec.format(entry=self.entry, desc=self.desc,
                                  book=self.book, url=self.url)

    def match_insensitive(self, key):
        """
        Match key case insensitive against entry.

        `key` : Lowercase string.
        """
        return key in self.entry.lower() or key in self.desc.lower()

    def match_sensitive(self, key):
        """
        Match key case sensitive against entry.

        `key` : Lowercase string.
        """
        return key in self.entry or key in self.desc

class IndexProcessor( htmllib.HTMLParser ):
    """
    Extract the index links from a Python HTML documentation index.
    """
    
    def __init__( self, writer, dirn):
        htmllib.HTMLParser.__init__( self, formatter.NullFormatter() )
        
        self.writer     = writer
        self.dirn       = dirn
        self.entry      = ""
        self.desc       = ""
        self.do_entry   = False
        self.one_entry  = False
        self.num_of_a   = 0

    def start_dd( self, att ):
        self.list_entry = True

    def end_dd( self ):
        self.list_entry = False

    def start_dt( self, att ):
        self.one_entry = True
        self.num_of_a  = 0

    def end_dt( self ):
        self.do_entry = False
        
    def start_a( self, att ):
        if self.one_entry:
            self.url = join( self.dirn, dict( att )[ 'href' ] )
            self.save_bgn()

    def end_a( self ):
        if self.one_entry:
            if self.num_of_a == 0 :
                self.desc = self.save_end()

                # extract fist element
                #  ex) __and__() (in module operator)
                if not self.list_entry :
                    self.entry = re.sub( "\([^)]+\)", "", self.desc )
                    
                    # clean up PEP
                    self.entry = trim(self.entry)
                    
                    match = re.search( "\([^)]+\)", self.desc )
                    if match :
                        self.desc = match.group(0)
                        
                self.desc = trim(re.sub( "[()]", "", self.desc ))

            self.num_of_a += 1
            book = build_book(self.url, self.num_of_a)
            e = Element(self.entry, self.desc, book, self.url)

            self.writer(e)

def update(db, urls, append=False):
    """Update database with entries from urls.

    `db` : filename to database
    `urls` : list of URL 
    `append` : append to db
    """
    mode = "ab" if append else "wb"
    with open(db, mode) as f:
        writer = lambda e: pickle.dump(e, f)
        for url in urls:
            parsed = urlparse.urlparse(url)
            if not parsed.scheme or parsed.scheme == "file":
                url = "file://%s" % abspath(expanduser(parsed.path))
            else:
                url = parsed.geturl()
            url = url.rstrip("/") + "/"
            print "Wait for a few seconds ..\nFetching htmls from '%s'" % url
            try:
                index = urllib.urlopen(url + "genindex-all.html").read()
                parser = IndexProcessor(writer, dirname(url))
                with closing(parser):
                    parser.feed(index)
            except IOError, e:
                print "Error: fetching file from the web: '%s'" % e

def lookup(db, key, format_spec, out=sys.stdout, insensitive=True):
    """Lookup key from database and print to out.
    
    `db` : filename to database
    `key` : key to lookup
    `out` : file-like to write to
    `insensitive` : lookup key case insensitive
    """
    if insensitive:
        matcher = Element.match_insensitive
        key = key.lower()
    else:
        matcher = Element.match_sensitive
                                             
    with open(db, "rb") as f:
        try:
            while True:
                e = pickle.load(f)
                if matcher(e, key):
                    print >> out, format(e, format_spec)
        except EOFError:
            pass

def cache(db, out=sys.stdout):
    """Print unique entries from db to out.

    `db` : filename to database
    `out` : file-like to write to
    """
    with open(db, "rb") as f:
        keys = set()
        try:
            while True:
                e = pickle.load(f)
                k = e.entry
                k = re.sub( "\([^)]*\)", "", k )
                k = re.sub( "\[[^]]*\]", "", k )
                keys.add(k)
        except EOFError:
            pass
        for k in keys:
            print >> out, k

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser( __doc__.strip() )
    
    parser.add_option( "-d", "--db", 
                       help="database name", 
                       dest="db", default="pylookup.db" )
    parser.add_option( "-l", "--lookup", 
                       help="keyword to search", 
                       dest="key" )
    parser.add_option( "-u", "--update",
                       help="update url or path",
                       action="append", type="str", dest="url" )
    parser.add_option( "-c", "--cache" , 
                       help="extract keywords, internally used",
                       action="store_true", default=False, dest="cache")
    parser.add_option( "-a", "--append", 
                       help="append to the db from multiple sources",
                       action="store_true", default=False, dest="append")
    parser.add_option( "-f", "--format",
                       help="type of output formatting, valid: Emacs, Terminal",
                       choices=["Emacs", "Terminal"],
                       default="Terminal", dest="format")

    ( opts, args ) = parser.parse_args()

    if opts.url:
        update(opts.db, opts.url, opts.append)
        
    if opts.cache:
        cache(opts.db)

    if opts.key:
        lookup(opts.db, opts.key, FORMATS[opts.format])
