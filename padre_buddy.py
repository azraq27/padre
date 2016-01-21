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
from padre.matching import bottle,filter_subjs,dsets_with,bottle_help


def list_objects(args):
    with nl.notify('Listing objects I can find that match that...'):
        subjects = filter_subjs(matches=args)
        
        dos = [x[0].concept.name for x in args if 'concept' in dir(x[0]) and x[0].concept.name.endswith('_do')]
        if 'subject_do' in dos:
            nl.notify('Subjects:')
            print '\n'.join(subjects)
    
        session_dicts = [x._sessions for x in subjects]
    
        if 'session_do' in dos:
            nl.notify('Sessions:')
            print '\n'.join(set([x.keys() for x in session_dicts]))

        sessions = [a for b in [x.values() for x in session_dicts] for a in b]
        
        if 'label_do' in dos:
            nl.notify('Labels:')
            labels = set([a for b in [x['labels'].keys() for x in sessions] for a in b])
            print '\n'.join(labels)
    
        if 'tag_do' in dos:
            nl.notify('Tags:')
            tags = set([a for b in [x['tags'] for x in sessions if 'tags' in x] for b in a])
            print '\n'.join(tags)
    
        if 'experiment_do' in dos:
            nl.notify('Experiments:')
            experiments = set([x['experiment'] for x in sessions if 'experiment' in x and x['experiment']])
            print '\n'.join(experiments)
        
        if 'dset_do' in dos:
            nl.notify('Datasets:')
            dsets = []
            # Find any restricting labels:
            labels = [x[0].item for x in args if 'concept' in dir(x[0]) and x[0].concept.name=='label']
            for subj in subjects:
                for sess in subj.sessions:                
                    if labels == []:
                        labels = subj._sessions[sess]['labels'].keys()
                    for label in labels:
                        dsets += subj.dsets(session=sess,label=label)
            print '\n'.join(dsets)

def link_dsets(args):
    with nl.notify('Trying to link the following datasets...'):
        subjects = filter_subjs(p.subjects(),args)
        dsets_to_link = []
        
        for subj in subjects:
            with nl.notify(str(subj)):
                for dset in dsets_with(subj,args):
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

def new_object(args):
    args = [x for x in args if 'concept' not in dir(x[0]) or x[0].concept.name!='new']
    concept_names = [x[0].concept.name for x in args if 'concept' in dir(x[0])]
    if 'session_do' in concept_names:
        other_args = [x for x in args if isinstance(x,basestring)]
        if len(other_args)>1:
            nl.notify('Error: You gave me multiple names (%s), don\'t know which you want to be the session name!' % ','.join(other_args),level=nl.level.error)
            return False
        new_session = other_args[0]
        if 'subject' not in concept_names:
            nl.notify('Error: I don\'t know what subject to create session %s in!' % new_session,level=nl.level.error)
            return False
        subject_id = [x[0].item for x in args if 'concept' in dir(x[0]) and x[0].concept.name=='subject'][0]
        with nl.notify('Creating session %s in subject %s' % (new_session,subject_id)):
            subj = p.load(subject_id)
            if not subj:
                nl.notify('Error: couldn\'t load data for subject "%s"' % subject_id,level=nl.level.error)
                return False
            p.maint.new_session(subj,new_session)
            return True
    # Otherwise assume you want to make a subject
    other_args = [x for x in args if isinstance(x,basestring)]
    if len(other_args)>1:
        nl.notify('Error: You gave me multiple names (%s), don\'t know which you want to be the subject name!' % ','.join(other_args),level=nl.level.error)
        return False
    new_subject = other_args[0]
    with nl.notify('Creating new subject %s' % (new_subject)):
        p.maint.create_subject(new_subject)
        return True

def add_data(args):
    pass

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
        

bottle.set_action('list',list_objects)
bottle.set_action('link',link_dsets)
bottle.set_action('new',new_object)
bottle.set_action('add',add_data)

if __name__ == '__main__':
    if len(sys.argv)==1:
        bottle_help()
    else:
        bottle.process_string(sys.argv[1:])