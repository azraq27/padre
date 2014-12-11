#!/usr/bin/env python
# depends on:
#   neural
#   padre
#   fuzzywuzzy
#   openpyxl

import argparse,os,json
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
    'types': ['types'],
    'sessions': ['sessions','scans','dates'],
    'dsets': ['dsets','datasets','runs','files']
}

p.subjects()
all_subjects = p.subject._all_subjects.keys()
all_labels = p.subject.tasks
all_types = p.subject.types
all_experiments = p.subject.experiments

all_objects = [(x,'subject') for x in all_subjects] + [(x,'label') for x in all_labels] + [(x,'type') for x in all_types] + [(x,'experiment') for x in all_experiments]

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

def identify_object(obj):
    '''tries to match to an existing object
    returns a tuple of (object,object_id)'''
    best_match = process.extractOne(obj,[x[0] for x in all_objects])
    if best_match[1]>fuzzyness:
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

def padre_info(args):
    pass

def padre_list(args):
    global all_objects
    params = {'subject':args.subject,'session':args.session,'type':args.type,'experiment':args.experiment,'label':args.label}
    listable = None
    added_sessions = False
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
                error('Error: Sorry, I can\'t figure out what you mean by "%s"' % arg, arg)
                return
    
    if listable==None:
        error('Error: You didn\'t tell me what you wanted to list!')
        return
    
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
        print '\n'.join([str(x) for x in p.subjects(type=params['type'],label=params['label'],experiment=params['experiment'])])
        return
    if listable=='labels':
        print '\n'.join(all_labels)
        return
    if listable=='experiments':
        print '\n'.join(all_experiments)
        return
    if listable=='types':
        print '\n'.join(all_types)
        return
    if listable=='sessions':
        if not params['subject']:
            error('Error: sorry, I need a subject to list their sessions')
        else:
            subj = p.load(params['subject'])
            if subj:
                sessions = list(subj.sessions)
                sessions = [x for x in sessions if len(subj.dsets(session=x,type=params['type'],label=params['label'],experiment=params['experiment']))>0]
                print '\n'.join(sessions)
        return
    if listable=='dsets':
        if not params['subject']:
            error('Error: sorry, I need a subject to list their datasets')
        else:
            subj = p.load(params['subject'])
            if subj:
                dsets = subj.dsets(session=params['session'],type=params['type'],label=params['label'],experiment=params['experiment'])
                print '\n'.join([str(x) for x in dsets])
        return

def padre_link(args):
    global all_objects
    params = {'subject':args.subject,'session':args.session,'type':args.type,'experiment':args.experiment,'label':args.label}
    added_sessions = False
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
            error('Error: Sorry, I can\'t figure out what you mean by "%s"' % arg, arg)
            return
    if not params['subject']:
        error('Error: You at least need to give me a subject!')
    subj = p.load(params['subject'])
    if not subj:
        error('Error: Couldn\'t load subject %s' % params['subject'])
    dsets = subj.dsets(session=params['session'],type=params['type'],label=params['label'],experiment=params['experiment'])
    for dset in dsets:
        os.symlink(str(dset),os.path.basename(str(dset)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet','-q',action='store_true',help='just print the bare information (good for scripts)')
    
    specify_group = parser.add_argument_group(title='explicitly specify object',description='(certain commands are also able to parse fuzzy keyword arguments)')
    specify_group.add_argument('-s','--subject',help='subject id')
    specify_group.add_argument('-n','--session',help='session identifier, by convention date of the scanning session in the format YYYYMMDD, but could really be any unique string')
    specify_group.add_argument('-t','--type',help='session type')
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
    
    args = parser.parse_args()
    args.func(args)
