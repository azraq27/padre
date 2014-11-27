'''PaDRe -- Patient Data Repository

Library to organize patient imaging data'''

version = 2.0

_global_experiment = None

from config import *

import sys
def error(msg):
	sys.stderr.write('## PaDRe Error: %s\n' % msg.strip())
	sys.stderr.flush()

import subject
from subject import Subject,subjects

from forgiving_dict import ForgivingDict

def load(s):
    return Subject.load(s)

def set_experiment(exp):
    global _global_experiment
    _global_experiment = exp