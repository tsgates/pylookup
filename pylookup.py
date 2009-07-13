#!/usr/bin/env python

"""
Pylookup is to lookup entries from python documentation, especially within emacs.
Pylookup adopts most of ideas from haddoc, lovely toolkit by Martin Blais.
"""

debug = False

import os, re, anydbm, urllib, htmllib, formatter
from os.path import join, dirname, exists

class IndexProcessor( htmllib.HTMLParser ):
    """
    Extract the index links from a Python HTML documentation index.
    """
    
    def __init__( self, db, dirn ):
        htmllib.HTMLParser.__init__( self, formatter.NullFormatter() )
        
        self.db         = db
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
                
                    match = re.search( "\([^)]+\)", self.desc )
                    
                    if match :
                        self.desc = match.group(0)
                        
                self.desc = re.sub( "[()]", "", self.desc )

            self.num_of_a += 1

            # book : reference[ref]/c-api[api]/library[lib]/other[etc]
            if self.url.find( "library" ) >= 0 :
                book = "lib"
            elif self.url.find( "c-api" ) >= 0 :
                book = "api"
            elif self.url.find( "reference" ) >= 0 :
                book = "ref"
            else :
                book = "etc"

            book = "[%s%s]" % ( book, "" if self.num_of_a == 1 else "/%d" % self.num_of_a )
            key = "%s\t(%s)\t%s" % ( self.entry , self.desc, book )

            if debug :
                print "%s : %s" % ( key, self.url )

            # store to db
            self.db[ key ] = self.url
        
if __name__ == "__main__":

    import optparse
    
    parser = optparse.OptionParser( __doc__.strip() )
    
    parser.add_option( "-d", "--db", dest="db", default="pylookup.db" )
    parser.add_option( "-l", "--lookup", dest="key" )
    parser.add_option( "-u", "--update", dest="url" )
    parser.add_option( "-c", "--cache", action="store_true", default=False, dest="cache")

    ( opts, args ) = parser.parse_args()

    # create db
    try:
        db = anydbm.open( opts.db, 'c' )
        
    except anydbm.error :
        raise SystemExit( "Error: Cannot access DB files" )

    # update
    if opts.url :

        # trim
        opts.url = opts.url if opts.url[-1] == "/" else opts.url + "/"

        print "Wait for a few second (Fetching htmls from '%s'" % opts.url

        try:
            index = urllib.urlopen( opts.url + "genindex-all.html" ).read()
        except IOError, e:
            raise SystemExit( "Error: fetching file from the web: '%s'" % e )
        
        parser = IndexProcessor( db, dirname( opts.url ) )
        
        parser.feed( index )
        parser.close()

    # cache
    if opts.cache :
        
        cache = []
        for key in db.keys() :
            key = re.sub( "\([^)]*\)", "", key )
            key = re.sub( "\[[^]]*\]", "", key )
            cache.append( key.strip() )

        # make it as unique
        print "\n".join( list( set( cache ) ) )

    # lookup
    if opts.key :

        keys = db.keys()
        
        results = []
        
        for term in opts.key.split() :
            results.extend( ( x, db[x] ) for x in
                            filter( re.compile( re.escape( term ), re.I ).search,
                                    keys) )
        
        results.sort()

        for key, url in results :
            print '%s;%s' % ( key, url )

    db.close()
