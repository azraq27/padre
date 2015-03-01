'''uses methods from the ``gini`` library for flexible matching'''
from gini.semantics import Bottle,Concept
from gini import logic
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
    Concept('subject', [[x] for x in p.subject._all_subjects.keys()]),
    Concept('label', [[x] for x in p.subject.tasks]),
    Concept('tag', [[x] for x in p.subject.tags]),
    Concept('experiment', [[x] for x in p.subject.experiments]),
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

def filter_by_match(match,subjects):
    if match.concept.name=='subject':
        # Combine subjects by OR (AND doesn't make any sense..)
        return [x for x in subjects if str(x)==match.examples]
    if match.concept.name=='experiment':
        # Combine experiments by OR
        filtered = []
        for subj in subjects:
            if any([subj._sessions[sess]['experiment'] in match.examples for sess in subj.sessions if 'experiment' in subj._sessions[sess] and subj._sessions[sess]['experiment']]):
                filtered.append(subj)
        return filtered
    if match.concept.name=='label':
        # Combine with AND per subject (not necessarily the same session)
        filtered = []
        for subj in subjects:
            if any([any([label in match.examples for label in subj._sessions[sess]['labels']]) for sess in subj.sessions]):
                filtered.append(subj)
        return filtered
    if match.concept.name=='tag':
        # Combine with AND per subject (not necessarily the same session)
        filtered = []
        for subj in subjects:
            if any([any([tag in match.examples for tag in subj._sessions[sess]['tags']]) for sess in subj.sessions if 'tags' in subj._sessions[sess]]):
                filtered.append(subj)
        return filtered

def filter_subjs(subjects=None,string=None,matches=None,require_match=True):
    '''takes ``list`` of subjects and filters based on the :class:`ConceptMatch`s given in ``matches``. If ``matches``
    is not given, will parse the string ``string`` instead. If ``require_match``, will return ``None`` if it fails to find
    any constraints, otherwise it returns ``subjects``'''
    match_concepts = ['subject','session','label','experiment','tag']
    if subjects==None:
        subjects = p.subjects()
    if matches==None:
        if string==None:
            return subjects
        matches = bottle.parse_string(string)
    running_exclusions = {}
    if not any([[x in sub_matches for x in match_concepts] for sub_matches in matches]):
        if require_match:
            nl.notify('Warning: Could not find any constraints to use',level=nl.level.warning)
            return None
        else:
            nl.notify('Using no constraints')
            return subjects
    with nl.notify('Using constraints:'):
        subjects_total = set(subjects)
        for match_options in matches:
            if not isinstance(match_options,list):
                continue
            match_options = [x for x in match_options if x in match_concepts]
            if len(match_options)==0:
                continue
            subjects_options = set()
            for match in match_options:
                nl.notify('%s = %s' % (match.concept.name,repr(match.examples)))
                subjects_options = logic.or_sets(subjects_options,set(filter_by_match(match,subjects)))
            subjects_total = logic.and_sets(subjects_options,subjects_total)
    return subjects_total
