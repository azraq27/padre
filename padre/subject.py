import padre as p
import json,os,shutil

 
def _default_session(): 
	return dict({
		'date': '',
		'type': '',
		'labels': dict()
	})

class SessionExists(LookupError):
	pass

class Subject(object):
	'''abstract container for subject information
	
	Subject objects can either be returned by one of the high-level lookup functions
	as part of a subject list (e.g., :meth:`p.subjects` ), or created individually using one of the class
	creation functions
	'''
	
	def __init__(self,subject_id,*initial_data):
		for key in root_level_attrs:
			setattr(self, key, None)
		
		self.subject_id = subject_id
		'''Experimental id - also available by casting as string (e.g., ``str(subject)``
		or ``'%s' % subject``)
		'''
		self.include = True
		'''Bool value of whether this subject should normally be used'''
		
		self.notes = ''
		'''Free text notes on the subject'''
		
		self.sessions = {}
		'''Dictionary organized by scanning session. Each entry contains several keys relating
		to session meta-data as well as a dictionary ``subject.sessions['labels']``. The keys
		for this dataset are the descriptive labels for each dataset (e.g., "anatomy", "field_map"),
		and the values are lists of the dataset filenames.
		'''
		
		self.labels = {}
		'''A dictionary of all the datasets available for this subject, organized by descriptive
		label (collapsed across session).
		'''
		
		self.dsets = []
		'''A flat list of all datasets available for this subject, collapsed across session and
		dataset type.
		'''
		
		for dictionary in initial_data:
			for key in dictionary:
				setattr(self, key, dictionary[key])
	
	@classmethod
	def load(cls,subject_id):
		''' returns a subject object initialized using JSON file '''
		json_file = p.subject_json(subject_id)
		try:
			with open(json_file) as f:
				subj = cls(subject_id,json.loads(f.read()))
		except (ValueError,IOError):
			p.error('Could not load valid JSON file for subject %s' % subject_id)
			subj = None
		else:
			self._make_sessions_absolute()
			subj._update_shortcuts()
		return subj

	@classmethod
	def create(cls,subject_id):
		''' creates a new subject (loads old JSON if present and valid) '''
		if os.path.exists(p.subject_json(subject_id)):
			try:
				subj = cls.load(subject_id)
			except ValueError:
				subj = cls(subject_id)				
		else:
			subj = cls(subject_id)
		subj.init_directories()
		subj.save()

		return subj
	
	def add_attr(self,attribute):
		'''adds a new root-level attribute
		
		This attribute will be available directly by calling subject.attribute,
		and will persist across sessions (if the subject is saved)'''
		if not attribute in dir(self):
			setattr(self,attribute,None)
			root_level_attrs.add(attribute)
	
	def save(self,json_file=None):
		''' save current state to JSON file (overwrites) '''
		if json_file==None:
			json_file = p.subject_json(self.subject_id)
		save_dict = dict(self.__dict__)
		# Delete the shortcuts -- they will be autocreated at every load
		del(save_dict['labels'])
		del(save_dict['dsets'])
		self._make_sessions_relative()
		with open(json_file,'w') as f:
			f.write(json.dumps(save_dict, sort_keys=True, indent=2))
		self._make_sessions_absolute()
		self._update_shortcuts()
	
	def init_directories(self):
		''' create directories that these scripts expect on the disk '''
		for p in [
				p.subject_dir(self),
				p.raw_subject_dir(self),
				p.sessions_dir(self)
			]:
			if not os.path.exists(p):
				os.makedirs(p)
	
	def new_session(self,session_name):
		''' create a new session
		
		Inserts the proper data structure into the JSON file, as well as creating
		the directory on disk.
		'''
		if session_name in self.sessions:
			raise SessionExists
		session_dir = os.path.join(p.sessions_dir(self),session_name)
		if not os.path.exists(session_dir):
			os.makedirs(session_dir)
		self.sessions[session_name] = _default_session()
	
	def delete_session(self,session_name,purge=False):
		''' delete a session
		
		By default, will only delete the references to the data within the JSON file.
		If ``purge`` is given as ``True``, then it will also delete the files from
		the disk (be careful!). ``purge`` will also automatically call ``save``.'''
		del(self.sessions[session_name])
		if purge:
			session_dir = os.path.join(p.sessions_dir(self),session_name)
			if os.path.exists(session_dir):
				shutil.rmtree(session_dir)
			self.save()
		else:
			self._update_shortcuts()
		
	
	def _update_shortcuts(self):
		''' update the shortcut objects "labels" and "dsets" based on "sessions" '''
		self.labels = {}
		self.dsets = []
		for session in self.sessions:
			session_dir = os.path.join(p.sessions_dir(self),session)
			if 'labels' in self.sessions[session]:
				for label in self.sessions[session]['labels']:
					if label not in self.labels:
						self.labels[label] = []
					self.labels[label] += [os.path.join(session_dir,x) for x in self.sessions[session]['labels'][label]]
					self.dsets += [os.path.join(session_dir,x) for x in self.sessions[session]['labels'][label]]
	
	def _make_sessions_absolute(self):
		'''updates the sessions dict to make all references absolute'''
		for session in self.sessions:
			session_dir = os.path.join(p.sessions_dir(self),session)
			if 'labels' in self.sessions[session]:
				for label in self.sessions[session]['labels']:
					self.sessions[session]['labels'][label] = [os.path.join(session_dir,os.path.split(x)[1]) for x in self.sessions[session]['labels'][label]]
	
	def _make_sessions_relative(self):
		'''updates the sessions dict to make all references relative to standard directories'''
		for session in self.sessions:
			session_dir = os.path.join(p.sessions_dir(self),session)
			if 'labels' in self.sessions[session]:
				for label in self.sessions[session]['labels']:
					self.sessions[session]['labels'][label] = [os.path.split(x)[1] for x in self.sessions[session]['labels'][label]]
	
	def session_for_label(self,label):
		''' returns the name of the first session that matches *label*'''
		for session in self.sessions:
			if label in self.sessions[session]['labels']:
				return session
	
	def dsets_for(self,label=None,session=None,session_type=None):
		''' returns a list of datasets matching all of the given parameters '''
		return_dsets = []
		if session:
			include_sessions = [session]
		else:
			include_sessions = self.sessions.keys()
		for sess in include_sessions:
			if sess in self.sessions:
				if session_type:
					if self.sessions[sess]['type']!=session_type:
						continue
				if label:
					include_labels = [label]
				else:
					include_labels = self.sessions[sess]['labels']
				for label in include_labels:
					if label in self.sessions[sess]['labels']:
						return_dsets += [os.path.join(p.sessions_dir(self),sess,x) for x in self.sessions[sess]['labels'][label]]
		return return_dsets
	
	def __repr__(self):
		return "subject(%s)" % (self.subject_id)
	
	def __str__(self):
		return self.subject_id

subject_ids = set()
tasks = set()
root_level_attrs = set()
def index_subjects():
	if os.path.exists(p.data_dir):
		for subject_id in os.listdir(p.data_dir):
			if os.path.exists(p.subject_json(subject_id)):
				try:
					with open(p.subject_json(subject_id)) as subj_json:
						subject_data = json.loads(subj_json.read())
					[root_level_attrs.add(x) for x in subject_data.keys()]
					subject_ids.add(subject_id)
					for session in subject_data['sessions']:
						if 'labels' in subject_data['sessions'][session]:
							[tasks.add(x) for x in subject_data['sessions'][session]['labels']]
				except ValueError:
					print p.subject_json(subject_id)
					p.error('Could not load valid JSON file for subject %s' % subject_id)

index_subjects()

_all_subjects = [Subject.load(x) for x in sorted(subject_ids)]
def subjects(label=None,only_included=True):
	'''returns a list of subject objects for all subjects with valid JSON files
	
	if *label* is set, it will only return subjects who have datasets with that label
	
	if *only_included* is True, will exclude any subjects with ``subject.include``
	set to False
	'''
	all_subjs = list(_all_subjects)
	if label:
		all_subjs = [x for x in all_subjs if label in x.labels and len(x.labels[label])]
	if only_included:
		all_subjs = [x for x in all_subjs if x.include]
	
	return all_subjs

class DatabaseConsistencyError(Exception):
	pass

def _files_exist():
	'''make sure all the files that should be there, are still there'''
	for s in p.subjects():
	    for dset in s.dsets:
	        if not os.path.exists(dset):
				raise DatabaseConsistencyError("dataset is missing: %s" % dset)
	    for sess in s.sessions:
	        if 'scan_sheets' in sess:
	            if not os.path.exists(os.path.join(p.sessions_dir(s),sess,sess['scan_sheets'])):
					raise DatabaseConsistencyError("scan sheets PDF is missing: %s" % sess['scan_sheets'])

def sanity_check():
	'''runs internal checks to find errors'''
	_files_exist()