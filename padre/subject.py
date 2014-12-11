import padre as p
import neural as nl
import json,os,shutil,copy

''' padre v2.0 design:

subject
    |- dsets(label,exp,...)
    |- meta('demographics','clinical','behavioral','neuropsych')
        # list available options:
    |- sessions, experiments, labels, types

dset
    |- complete
    |- meta('eprime','scan_sheet')
    |- info #dset_info object
    |- experiment, label, type, session
'''

class Dset(object):
    '''object to contain dataset filename and meta-data
    
    Calling :meth:`subject.dsets` with return a list of these objects. They can be treated as 
    strings most of the time, because they will return the absolute location of the dataset
    filename when cast as strings. If you want to explicitly convert them into the file location
    you can manually cast them as a string, ``str(dset)``. To return only the filename,
    with no directory information, you can call :meth:`__str__` with the argument ``False``
    
    Other information contained in the objects include:
    
    :complete:      Whether this is a complete, usable dataset
    :date:          Date this was acquired
    :experiment:    Experiment in which this was aquired
    :label:         Kind of dataset (e.g., ``anatomy``)
    :type:          Type of session this was acquired during
    :session:       Label of session this was acquired during
    :md5:           md5 checksum of dataset file (used for checking for data corruption)
    :meta:          dictionary of meta data associated with this dataset (e.g., ``eprime`` or ``eprime-txt``)
    :info:          object containing information from a call to ``3dinfo`` (for more information see the neural library)'''
    
    def __init__(self,subject,session,dset_fname,label=None,complete=True,md5=None,meta={}):
        self._dset_fname = dset_fname
        self.complete = complete
        self.meta = meta
        self.md5 = md5
        
        self.date = subject._sessions[session]['date']
        self.experiment = subject._sessions[session]['experiment']
        self.label = label
        if self.label == None:
            try:
                for l in subject._sessions[session]['labels']:
                    for d in subject._sessions[session]['labels'][l]:
                        if d['filename'] == dset_fname:
                            self.label = l
                            raise StopIteration
            except StopIteration:
                pass
        self.type = subject._sessions[session]['type']
        self.session = session
        
        self._info = None
        self._subject = subject
    
    def __abspath__(self):
        '''return the absolute path the the dataset'''
        return os.path.join(p.sessions_dir(self._subject),self.session,self._dset_fname)
    
    def __dict__(self):
        return {
            'filename': self._dset_fname,
            'complete': self.complete,
            'md5': self.md5,
            'meta': self.meta
        }
    
    @classmethod
    def from_dict(cls,subject,session,dict_source):
        dset = Dset(subject,session,dict_source['filename'])
        dset.complete = dict_source['complete'] if 'complete' in dict_source else True
        dset.md5 = dict_source['md5'] if 'md5' in dict_source else None
        dset.meta = p.ForgivingDict.copy_nested_dict(dict_source['meta'])
        return dset
    
    def __str__(self,absolute=True):
        if absolute:
            return self.__abspath__()
        else:
            return self._dset_fname
    
    def __repr__(self):
        return self._dset_fname
    
    def __getattribute__(self,name):
        if name=='info':
            if self._info==None:
                try:
                    self._info = nl.afni.dset_info(self.__abspath__())
                except:
                    pass
            return self._info
        else:
            return object.__getattribute__(self,name)

class Subject(object):
    '''abstract container for subject information
    
    If cast as string(``str(subject)``), will return subject id. Subject objects can be obtained by 
    calling the search function :meth:`padre.subjects` or by loading directly using
    :meth:`padre.load`
    
    .. autoinstanceattribute:: Subject.include
        :annotation:
    
    .. autoinstanceattribute:: Subject.sessions
        :annotation:
        
    .. autoinstanceattribute:: Subject.labels
        :annotation:
        
    .. autoinstanceattribute:: Subject.experiments
        :annotation:
    
    .. autoinstanceattribute:: Subject.meta
        :annotation:
    
    .. autoinstanceattribute:: Subject.notes
        :annotation:
    
    .. automethod:: Subject.load
    
    .. automethod:: Subject.dsets
    
    '''
    def __init__(self,subject_id,initial_data={}):
        self._subject_id = subject_id
        #: If ``False``, this subject will be excluded from standard analyses
        self.include = initial_data['include'] if 'include' in initial_data else True  
        #: Free text notes on subject
        self.notes = initial_data['notes'] if 'notes' in initial_data else ''
        
        #: List of session names
        self.sessions = []
        #: List of labels used by this subject
        self.labels = []
        #: List of experiments this subject has data for
        self.experiments = []
        self._dsets = []
        
        self._sessions = initial_data['sessions'] if 'sessions' in initial_data else {}
        for sess in self._sessions:
            if 'unverified' in self._sessions[sess] and not p._include_all:
                continue
            self.sessions.append(sess)
            for label in self._sessions[sess]['labels']:
                self.labels.append(label)
                for dset in self._sessions[sess]['labels'][label]:
                    self._dsets.append(Dset(self,sess,dset['filename'],label,dset['complete'],dset['meta']))
        self.labels = list(set(self.labels))
        self.experiments = list(set(self.labels))
        
        self.meta = p.ForgivingDict.copy_nested_dict(initial_data['meta']) if 'meta' in initial_data else p.ForgivingDict()
        '''Dictionary of meta-data
        Standard entries include: ``clinical``, ``demo`` (i.e., demographic), ``neuropsych``, and ``behavioral``'''
    
    @classmethod
    def load(cls,subject_id):
        ''' returns a subject object initialized using JSON file
        If no subject can be loaded, will print an error and return ``None``
        
        This method is imported to the root-level, and can be called as :meth:``padre.load``'''
        subject_id = str(subject_id).rstrip('/')
        json_file = p.subject_json(subject_id)
        try:
            with open(json_file) as f:
                return Subject(subject_id,json.loads(f.read()))
        except (ValueError,IOError):
            p.error('Could not load valid JSON file for subject %s' % subject_id)
            return None
    
    def __dict__(self):
        return {
            'include': self.include,
            'notes': self.notes,
            'meta': self.meta,
            'sessions': self._sessions
        }
             
    def save(self,json_file=None):
        ''' save current state to JSON file '''
        if json_file==None:
            json_file = p.subject_json(self._subject_id)
        save_dict = self.__dict__()
        with open(json_file,'w') as f:
            f.write(json.dumps(save_dict, sort_keys=True, indent=2))
    
    def init_directories(self):
        ''' create directories that these scripts expect on the disk '''
        for d in [
                p.subject_dir(self),
                p.raw_dir(self),
                p.sessions_dir(self)
            ]:
            if not os.path.exists(d):
                os.makedirs(d)   
    
    def __repr__(self):
        return "subject(%s)" % (self._subject_id)
    
    def __str__(self):
        return self._subject_id
    
    def dsets(self,label=None,experiment=None,session=None,type=None,include_all=False):
        '''returns list of :class:`Dset` objects matching the given criteria
        
        This is the primary method for accessing the datasets. This does not return strings, but :class:`Dset` objects.
        Datasets can be searched using the following parameters:
        
            :label:         type of dataset (e.g., ``anatomy`` or a task name)
            :experiment:    name of experiment this dataset belongs to
            :session:       name of session this dataset was collected in
            :type:          arbitrary tag for session (e.g., ``preop`` or ``session_5``)
            
        By default, datasets that are tagged as ``unverified`` or ``incomplete`` are not returned. To return all
        datasets, call with ``include_all=True``'''
        if experiment==None and p._global_experiment:
            experiment = p._global_experiment
        return_dsets = []
        if session:
            include_sessions = [session]
        else:
            include_sessions = self._sessions.keys()
        if include_all==False:
            include_sessions = [x for x in include_sessions if p._include_all or 'unverified' not in self._sessions[x] and ('include' not in self._sessions[x] or self._sessions[x]['include']==True)]
        for sess in include_sessions:
            if sess in self._sessions:
                if type:
                    if self._sessions[sess]['type']!=type:
                        continue
                if experiment:
                    if self._sessions[sess]['experiment']!=experiment:
                        continue
                if label:
                    include_labels = [label]
                else:
                    include_labels = self._sessions[sess]['labels']
                for label in include_labels:
                    if label in self._sessions[sess]['labels']:
                        return_dsets += [Dset.from_dict(self,sess,dset) for dset in self._sessions[sess]['labels'][label] if include_all or dset['complete']]
        return return_dsets


tasks = set()
experiments = set()
types = set()
_all_subjects = {}
_indexed_and_loaded_all_subjects = False

def _index_one_subject(subject_id):
    _all_subjects[subject_id] = Subject.load(subject_id)
    for session in _all_subjects[subject_id]._sessions:
        session_dict = _all_subjects[subject_id]._sessions[session]
        if 'experiment' in session_dict and session_dict['experiment']!='' and session_dict['experiment']!=None:
            experiments.add(session_dict['experiment'])
        if 'labels' in session_dict and session_dict['labels']!='' and session_dict['labels']!=None:
            [tasks.add(x) for x in session_dict['labels']]
        if 'type' in session_dict and session_dict['type']!='' and session_dict['type']!=None:
            types.add(session_dict['type'])

def _index_all_subjects(load_all=False):
    global _all_subjects
    if os.path.exists(p.data_dir):
        for subject_id in os.listdir(p.data_dir):
            if os.path.exists(p.subject_json(subject_id)):
                if subject_id not in _all_subjects:
                    _all_subjects[subject_id] = None
                if load_all and _all_subjects[subject_id]==None:
                    _index_one_subject(subject_id)
    if load_all:
        _indexed_and_loaded_all_subjects = True

_index_all_subjects()

def subjects(experiment=None,label=None,type=None,only_included=True):
    '''returns a list of subject objects for all subjects with valid JSON files
    
    :experiment:    only return subjects that have a scan for the given experiment
    :label:         only return subjects who have datasets with that label
    :type:          only return subjects who have a session of given type
    
    :only_included: if True (the default), will exclude any subjects with ``subject.include``
                    set to False
    
    Using this list, it is easy to filter again to find a specific subset of subjects. For example,
    to get a list of all subjects who have had a left ATL surgery::

    	subjects = [s for s in padre.subjects() if s.meta['clinical']['surgery_type']=='left atl']
    
    '''
    if not _indexed_and_loaded_all_subjects:
        _index_all_subjects(True)
    if experiment==None and p._global_experiment:
        experiment = p._global_experiment
    all_subjs = _all_subjects.values()
    if label:
        all_subjs = [x for x in all_subjs if len(x.dsets(label))]
    if experiment:
        all_subjs = [x for x in all_subjs if experiment in [x._sessions[y]['experiment'] for y in x._sessions]]
    if type:
        all_subjs = [x for x in all_subjs if type in [x._sessions[y]['type'] for y in x._sessions]]
    if only_included and not p._include_all:
        all_subjs = [x for x in all_subjs if x.include]
    
    return all_subjs

def subject_exists(subj_id):
    return os.path.exists(p.subject_json(subj_id))

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
