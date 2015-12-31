#!/usr/bin/env python
'''straight-forward importing program using argparse parameters'''
import padre as p
import neural as nl
import argparse,os,shutil

parser = argparse.ArgumentParser()

parser.add_argument("subject")
parser.add_argument("session")
parser.add_argument("-t","--tag",nargs='*')
parser.add_argument("-e","--experiment")
parser.add_argument("--date")
parser.add_argument("--scan-sheet")
parser.add_argument("-l","--label")
parser.add_argument("-d","--dsets",nargs='*')
parser.add_argument("-m","--meta",nargs='*')
parser.add_argument("-r","--raw")
parser.add_argument("--verify",help="automatically accept datasets as verified",action='store_true')

args = parser.parse_args()

with p.maint.commit_wrap():
    nl.notify('Loading subject %s' % args.subject)
    subj = p.maint.create_subject(args.subject)
    if args.session not in subj.sessions:
        nl.notify('Creating new session (%s)' % args.session)
        p.maint.new_session(subj,args.session)
    
    sess = subj._sessions[args.session]

    if args.experiment:
        nl.notify('Setting experiment to %s' % args.experiment)
        sess['experiment'] = args.experiment

    if args.tag:
        nl.notify('Adding tags: %s' % repr(args.tag))
        if 'tags' not in sess:
                sess['tags'] = []
        sess['tags'] += args.tag

    if args.date:
        nl.notify('Setting date to %s' % args.date)
        sess['date'] = args.date

    if args.verify:
        sess['unverified'] = False
    else:
        sess['unverified'] = True
    
    subj.save()

sess_dir = os.path.join(p.sessions_dir(subj),args.session)
if args.scan_sheet:
    if os.path.exists(args.scan_sheet):
        with p.maint.commit_wrap():
            try:
                shutil.copy(args.scan_sheet,sess_dir)
                sess['scan_sheets'] = os.path.basename(args.scan_sheets)
            except:
                pass

if args.dsets:
    for i in xrange(len(args.dsets)):
        with p.maint.commit_wrap():
            dset = args.dsets[i]
            try:
                meta = args.meta[i]
            except:
                meta = None
            with nl.notify('Trying to add %s' % dset):
                if os.path.exists(dset) and dset not in [x.__str__(False) for x in subj.dsets(include_all=True)]:
                    dset_dict = {}
                    dset_dict['filename'] = os.path.basename(dset)
                    dset_dict['md5'] = nl.hash(dset)
                    dset_dict['complete'] = True
                    dset_dict['meta'] = {}
                    label = args.label
                    if label==None:
                        label = 'unsorted'
                    if label not in sess['labels']:
                        sess['labels'][label] = []
                    sess['labels'][label].append(dset_dict)
                    dset_fname = os.path.join(sess_dir,dset_dict['filename'])
                    nl.notify('copying dset')
                    if not os.path.exists(dset_fname):
                        shutil.copy(dset,dset_fname)
                if meta:
                    nl.notify('Warning: meta not implemented yet',level=nl.level.warning)
    subj.save()

if args.raw:
    try:
        shutil.copytree(args.raw,p.raw_dir(subj))
    except:
        pass