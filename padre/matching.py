'''uses methods from the ``gini`` library for flexible matching'''
from gini.semantics import Bottle,Concept
import padre as p
import neural as nl
import copy

bottle = Bottle()

p.subjects()
bottle.vocab = [
    # Direct objects
    Concept('atlas_do', ['atlases','templates']),
    Concept('subject_do', ['subjects','patients']),
    Concept('experiment_do', ['experiments', 'studies', 'study']),
    Concept('label_do', ['labels','tasks']),
    Concept('tag_do', ['types','tags']),
    Concept('session_do', ['sessions','scans','dates']),
    Concept('dset_do', ['dsets','datasets','runs','files']),
    Concept('metadata_do', ['meta','metadata','behavioral','eprime']),
    Concept('eprime_do', ['eprime','edat']),
    Concept('eprime-txt_do', ['eprime-txt']),
    # Actions
    Concept('list', ['list','show','get','print']),
    Concept('link', ['link','copy','symlink']),
    Concept('add', ['add','attach','upload']),
    # Objects
    Concept('subject', p.subject._all_subjects.keys()),
    Concept('label', p.subject.tasks),
    Concept('tag', p.subject.tags),
    Concept('experiment', p.subject.experiments),
    Concept('quiet', ['quiet','quietly','-q','--quiet'])
]


def recursive_parse_string(bottle,string):
    raise RuntimeError('Need to update to newest gini version')
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
    raise RuntimeError('Need to update to newest gini version')
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

def filter_subjs(subjects,matches):
    if not any([x in matches for x in ['subject','session','label','experiment','tag']]):
        nl.notify('Using no constraints')
        return subjects
    with nl.notify('Using constraints:'):
        for concept in matches:
            examples = concept.examples_matching()
            nl.notify('%s = %s' % (concept.name,repr(examples)))
            if concept=='subject':
                subjects = [x for x in subjects if str(x) in examples]
            if concept=='session':
                # This isn't going to work unless we've done a recursive match
                subjects = [x for x in subjects if any([y in x.sessions for y in examples])]
            loop_tests = {
                'experiment': lambda subj,sess: subj._sessions[sess]['experiment'] in examples,
                'label': lambda subj,sess: all([x in subj._sessions[sess]['labels'] for x in examples]),
                'tag': lambda subj,sess: all([x in subj._sessions[sess]['tags'] for x in examples])
            }
            for attr in loop_tests:
                if concept==attr:
                    new_subjects = []
                    for subj in subjects:
                        for sess in subj.sessions:
                            try:
                                if loop_tests[attr](subj,sess):
                                    if subj not in new_subjects:
                                        new_subjects.append(subj) 
                                    break
                            except:
                                pass
                    subjects = new_subjects
    return subjects