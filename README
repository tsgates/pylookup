<Author>

 Taesoo Kim (tsgatesv@gmail.com)

<README>

 Pylookup stollen idea from 'http://furius.ca/haddoc', one of my favorite 
 emacs mode for python documentation lookup. I reimplemented python code and 
 elisp code not just to support new version of python 2.6 but also to extend 
 it for other documentation lookup interface with easy. Importantly, pylookup 
 mode is much faster and support fancy highlighting.

 Please check, 
    Web  : http://taesoo.org/Opensource/Pylookup
    Repo : http://github.com/tsgates/pylookup

<INSTALL>

 ** [PATH] parameter totally depends on your environment, 
      ex) "~/.emacs.d/pylookup"

;; ======================================================================
;; add pylookup to your loadpath, ex) ~/.emacs.d/pylookup
(setq pylookup-dir "[PATH]")
(add-to-list 'load-path pylookup-dir)

;; load pylookup when compile time
(eval-when-compile (require 'pylookup))

;; set executable file and db file
(setq pylookup-program (concat pylookup-dir "/pylookup.py"))
(setq pylookup-db-file (concat pylookup-dir "/pylookup.db"))

;; to speedup, just load it on demand
(autoload 'pylookup-lookup "pylookup"
  "Lookup SEARCH-TERM in the Python HTML indexes." t)

(autoload 'pylookup-update "pylookup" 
  "Run pylookup-update and create the database at `pylookup-db-file'." t)
;;----------------------------------------------------------------------

<SEARCHING LOCAL HTML>

Index the database by yourself

1. download any versions of documents from 'http://docs.python.org'
2. indexing by typing './pylookup.py -u file:///home/... [absolute path]'
