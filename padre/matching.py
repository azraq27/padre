'''uses methods from the ``gini`` library for flexible matching'''
import gini
import padre as p
import neural as nl
import copy

bottle = gini.semantics.Bottle()

p.subjects()
bottle.vocab = {
    # Direct objects
    'atlas_do': ['atlases','templates'],
    'subject_do': ['subjects','patients'],
    'experiment_do': ['experiments', 'studies', 'study'],
    'label_do': ['labels','tasks'],
    'tag_do': ['types','tags'],
    'session_do': ['sessions','scans','dates'],
    'dset_do': ['dsets','datasets','runs','files'],
    'metadata_do': ['meta','metadata','behavioral','eprime'],
    'eprime_do': ['eprime','edat'],
    'eprime-txt_do': ['eprime-txt'],
    # Actions
    'list': ['list','show','get','print'],
    'link': ['link','copy','symlink'],
    'add': ['add','attach','upload'],
    # Objects
    'subject': p.subject._all_subjects.keys(),
    'label': p.subject.tasks,
    'tag': p.subject.tags,
    'experiment': p.subject.experiments,
    'quiet': ['quiet','quietly','-q','--quiet']
}

def recursive_parse_string(bottle,string):
    '''calls :meth:`bottle.parse_string` and then adds subject-specific information and re-runs it to get things like dataset names'''
    matches = bottle.parse_string(string)
    if 'other' in matches:
        # There were some strings that didn't match anything
        matching_subjects = filter_subjs(p.subjects(),matches)
        new_bottle = copy.deepcopy(bottle)
        new_bottle.vocab['dset'] = []
        # Not finished -- add dset filenames, metadata, 
        # Would be nice to keep track of where they came from (what subject is this dset from?)

def dsets_with(subj,args):
    '''returns the result of :meth:`Subject.dsets`, using the relevant keyword arguments from args'''
    def get(dict,key,only_one=True):
        if key in dict:
            if only_one and isinstance(dict[key],list):
                return dict[key][0]
            else:
                return dict[key]
        else:
            return None
    return subj.dsets(label=get(args,'label'),tags=get(args,'tag',False),experiment=get(args,'experiment'))

def filter_subjs(subjects,args):
    if not any([x in args for x in ['subject','session','label','experiment','tag']]):
        nl.notify('Using no constraints')
        return subjects
    with nl.notify('Using constraints:'):
        if 'subject' in args:
            nl.notify('subjects = %s' % repr(args['subject']))
            subjects = [x for x in subjects if str(x) in args['subject']]
        if 'session' in args:
            nl.notify('sessions = %s' % repr(args['session']))
            subjects = [x for x in subjects if any([y in x.sessions for y in args['session']])]
        if 'experiment' in args:
            nl.notify('experiments = %s' % repr(args['experiment']))
            new_subjects = []
            for subj in subjects:
                for sess in subj.sessions:
                    if 'experiment' in subj._sessions[sess] and subj._sessions[sess]['experiment'] in args['experiment']:
                        if subj not in new_subjects:
                            new_subjects.append(subj) 
                        break
            subjects = new_subjects
        if 'label' in args:
            nl.notify('labels = %s' % repr(args['label']))
            new_subjects = []
            for label in args['label']:
                for subj in subjects:
                    for sess in subj.sessions:
                        if label in subj._sessions[sess]['labels']:
                            if subj not in new_subjects:
                                new_subjects.append(subj) 
                            break
            subjects = new_subjects
        if 'tag' in args:
            nl.notify('tags = %s' % repr(args['tag']))
            new_subjects = []
            for tag in args['tag']:
                for subj in subjects:
                    for sess in subj.sessions:
                        if 'tags' in subj._sessions[sess] and tag in subj._sessions[sess]['tags']:
                            if subj not in new_subjects:
                                new_subjects.append(subj) 
                            break
            subjects = new_subjects
    return subjects