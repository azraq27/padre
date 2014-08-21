'''Standard directory and filename locations are stored in the :class:`padre.config` class, and imported
to the root level for convenience.
'''

import os
import json

verbose = True

if 'PADRE_ROOT' not in os.environ:
    raise RuntimeError('''
ERROR!! PADRE_ROOT not set!!

Please set the environment variable PADRE_ROOT to the location of the
data repository before using the library.

For example, in bash you could type:
    export PADRE_ROOT=/mnt/server/share/data_store

Or in tcsh you could use:
    setenv PADRE_ROOT /mnt/server/share/data_store
''')

padre_root = os.environ['PADRE_ROOT']
data_dir = os.path.join(padre_root,'Data') #: [padre_root]/Data
analyses_dir = os.path.join(padre_root,'Analyses') #: [padre_root]/Analyses
atlas_dir = os.path.join(padre_root,'Atlases')
stimfile_dir = os.path.join(padre_root,'Stimfiles')


def subject_dir(subject):
	'''returns subject directory for given subject'''
	return os.path.join(data_dir,str(subject))

def raw_dir(subject):
	'''[subject_dir]/raw'''
	return os.path.join(subject_dir(subject),'raw')

def sessions_dir(subject):
	'''[subject_dir]/sessions'''
	return os.path.join(subject_dir(subject),'sessions')

def subject_json(subject):
	''' location of subject's JSON file '''
	return os.path.join(subject_dir(subject),'%s.json' % subject)

atlases = {}
'''dictionary of atlas nicknames and dataset locations'''
stimfiles = {}
'''dictionary with location of shared stimfiles'''

def _load_atlases():
	'''load atlas information from JSON file, autoloaded on import'''
	global atlases
	atlas_json = os.path.join(atlas_dir,'atlases.json')
	if os.path.exists(atlas_json):
		with open(atlas_json) as f:
			atlases = json.loads(f.read())
	for atlas in atlases:
		atlases[atlas]['file'] = os.path.join(atlas_dir,atlases[atlas]['file'])	

_load_atlases()

def _load_stimfiles():
	'''loads the shared stimfile information from JSON file, autoloaded on module import'''
	global stimfiles
	stimfile_json = os.path.join(stimfile_dir,'stimfiles.json')
	if os.path.exists(stimfile_json):
		with open(stimfile_json) as f:
			stimfiles = json.loads(f.read())
	for stim in stimfiles:
		stimfiles[stim]['file'] = os.path.join(stimfile_dir,stimfiles[stim]['file'])

_load_stimfiles()