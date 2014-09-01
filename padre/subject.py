import padre as p
import json,os,shutil,copy

 
def _default_session(): 
    return dict({
        'date': '',
        'type': '',
        'experiment': '',
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

class DsetFinder(list):
    '''behaves as either a list of dsets or a function to search for a dset'''
    def __init__(self,session_dict):
        self.session_dict = session_dict
        self.session_dir = None
        self.incomplete = False
    
    def _dset_list(self):
        dset_list = []
        for sess in self.session_dict:
            for label in self.session_dict[sess]['labels']:
                dset_list += self.session_dict[sess]['labels'][label]
        if self.session_dir:
            dset_list = [os.path.join(self.session_dir,dset) for dset in dset_list]
        return dset_list
    
    def __getitem__(self,index):
        return self.dset_list()[index]
    
    def __repr__(self):
        return dict.__repr__(self._dset_list())
    
    def __str__(self):
        return dict.__str__(self._dset_list())
    
    def __iter__(self):
        for dset in self._dset_list():
            yield dset
    
    def __call__(self,label=None,experiment=None,session=None,type=None,incomplete=False):
        ''' returns a list of datasets matching all of the given parameters 
        
        .. warning::
    
            This method is convenient but don't cover every possibility. For example, if the 
            anatomy scan for a functional session was lost, but there is another anatomy scan 
            obtained at another date, these datasets will appear normally as ``subject.dsets('functional')``
            and ``subject.dsets('anatomy')`` with no reference to the fact that they were obtained 
            in different sessions. If you write your script session-centric, you can explicitly 
            address these exception cases.
        '''
        if experiment==None and p.global_experiment:
            experiment = p.global_experiment
        return_dsets = []
        if session:
            include_sessions = [session]
        else:
            include_sessions = self.session_dict.keys()
        for sess in include_sessions:
            if sess in self.session_dict:
                if type:
                    if self.session_dict[sess]['type']!=type:
                        continue
                if experiment:
                    if self.session_dict[sess]['experiment']!=experiment:
                        continue
                if label:
                    include_labels = [label]
                else:
                    include_labels = self.session_dict[sess]['labels']
                for label in include_labels:
                    if label in self.session_dict[sess]['labels']:
                        if self.session_dir:
                            return_dsets += [os.path.join(self.session_dir,sess,dset) for dset in self.session_dict[sess]['labels'][label] if self.incomplete or ('incomplete' not in self.session_dict[sess]) or (dset not in self.session_dict[sess]['incomplete'])]                        
                        else:
                            return_dsets += [os.path.join(sess,dset) for dset in self.session_dict[sess]['labels'][label] if self.incomplete or ('incomplete' not in self.session_dict[sess]) or (dset not in self.session_dict[sess]['incomplete'])]                                                    
        return return_dsets
    

class SessionFinder(dict):
    '''behaves as either a dictionary of sessions or a function to search for a session'''
    def __init__(self,*args,**kwargs):
        '''will be initialized with session dictionary
        defaults to ``incomplete`` = ``False``, which will not return dsets that are marked "incomplete"'''
        dict.__init__(self,*args,**kwargs)
        self.session_dir = None
        self.incomplete = False
    
    def __getitem__(self,key):
        sess = copy.deepcopy(dict.__getitem__(self,key))
        if self.session_dir:
            for label in sess['labels']:
                sess['labels'][label] = [os.path.join(self.session_dir,key,dset) for dset in sess['labels'][label] if self.incomplete or ('incomplete' not in sess) or (dset not in sess['incomplete'])]
        return sess
    
    def __call__(self,label=None,experiment=None,type=None,dset=None):
        '''returns a dictionary containing all of the sessions matching all the given parameters
            :label:         session contains datasets with given label
            :type:          session is of given type
            :experiment:    only sessions from given experiment
            :dset:          session contains dset with given filename
            :incomplete:    if ``False`` will filter out incomplete datasets in returned session
        '''
        if experiment==None and p.global_experiment:
            experiment = p.global_experiment
        return_dict = Session()
        if dset:
            if os.sep in dset:
                dset = os.path.basename(dset.rstrip(os.sep))
            for sess in self:
                if experiment:
                    if self[sess]['experiment']!=experiment:
                        continue
                for label in self[sess]['labels']:
                    if dset in self[sess]['labels'][label]:
                        return_dict[sess] = self[sess]
        else:
            for sess in self:
                if experiment:
                    if self[sess]['experiment']!=experiment:
                        continue
                if type:
                    if self[sess]['type']!=type:
                        continue
                if label:
                    if label not in self[sess]['labels']:
                        continue
                return_dict[sess] = self[sess]
        
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
                elif key=='dsets':
                    pass
                else:
                    setattr(self, key, dictionary[key])
        
        self.dsets = DsetFinder(self.sessions)
        self.session_dir = p.sessions_dir(self)
        
        self.sessions.session_dir = p.sessions_dir(self)
        
        # Autopopulate ``subject`` and ``name`` fields in sessions:
        for session in self.sessions:
            self.sessions[session]['subject'] = self.subject_id
            self.sessions[session]['name'] = session
    
    @classmethod
    def load(cls,subject_id,data=None):
        ''' returns a subject object initialized using JSON file (or supplied ``data`` argument) '''
        if data==None:
            json_file = p.subject_json(subject_id)
            try:
                with open(json_file) as f:
                    data = json.loads(f.read())
            except (ValueError,IOError):
                p.error('Could not load valid JSON file for subject %s' % subject_id)
                return None
        return cls(subject_id,data)

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
        save_dict['sessions'] = dict(self.sessions)
        for session in save_dict['sessions']:
            for k in ['subject','name','dsets']:
                if k in save_dict['sessions'][session]:
                    del(save_dict['sessions'][session][k])
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
            print '\texperiment: %s' % self.sessions[sess]['experiment']
            print '\tother attributes:'
            print '\t\t%s' % ' '.join(set(self.sessions[sess].keys()) - set(['date', 'type', 'labels', 'experiment']))
            print '\tdatasets:'
            for label in self.sessions[sess]['labels']:
                print '\t\t%s:'  % label
                for dset in self.sessions[sess]['labels'][label]:
                    print '\t\t\t%s' % dset

def rename(subject_id,new_subject_id,deep=False):
    subj = Subject.load(subject_id)
    if subj:
        try:
            os.rename(p.subject_dir(subject_id),p.subject_dir(new_subject_id))
        except OSError:
            nl.notify('Error: filesystem reported error moving %s to %s' % (subject_id,new_subject_id),level=nl.level.error)
        else:
            subj.subject_id = new_subject_id
            subj.save()
            if deep:
                for dset in subj.dsets():
                    if str(subj) in os.path.basename(dset):
                        new_name = os.path.join(os.path.dirname(dset),os.path.basename(dset).replace(args.subject,args.new_name))
                        try:
                            os.rename(dset,new_name)
                        except OSError:
                            nl.notify('Error: filesystem reported error moving %s to %s' % (subj,args.new_name),level=nl.level.error)                            
            else:
                nl.notify('Successfully renamed %s to %s (NOTE: none of the dataset names are changed in this process)' % (subj,args.new_name))

subject_ids = set()
tasks = set()
experiments = set()
root_level_attrs = set()
def index_subjects(save_subjects=False):
    global _all_subjects
    if save_subjects:
        _all_subjects = []
    if os.path.exists(p.data_dir):
        for subject_id in os.listdir(p.data_dir):
            if os.path.exists(p.subject_json(subject_id)):
                try:
                    with open(p.subject_json(subject_id)) as subj_json:
                        subject_data = json.loads(subj_json.read())
                    [root_level_attrs.add(x) for x in subject_data.keys()]
                    subject_ids.add(subject_id)
                    for session in subject_data['sessions']:
                        if 'experiment' in subject_data['sessions'][session] and subject_data['sessions'][session]['experiment']!='':
                            experiments.add(subject_data['sessions'][session]['experiment'])
                        if 'labels' in subject_data['sessions'][session]:
                            [tasks.add(x) for x in subject_data['sessions'][session]['labels']]
                    _all_subjects.append(Subject.load(subject_id,subject_data))
                except ValueError:
                    print p.subject_json(subject_id)
                    p.error('Could not load valid JSON file for subject %s' % subject_id)

_all_subjects = None
def load_subjects():
    global _all_subjects
    _all_subjects = [Subject.load(x) for x in sorted(subject_ids)]

index_subjects(True)
#load_subjects()


def subjects(label=None,experiment=None,only_included=True):
    '''returns a list of subject objects for all subjects with valid JSON files
    
    if *label* is set, it will only return subjects who have datasets with that label
    
    if *experiment* is set, will only return subjects that have a scan for the given experiment
    
    if *only_included* is True, will exclude any subjects with ``subject.include``
    set to False
    '''
    if experiment==None and p.global_experiment:
        experiment = p.global_experiment
    all_subjs = list(_all_subjects)
    if label:
        all_subjs = [x for x in all_subjs if len(x.dsets(label))]
    if experiment:
        all_subjs = [x for x in all_subjs if experiment in [y['experiment'] for y in x.sessions if 'experiment' in y]]
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
