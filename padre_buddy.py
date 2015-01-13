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

fuzzyness = 90

listable_objects = {
    'atlases': ['atlases','templates'],
    'subjects': ['subjects','patients'],
    'experiments': ['experiments', 'studies', 'study'],
    'labels': ['labels','tasks'],
    'tags': ['types','tags'],
    'sessions': ['sessions','scans','dates'],
    'dsets': ['dsets','datasets','runs','files'],
    'metadata': ['meta','metadata','behavioral','eprime']
}

p.subjects()
all_subjects = p.subject._all_subjects.keys()
all_labels = p.subject.tasks
all_tags = p.subject.tags
all_experiments = p.subject.experiments

all_objects = [(x,'subject') for x in all_subjects] + [(x,'label') for x in all_labels] + [(x,'tag') for x in all_tags] + [(x,'experiment') for x in all_experiments]

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

from neural.personality import _unic_bub_print,decompress

def identify_object(obj):
    '''tries to match to an existing object
    returns a tuple of (object,object_id)'''
    best_match = process.extractOne(obj,[x[0] for x in all_objects])
    if best_match and best_match[1]>fuzzyness:
        return [x for x in all_objects if x[0]==best_match[0]][0]
    else:
        return None

def identify_listable(keyword):
    '''tries to match keyword to some listable object'''    
    possible_names = [x for s in listable_objects.values() for x in s]
    best_match = process.extractOne(keyword,possible_names)
    if best_match[1]>fuzzyness:
        return [x for x in listable_objects if best_match[0] in listable_objects[x]][0]
    else:
        return None

def identify_dsets(dset_names,subjects):
    '''try to find each dset filename in ``dset_names`` within the list of subject objects ``subjects``'''
    found_dsets = {}
    leftover_names = list(dset_names)
    for subj in subjects:
        for sess in subj._sessions:
            for label in subj._sessions[sess]['labels']:
                for i in xrange(len(subj._sessions[sess]['labels'][label])):
                    dset = subj._sessions[sess]['labels'][label][i]
                    if dset['filename'] in dset_names:
                        if dset['filename'] in found_dsets:
                            error('Error: with the given parameters, I found the dataset name %s more than once' % dset['filename'])
                            return None
                        found_dsets[dset['filename']] = (subj,sess,label,dset,i)
                        del(leftover_names[leftover_names.index(dset['filename'])])
    return (found_dsets,leftover_names)

def identify_params(args,allow_unidentified=False):
    '''go through the args and try to assign unassigned jibberish'''
    params = {'subject':args.subject,'session':args.session,'tag':args.tag,'experiment':args.experiment,'label':args.label}
    global all_objects
    listable = None
    added_sessions = False
    unidentified_args = []
    for arg in args.something:
        if params['subject'] and not added_sessions:
            subj = p.load(params['subject'])
            if subj:
                all_objects += [(x,'session') for x in subj.sessions]
            added_sessions = True
        obj = identify_object(arg)
        if obj:
            params[obj[1]] = obj[0]
        else:
            l = identify_listable(arg)
            if l:
                listable = l
            else:
                unidentified_args.append(arg)
    if not allow_unidentified and len(unidentified_args)>0:
        error('Error: Sorry, I can\'t figure out what you mean by "%s"' % arg, arg)
    
    return (params,listable,unidentified_args)
 

def padre_info(args):
    pass

def subjects_from_params(params):
    if params['subject']:
        all_subjs = [p.load(params['subject'])]
    else:
        all_subjs = p.subjects(tags=params['tag'],label=params['label'],experiment=params['experiment'])
    return all_subjs

def padre_list(args):
    (params,listable,unidentified_args) = identify_params(args,True)
    
    if listable==None:
        error('Error: You didn\'t tell me what you wanted to list!')
        return
    
    if getpass.getuser()==decompress('eNrLLcqvyk3MAwAMOAMF'):
        sys.stderr.write(_unic_bub_print('%s!!!' %listable.capitalize())+'\n\n')
    
    all_subjs = subjects_from_params(params)
    
    all_dsets = {}
    if listable=='metadata':
        if len(unidentified_args)>0:
            (all_dsets,unidentified_args) = identify_dsets(unidentified_args,all_subjs)
   
    if listable=='metadata':
        if len(all_dsets)==0:
            error('Error: To list meta-data, you need to give me the name of a dataset')
            return
        for dset in all_dsets:
            subj,sess,label,dset_dict,i = all_dsets[dset]
            for meta in dset_dict['meta']:
                print '\t'.join([dset,meta,dset_dict['meta'][meta]])
    
    if listable=='atlases':
        if args.quiet:
            print '\n'.join(p.atlases.keys())
        else:
            for atlas in p.atlases:
                print atlas,
                if 'space' in p.atlases[atlas]:
                    print ' (%s)' % p.atlases[atlas]['space'],
                if 'notes' in p.atlases[atlas]:
                    print ': ' + p.atlases[atlas]['notes'],
                print ''
    if listable=='subjects':
        print '\n'.join([str(x) for x in all_subjs])
        return
    if listable=='labels':
        labels = set(nl.flatten([[x._sessions[y]['labels'].keys() for y in x._sessions] for x in all_subjs]))
        print '\n'.join(labels)
        return
    if listable=='experiments':
        experiments = set(nl.flatten([[x._sessions[y]['experiment'] for y in x._sessions if 'experiment' in x._sessions[y]] for x in all_subjs]))
        experiments = [x for x in experiments if x!=None and x!='']
        print '\n'.join(experiments)
        return
    if listable=='tags':
        tags = set(nl.flatten([[x._sessions[y]['tags'] for y in x._sessions if 'tags' in x._sessions[y]] for x in all_subjs]))
        tags = [x for x in tags if x!=None and x!='']
        print '\n'.join(tags)
        return
    if listable=='sessions':
        if not params['subject']:
            error('Error: sorry, I need a subject to list their sessions')
        else:
            subj = p.load(params['subject'])
            if subj:
                sessions = list(subj.sessions)
                sessions = [x for x in sessions if len(subj.dsets(session=x,tags=params['tag'],label=params['label'],experiment=params['experiment']))>0]
                print '\n'.join(sessions)
        return
    if listable=='dsets':
        if not params['subject']:
            error('Error: sorry, I need a subject to list their datasets')
        else:
            subj = p.load(params['subject'])
            if subj:
                dsets = subj.dsets(session=params['session'],tags=params['tag'],label=params['label'],experiment=params['experiment'])
                print '\n'.join([str(x) for x in dsets])
        return

def padre_link(args):
    (params,listable,unidentified_args) = identify_params(args)
    
    if not params['subject']:
        error('Error: You at least need to give me a subject!')
    subj = p.load(params['subject'])
    if not subj:
        error('Error: Couldn\'t load subject %s' % params['subject'])
    dsets = subj.dsets(session=params['session'],tags=params['tag'],label=params['label'],experiment=params['experiment'])
    for dset in dsets:
        try:
            os.symlink(str(dset),os.path.basename(str(dset)))
        except OSError:
            pass

def padre_add_meta(args):
    (params,listable,unidentified_args) = identify_params(args,True)
    all_subjs = subjects_from_params(params)
    (all_dsets,unidentified_args) = identify_dsets(unidentified_args,all_subjs)
    if len(all_dsets)!=1:
        error('Error: To add meta-data, you need to give me the name of exactly one dataset')
    (subj,sess,label,dset,i) = all_dsets[0]
    subj._sessions[sess][label][i]['meta'][args.meta_type] = os.path.basename(args.filename)
    shutil.copy(args.filename,os.path.join(p.sessions_dir(subj),sess))
    print 'Added %s (%s) to %s' % (os.path.basename(args.filename),args.meta_type,str(subj))
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet','-q',action='store_true',help='just print the bare information (good for scripts)')
    
    specify_group = parser.add_argument_group(title='explicitly specify object',description='(certain commands are also able to parse fuzzy keyword arguments)')
    specify_group.add_argument('-s','--subject',help='subject id')
    specify_group.add_argument('-n','--session',help='session identifier, by convention date of the scanning session in the format YYYYMMDD, but could really be any unique string')
    specify_group.add_argument('-t','--tag',help='session tag')
    specify_group.add_argument('-l','--label',help='label for dataset (the type of dataset; anatomy, sdtones)')
    specify_group.add_argument('-e','--experiment',help='experiment identifier')
    subparsers = parser.add_subparsers(title='commands')
    
    parser_info = subparsers.add_parser('info',help='get details on a single object')
    parser_info.add_argument('something',nargs='*',help='keywords identifying what you want')
    parser_info.set_defaults(func=padre_info)
    
    parser_list = subparsers.add_parser('list',help='retrieve a list of things')
    parser_list.add_argument('something',nargs='*',help='keywords identifying all the things you want')
    parser_list.set_defaults(func=padre_list)
    
    parser_link = subparsers.add_parser('link',help='create symbolic links in the current directory to datasets matching the given parameters')
    parser_link.add_argument('something',nargs='*',help='keywords identifying the datasets you want')
    parser_link.set_defaults(func=padre_link)
    
    parser_add_meta = subparsers.add_parser('add_meta',help='attach a file as metadata to a dataset')
    parser_add_meta.add_argument('meta_type',help='keyword to identify the metadata file')
    parser_add_meta.add_argument('filename',help='filename of meta file you\'d like to add')
    parser_add_meta.add_argument('something',nargs='*',help='keywords identifying all the things you want')
    parser_add_meta.set_defaults(func=padre_add_meta)
    
    args = parser.parse_args()
    args.func(args)
