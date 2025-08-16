import sys
import os

from main import HTMLParser, print_tree
from c2_Downloading_Web_Pages.browser import URL 

body = URL(sys.argv[1]).request()
#print(body)
nodes = HTMLParser(body).parse()
print_tree(nodes)