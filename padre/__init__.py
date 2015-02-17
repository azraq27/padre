'''PaDRe -- Patient Data Repository

Library to organize participant imaging data'''

version = 2.3

_global_experiment = None
_include_all = False

from config import *

import sys
def error(msg):
	sys.stderr.write('## PaDRe Error: %s\n' % msg.strip())
	sys.stderr.flush()

import subject
from subject import Subject,subjects
import maint

from forgiving_dict import ForgivingDict

def load(s):
    return Subject.load(s)

def set_experiment(exp):
    global _global_experiment
    _global_experiment = exp