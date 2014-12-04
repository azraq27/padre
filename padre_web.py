#!/usr/bin/env python
import padre as p
from bottle import route,view,run,post,static_file,request,redirect
import datetime
from dateutil.parser import parse
from fuzzywuzzy import process
import sys,os

import imp
c = imp.load_source('padre_config',os.path.join(p.padre_root,'padre_config.py'))

web_view_root = os.path.join(sys.prefix,'padre_web')
if not os.path.exists(web_view_root):
    # Debian reports sys.prefix as '/usr', but places files in '/usr/local'
    web_view_root = os.path.join(sys.prefix,'local','padre_web')

os.chdir(web_view_root)

@route('/style/<filename>')
def style_file(filename):
    return static_file('views/style/%s'%filename,'.')

@route('/favicon.ico')
def favicon():
    return static_file('views/favicon.ico','.')

@route('/')
@route('/index')
@view('index')
def index():
    return {'experiments':p.subject.experiments}
    

@route('/list_subjects')
@view('list_subjects')
def subjects():
    exp = request.params.get('exp')
    print repr(exp)
    if exp!='':
        subjects = p.subjects(experiment=exp)
    else:
        subjects = p.subjects()
    
    unverified = []
    for subj in subjects:
        for sess in subj._sessions:
            if 'unverified' in subj._sessions[sess]:
                unverified.append(subj)
    subjects = list(set(subjects) - set(unverified))
    
    def sort_key(s):
        dates = sorted([parse(s._sessions[sess]['date']) for sess in s._sessions if 'date' in s._sessions[sess]])
        if len(dates):
            return dates[-1]
        else:
            return datetime.datetime(1,1,1)
    
#    sort_key = lambda x: sorted([parse(y[1]) for y in x[1]])[0] if len(x[1]) else datetime.datetime(1,1,1)
#    subjects = reversed(sorted([(str(s),[(sess,s.sessions[sess]['date']) for sess in s.sessions]) for s in p.subjects()],key=sort_key))
    return {
            'subjects':list(reversed(sorted(subjects,key=sort_key))),
            'unverified':list(reversed(sorted(unverified,key=sort_key))),
            'experiments':p.subject.experiments
    }

@route('/edit_subject/<subject_id>')
@view('edit_subject')
def edit_subject(subject_id):
    subject = p.load(subject_id)
    unverified = []
    for sess in subject._sessions:
        if 'unverified' in subject._sessions[sess]:
            unverified.append(sess)
    sessions = list(set(subject.sessions) - set(unverified))
    return {
        'subject':subject,
        'sessions':sessions,
        'unverified':unverified,
        'experiments':p.subject.experiments        
    }

@post('/save_subject')
def save_subject():
    old_subject_id = request.forms.get('old_subject_id')
    new_subject_id = request.forms.get('subject_id')
    return "%s -> %s" % (old_subject_id,new_subject_id)

@route('/edit_subject/<subject_id>/<session>')
@view('edit_session')
def edit_session(subject_id,session):
    subject = p.load(subject_id)
    return {
        'subject':subject,
        'session':session,
        'labels':p.subject.tasks,
        'experiments':p.subject.experiments,
        'types': p.subject.types
    }

@post('/save_subject/<subject_id>/<session>')
@view('save_session')
def save_session(subject_id,session):
    subj = p.load(subject_id)
    subj._sessions[session]['date'] = parse(request.forms.get("date")).strftime("%Y-%m-%d")
    experiment = request.forms.get("experiment")
    if experiment=='new':
        experiment = request.forms.get("new_experiment_text")
    subj._sessions[session]['experiment'] = experiment
    type = request.forms.get("type")
    if type=='none':
        type = None
    if type=='new':
        type = request.forms.get("new_type_text")
    subj._sessions[session]['type'] = type
    scan_sheet = request.files.get("scan_sheet")
    if scan_sheet != None:
        subj._sessions[session]['scan_sheet'] = scan_sheet.filename
#        scan_sheet.save(os.path.join(p.sessions_dir(subj),session))
    subj._sessions[session]['notes'] = request.forms.get("notes")
    subj._sessions[session]['include'] = True if request.forms.get("include") else False
    for dset in subj.dsets(session=session,include_all=True):
        dset_fname = dset.__str__(False)
        i = [x['filename'] for x in subj._sessions[session]['labels'][dset.label]].index(dset_fname)
        subj._sessions[session]['labels'][dset.label][i]['complete'] = True if request.forms.get('complete_%s'%dset_fname) else False
        dset.complete = subj._sessions[session]['labels'][dset.label][i]['complete']
        print dset.complete
        label = request.forms.get('label_%s' % dset_fname)
        if label:
            if dset.label!=label:
                if label=='new':
                    label = request.forms.get('label_%s_new' % dset_fname)
                    if label not in subj._sessions[session]['labels']:
                        subj._sessions[session]['labels'][label] = []
                del(subj._sessions[session]['labels'][dset.label][i])
                if len(subj._sessions[session]['labels'][dset.label])==0:
                    del(subj._sessions[session]['labels'][dset.label])
                subj._sessions[session]['labels'][label].append(dset.__dict__())
    if 'unverified' in subj._sessions[session]:
        del(subj._sessions[session]['unverified'])
    subj.save()
    redirect('/edit_subject/%s' % subj)
    

@post('/search_form')
@view('list_subjects')
def search_form():
    search_string = request.forms.get('search_field')
    matches = [x[0] for x in process.extract(search_string,[str(x) for x in p.subjects()]) if x[1]>90]
    subjects = [p.load(x) for x in matches]
    unverified = []
    for subj in subjects:
        for sess in subj._sessions:
            if 'unverified' in subj._sessions[sess]:
                unverified.append(subj)
    subjects = list(set(subjects) - set(unverified))
    
    return {
            'subjects':subjects,
            'unverified':unverified,
            'experiments':p.subject.experiments
    }

'''
@route('/<subject_id>')
@view('edit_subject')
def subject_list(subject_id):
    return {
        'subject_id': subject_id,
        'subj': p.load(subject_id)
    }

@route('/<subject_id>/<session>')
@view('edit_session')
def edit_session(subject_id,session):
    return {
        'subject_id': subject_id,
        'subj': p.load(subject_id),
        'session': session,
        'labels': p.subject.tasks
    }

@post('/save_session/<subject_id>/<session>')
def save_session(subject_id,session):
    new_subject_id = request.forms.get('new_subject_id')
    if new_subject_id!=subject_id:
        pass
'''
if __name__ == '__main__':
    import socket
    p._include_all = True
    p.subjects()
    run(host=c.web_hostname,port=c.web_port)