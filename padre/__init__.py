'''PaDRe -- Patient Data Repository

Library to organize patient imaging data'''

version = 0.3

from config import *

import sys
def error(msg):
	sys.stderr.write('## EpiLib Error: %s\n' % msg.strip())
	sys.stderr.flush()

import subject
from subject import Subject,subjects

def load(s):
    return Subject.load(s)