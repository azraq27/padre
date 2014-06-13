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

class Session(dict):
    '''customized dictionary to add a couple helper methods'''
    def __init__(self):
        dict.__init__(self)
        self.current_session = None
    
    def __enter__(self):
        if len(self.keys()):
            self.current_session = self.keys()[0]
            return self.get(self.current_session)
        return None
    
    def __exit__(self, type, value, traceback):
        pass

class SessionFinder(dict):
    '''behaves as either a dictionary of sessions or a function to search for a session'''
    def __call__(self,session=None,label=None,type=None,dset=None,incomplete=False):
        '''returns a dictionary containing all of the sessions matching all the given parameters
        
        if session name is explicitly given, will only return that session'''
        return_dict = Session()
        if session:
            if session in self:
                return self[session]
        elif dset:
            for sess in self:
                for label in self[sess]['labels']:
                    if dset in self[sess]['labels'][label]:
                        return_dict[sess] = self[sess]
        else:
            for sess in self:
                if type:
                    if self[sess]['type']!=type:
                        continue
                if label:
                    if label not in self[sess]['labels']:
                        continue
                return_dict[sess] = self[sess]
        
        for sess in return_dict:
            for label in return_dict[sess]['labels']:
                return_dict[sess]['labels'][label] = [self._make_dset_absolute(x,sess) for x in return_dict[sess]['labels'][label] if incomplete or 'incomplete' not in self[sess] or x not in self[sess]['incomplete']]
        return return_dict

class Subject(object):
    '''abstract container for subject information
    
    Subject objects can either be returned by one of the high-level lookup functions
    as part of a subject list (e.g., :meth:`p.subjects` ), or created individually using one of the class
    creation functions
    '''
    
    def __init__(self,subject_id,*initial_data):
        for key in root_level_attrs:
            if key != 'sessions':
                setattr(self, key, None)
        
        self.subject_id = subject_id
        '''Experimental id - also available by casting as string (e.g., ``str(subject)``
        or ``'%s' % subject``)
        '''
        self.include = True
        '''Bool value of whether this subject should normally be used'''
        
        self.notes = ''
        '''Free text notes on the subject'''
        
        self.sessions = SessionFinder()
        '''Dictionary organized by scanning session. Each entry contains several keys relating
        to session meta-data as well as a dictionary ``subject.sessions['labels']``. The keys
        for this dataset are the descriptive labels for each dataset (e.g., "anatomy", "field_map"),
        and the values are lists of the dataset filenames.
        '''
        
        for dictionary in initial_data:
            for key in dictionary:
                if key=='sessions':
                    self.sessions = SessionFinder(dictionary[key])
                else:
                    setattr(self, key, dictionary[key])
        
        # Autopopulate ``subject`` and ``name`` fields in sessions:
        for session in self.sessions:
            self.sessions[session]['subject'] = self.subject_id
            self.sessions[session]['name'] = session
    
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
    
    def import_raw(self,new_dir,remove=False):
        '''copies the directory ``dir`` into the raw directory, and deletes original if ``remove`` is ``True``'''
        dest_dir = os.path.join(p.raw_dir(self),os.path.split(new_dir.rstrip('/'))[1])
        if os.path.exists(dset_dir):
            raise OSError('Cannot import "%s" into subject %s - directory already exists' % (new_dir,self))
        if remove:
            shutil.move(new_dir,dest_dir)
        else:
            shutil.copytree(new_dir,dest_dir)
    
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
        save_dict['sessions'] = save_dict.pop('_sessions')
        for session in save_dict['sessions']:
            for k in ['subject','name']:
                if k in save_dict['sessions'][session]:
                    del(save_dict['sessions'][session][k])
        with open(json_file,'w') as f:
            f.write(json.dumps(save_dict, sort_keys=True, indent=2))
    
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
        self.sessions[session_name] = SessionFinder(default_session())
    
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
    
    def _make_dset_absolute(self,dset,session):
        '''adds the appropriate directory prefix to a file'''
        return os.path.join(p.sessions_dir(self),session,dset)
    
    def dsets(self,label=None,session=None,type=None,incomplete=False):
        ''' returns a list of datasets matching all of the given parameters 
        
        .. warning::
    
            This method is convenient but don't cover every possibility. For example, if the 
            anatomy scan for a functional session was lost, but there is another anatomy scan 
            obtained at another date, these datasets will appear normally as ``subject.dsets('functional')``
            and ``subject.dsets('anatomy')`` with no reference to the fact that they were obtained 
            in different sessions. If you write your script session-centric, you can explicitly 
            address these exception cases.
        '''
        return_dsets = []
        if session:
            include_sessions = [session]
        else:
            include_sessions = self.sessions.keys()
        for sess in include_sessions:
            if sess in self.sessions:
                if type:
                    if self.sessions[sess]['type']!=type:
                        continue
                if label:
                    include_labels = [label]
                else:
                    include_labels = self.sessions[sess]['labels']
                for label in include_labels:
                    if label in self.sessions[sess]['labels']:
                        return_dsets += [self._make_dset_absolute(x,sess) for x in self.sessions[sess]['labels'][label] if incomplete or 'incomplete' not in self.sessions[sess] or x not in self.sessions[sess]['incomplete']]
        return return_dsets
    
    def __repr__(self):
        return "subject(%s)" % (self.subject_id)
    
    def __str__(self):
        return self.subject_id
    
    def pretty_print(self):
        '''prints out a text representation of the subject data'''
        print 'Subject %s:' % self.subject_id
        print '='*50
        print '\tinclude = %s' % str(self.include)
        print '\tnotes = %s' % self.notes
        print '\tattributes:'
        print '\t\t%s' % ' '.join(set(self.__dict__.keys()) - set(['dsets', 'sessions', 'subject_id', 'labels', 'include', 'notes']))
        print '----sessions---' + '-'*35
        for sess in self.sessions:
            print '|-- %s:' % sess
            print '\tdate: %s' % self.sessions[sess]['date']
            print '\ttype: %s' % self.sessions[sess]['type']
            print '\tother attributes:'
            print '\t\t%s' % ' '.join(set(self.sessions[sess].keys()) - set(['date', 'type', 'labels']))
            print '\tdatasets:'
            for label in self.sessions[sess]['labels']:
                print '\t\t%s:'  % label
                for dset in self.sessions[sess]['labels'][label]:
                    print '\t\t\t%s' % dset

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

_all_subjects = None
def load_subjects():
    global _all_subjects
    _all_subjects = [Subject.load(x) for x in sorted(subject_ids)]

index_subjects()
load_subjects()


def subjects(label=None,only_included=True):
    '''returns a list of subject objects for all subjects with valid JSON files
    
    if *label* is set, it will only return subjects who have datasets with that label
    
    if *only_included* is True, will exclude any subjects with ``subject.include``
    set to False
    '''
    all_subjs = list(_all_subjects)
    if label:
        all_subjs = [x for x in all_subjs if len(x.dsets(label))]
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