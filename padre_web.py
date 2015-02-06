#!/usr/bin/env python
import padre as p
import neural as nl
import bottle
from bottle import route,view,run,post,static_file,request,redirect,error
import datetime
from dateutil.parser import parse
from fuzzywuzzy import process
import sys,os
import padre.matching
import HTMLParser
h = HTMLParser.HTMLParser()

app = application = bottle.Bottle()

import imp
c = imp.load_source('padre_config',os.path.join(p.padre_root,'padre_config.py'))

web_view_root = os.path.join(sys.prefix,'padre_web')
if not os.path.exists(web_view_root):
    # Debian reports sys.prefix as '/usr', but places files in '/usr/local'
    web_view_root = os.path.join(sys.prefix,'local','padre_web')

os.chdir(web_view_root)

@app.route('/style/<filename>')
def style_file(filename):
    return static_file('views/style/%s'%filename,'.')

@app.route('/favicon.ico')
def favicon():
    return static_file('views/favicon.ico','.')

@app.route('/view_file/<subject>/<session>/<filename>')
def view_file(subject,session,filename):
    return static_file(os.path.join('Data',subject,'sessions',session,filename),root=p.padre_root)

@app.route('/')
@app.route('/index')
@view('index')
def index():
    return {'experiments':sorted(p.subject.experiments,key=lambda x: x.lower())}
    

@app.route('/list_subjects')
@app.post('/list_subjects')
@view('list_subjects')
def subjects():
    exp = request.forms.get('exp')
    if exp!='':
        subjects = p.subjects(experiment=exp)
    else:
        subjects = p.subjects()
    
    unverified = []
    for subj in subjects:
        try:
            for sess in subj._sessions:
                if 'unverified' in subj._sessions[sess]:
                    unverified.append(subj)
                    raise StopIteration
        except StopIteration:
            pass
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
            'experiments':sorted(p.subject.experiments,key=lambda x: x.lower())
    }

@app.route('/edit_subject/<subject_id>')
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
        'sessions':sorted(sessions),
        'unverified':sorted(unverified),
        'experiments':sorted(p.subject.experiments,key=lambda x: x.lower())        
    }

@app.post('/save_subject')
def save_subject():
    old_subject_id = request.forms.get('old_subject_id').rstrip('/')
    new_subject_id = request.forms.get('subject_id').rstrip('/')
    if p.subject.subject_exists(new_subject_id):
        with p.maint.commit_wrap():
            p.maint.merge(old_subject_id,new_subject_id)
    else:
        with p.maint.commit_wrap():
            p.maint.rename(old_subject_id,new_subject_id)
    p.subject._index_one_subject(new_subject_id)
    if old_subject_id in p.subject._all_subjects:
        del(p.subject._all_subjects[old_subject_id])
    redirect('/edit_subject/%s' % new_subject_id)

@app.route('/edit_subject/<subject_id>/<session>')
@view('edit_session')
def edit_session(subject_id,session):
    subject = p.load(subject_id)
    return {
        'subject':subject,
        'session':session,
        'labels':sorted(p.subject.tasks,key=lambda x: x.lower()),
        'experiments':sorted(p.subject.experiments,key=lambda x: x.lower()),
        'tags': sorted(p.subject.tags,key=lambda x: x.lower())
    }

@app.post('/save_subject/<subject_id>/<session>')
@view('save_session')
def save_session(subject_id,session):
    with p.maint.commit_wrap():
        subj = p.load(subject_id)
        subj._sessions[session]['date'] = parse(request.forms.get("date")).strftime("%Y-%m-%d")
        experiment = request.forms.get("experiment")
        if experiment=='none':
            experiment = None
        if experiment=='new':
            experiment = request.forms.get("new_experiment_text")
            p.subject.experiments.add(experiment)
        subj._sessions[session]['experiment'] = experiment
        tag = request.forms.get("new_tag")
        if tag and tag!='':
            p.subject.tags.add(tag)
            if 'tags' not in subj._sessions[session]:
                subj._sessions[session]['tags'] = []
            subj._sessions[session]['tags'].append(tag)
        scan_sheet = request.files.get("scan_sheet")
        if scan_sheet != None:
            subj._sessions[session]['scan_sheet'] = scan_sheet.filename
            scan_sheet.save(os.path.join(p.sessions_dir(subj),session))
        subj._sessions[session]['notes'] = request.forms.get("notes")
        subj._sessions[session]['include'] = True if request.forms.get("include") else False
        for dset in subj.dsets(session=session,include_all=True):
            dset_fname = dset.__str__(False)
            i = [x['filename'] for x in subj._sessions[session]['labels'][dset.label]].index(dset_fname)
            subj._sessions[session]['labels'][dset.label][i]['complete'] = True if request.forms.get('complete_%s'%dset_fname) else False
            dset.complete = subj._sessions[session]['labels'][dset.label][i]['complete']
            label = request.forms.get('label_%s' % dset_fname)
            if label:
                if dset.label!=label:
                    if label=='new':
                        label = request.forms.get('label_%s_new' % dset_fname)
                        p.subject.tasks.add(label)
                        if label not in subj._sessions[session]['labels']:
                            subj._sessions[session]['labels'][label] = []
                    del(subj._sessions[session]['labels'][dset.label][i])
                    if len(subj._sessions[session]['labels'][dset.label])==0:
                        del(subj._sessions[session]['labels'][dset.label])
                    if label not in subj._sessions[session]['labels']:
                        subj._sessions[session]['labels'][label] = []
                    subj._sessions[session]['labels'][label].append(dset.__dict__())
            add_meta = request.files.get('add_meta_%s' % dset_fname)
            if add_meta:
                meta_type = request.forms.get('meta_type_%s'%dset_fname)
                subj._sessions[session]['labels'][dset.label][i]['meta'][meta_type] = add_meta.filename
                add_meta.save(os.path.join(p.sessions_dir(subj),session))
        if 'unverified' in subj._sessions[session]:
            del(subj._sessions[session]['unverified'])
        subj.save()
        p.subject._all_subjects[str(subj)] = subj
        new_subj_id = request.forms.get("new_subject_id")
        if new_subj_id and new_subj_id!='':
            # create_subject will load the subject if it already exists...
            new_subj = p.maint.create_subject(new_subj_id)
            if new_subj:
                p.maint.merge_session(subj,new_subj,session)
                subj.save()
                new_subj.save()
                p.subject._index_one_subject(subj)
                p.subject._index_one_subject(new_subj)
                subj = new_subj
        else:
            p.subject._index_one_subject(subj)
    redirect('/edit_subject/%s/%s' % (subj,session))
    
@app.route('/delete_tag/<subject>/<session>/<tag>')
def delete_tag(subject,session,tag):
    subj = p.load(subject)
    if subj:
        if 'tags' in subj._sessions[session] and tag in subj._sessions[session]['tags']:
            del(subj._sessions[session]['tags'][subj._sessions[session]['tags'].index(tag)])
        subj.save()
    redirect('/edit_subject/%s/%s' % (subject,session))

@app.post('/search_form')
@view('list_subjects')
def search_form():
    search_string = request.forms.get('search_field')

    args = padre.matching.bottle.parse_string(search_string)
    subjects = padre.matching.filter_subjs(p.subjects(),args)
    unverified = []
    for subj in subjects:
        for sess in subj._sessions:
            if 'unverified' in subj._sessions[sess]:
                unverified.append(subj)
    subjects = list(set(subjects) - set(unverified))
    
    return {
            'subjects':subjects,
            'unverified':unverified,
            'experiments':sorted(p.subject.experiments,key=lambda x: x.lower())
    }


if __name__ == '__main__':
    import socket
    p._include_all = True
    p.subjects()
    if 'web_server' in dir(c):
        run(server=c.web_server,host=c.web_hostname,port=c.web_port)
    else:
        run(host=c.web_hostname,port=c.web_port)
