#!/usr/bin/env python
# depends on:
#   neural
#   padre
#   fuzzywuzzy
#   openpyxl

import argparse,os,json,sys,shutil,getpass
from fuzzywuzzy import process
import padre as p
import neural as nl
import openpyxl
import gini

bottle = gini.semantics.Bottle()

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

def list_objects(args):
    with nl.notify('Listing objects I can find that match that...'):
        subjects = filter_subjs(p.subjects(),args)
    
        if 'subject_do' in args:
            nl.notify('Subjects:')
            print '\n'.join(subjects)
    
        session_dicts = [x._sessions for x in subjects]
    
        if 'session_do' in args:
            nl.notify('Sessions:')
            print '\n'.join(set([x.keys() for x in session_dicts]))

        sessions = [a for b in [x.values() for x in session_dicts] for a in b]
    
        if 'label_do' in args:
            nl.notify('Labels:')
            labels = set([a for b in [x['labels'].keys() for x in sessions] for a in b])
            print '\n'.join(labels)
    
        if 'tag_do' in args:
            nl.notify('Tags:')
            tags = set([a for b in [x['tags'] for x in sessions if 'tags' in x] for b in a])
            print '\n'.join(tags)
    
        if 'experiment_do' in args:
            nl.notify('Experiments:')
            experiments = set([x['experiment'] for x in sessions if 'experiment' in x and x['experiment']])
            print '\n'.join(experiments)

def get(dict,key,only_one=True):
    if key in dict:
        if isinstance(dict[key],list):
            return dict[key][0]
        else:
            return dict[key]
    else:
        return None

def link_dsets(args):
    with nl.notify('Trying to link the following datasets...'):
        subjects = filter_subjs(p.subjects(),args)
        dsets_to_link = []
        
        for subj in subjects:
            with nl.notify(str(subj)):
                for dset in subj.dsets(label=get(args,'label'),tags=get(args,'tag',False),experiment=get(args,'experiment')):
                    nl.notify(dset.__str__(False))
                    dsets_to_link.append(dset)
        nl.notify('Does that all look good? (y/n)')
        i = raw_input()
        if i.lower()=='y':
            nl.notify('Ok, linking them')
            for dset in dsets_to_link:
                try:
                    os.symlink(str(dset),os.path.basename(str(dset)))
                except OSError:
                    pass
        else:
            nl.notify('Nope, that didn\'t look like a "y"...',level=nl.level.warning)

def error(msg,miss=None):
    nl.notify(msg + '\n',level=nl.level.error)
    if miss:
        try:
            import urllib,urllib2
            data = {'miss':miss}
            data_enc = urllib.urlencode(data)
            urllib2.urlopen('http://wolflion.org/cgi-bin/report.py?%s' % data_enc)
        except:
            pass
    sys.exit()

'''def padre_add_meta(args):
    (params,listable,unidentified_args) = identify_params(args,True)
    all_subjs = subjects_from_params(params)
    (all_dsets,unidentified_args) = identify_dsets(unidentified_args,all_subjs)
    if len(all_dsets)!=1:
        error('Error: To add meta-data, you need to give me the name of exactly one dataset')
    (subj,sess,label,dset,i) = all_dsets.values()[0]
    if 'meta' not in subj._sessions[sess]['labels'][label][i]:
        subj._sessions[sess]['labels'][label][i]['meta'] = {}
    subj._sessions[sess]['labels'][label][i]['meta'][args.meta_type] = os.path.basename(args.filename)
    subj.save()
    shutil.copy(args.filename,os.path.join(p.sessions_dir(subj),sess))
    print 'Added %s (%s) to %s' % (os.path.basename(args.filename),args.meta_type,str(subj))'''
        
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
    # Actions
    'list': ['list','show','get','print'],
    'link': ['link','copy','symlink'],
    # Objects
    'subject': p.subject._all_subjects.keys(),
    'label': p.subject.tasks,
    'tag': p.subject.tags,
    'experiment': p.subject.experiments,
    'quiet': ['quiet','quietly','-q','--quiet']
}

bottle.actions = {
    'list':list_objects,
    'link':link_dsets
}

if __name__ == '__main__':
    bottle.process(sys.argv[1:])