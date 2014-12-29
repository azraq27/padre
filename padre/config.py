'''Standard directory and filename locations are stored in the :class:`padre.config` class, and imported
to the root level for convenience. (e.g., ``padre.config.padre_root`` can be accessed as ``padre.padre_root``)
'''

import os
import json

verbose = True

error_msg = '''
ERROR!! PADRE_ROOT not set!!

Please set the environment variable PADRE_ROOT to the location of the
data repository before using the library.

For example, in bash you could type:
    export PADRE_ROOT=/mnt/server/share/data_store

Or in tcsh you could use:
    setenv PADRE_ROOT /mnt/server/share/data_store
'''

padre_root = '' #: The absolute path to the root of the padre directory tree (taken from the PADRE_ROOT environment variable)

if 'PADRE_ROOT' not in os.environ:
    print error_msg
else:
    padre_root = os.environ['PADRE_ROOT']
data_dir = os.path.join(padre_root,'Data') #: [padre_root]/Data
analyses_dir = os.path.join(padre_root,'Analyses') #: [padre_root]/Analyses
atlas_dir = os.path.join(padre_root,'Atlases') #: [padre_root]/Atlases (see :data:`padre.config.atlases` for a description)
stimfile_dir = os.path.join(padre_root,'Stimfiles') #: [padre_root]/Stimfiles (see :data:`padre.config.stimfiles` for a description)
trash_dir = os.path.join(padre_root,'Trash')
''' [padre_root]/Trash

Contains deleted subjects and sessions (instead of actually deleting them). Currently just stores them forever.
'''


def subject_dir(subject):
	'''returns subject directory for given subject'''
	return os.path.join(data_dir,str(subject))

def raw_dir(subject):
	'''[subject_dir]/raw'''
	return os.path.join(subject_dir(subject),'raw')

def sessions_dir(subject):
	'''[subject_dir]/sessions'''
	return os.path.join(subject_dir(subject),'sessions')

json_ext = 'json'  #: extension used for the JSON file

def subject_json(subject):
	''' location of subject's JSON file '''
	return os.path.join(subject_dir(subject),'%s.%s' % (subject,json_ext))

atlases = {}
'''dictionary of atlas nicknames and dataset locations
each atlas is listed by its recognizable name (e.g., ``TT_N27``) and contains (*optionally*) any of the following useful information:

:file:  an absolute path to the atlas filename (*required*)
:space: a description of the space this atlas is registered to (e.g., tlrc or mni)
:notes: free-text notes on the atlas

other dictionary entries may be present offering more meta-data on that particular atlas'''

stimfiles = {}
'''dictionary with location of shared stimfiles

These stimfiles are standardardized stimfiles to common tasks that can be reused for multiple different subjects'''

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
