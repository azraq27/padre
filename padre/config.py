'''Standard directory and filename locations are stored in the :class:`padre.config` class, and imported
to the root level for convenience.
'''

import os

verbose = True

padre_root = os.path.dirname(os.path.abspath(__file__ + '/..')) #: Root directory of repository
data_dir = os.path.join(padre_root,'Data') #: [padre_root]/Data
analyses_dir = os.path.join(padre_root,'Analyses') #: [padre_root]/Analyses

def subject_dir(subject):
	'''returns subject directory for given subject'''
	return os.path.join(data_dir,str(subject))

def raw_subject_dir(subject):
	'''[subject_dir]/raw'''
	return os.path.join(subject_dir(subject),'raw')

def sessions_subject_dir(subject):
	'''[subject_dir]/sessions'''
	return os.path.join(subject_dir(subject),'sessions')

def subject_json(subject):
	''' location of subject's JSON file '''
	return os.path.join(subject_dir(subject),'%s.json' % subject)