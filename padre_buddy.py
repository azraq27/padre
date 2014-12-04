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

fuzzyness = 80

listable_objects = {
    'atlases': ['atlases','templates'],
    'subjects': ['subjects','patients'],
    'experiments': ['experiments', 'studies', 'study'],
    'labels': ['labels','types'],
    'sessions': ['sessions','scans','dates'],
    'dsets': ['dsets','datasets','runs','files']
}

all_subjects = [str(x) for x in p.subject._all_subjects]
all_labels = p.subject.tasks
all_attrs = p.subject.root_level_attrs


def report(miss):
    '''tries to keep a central list of all misses'''
    try:
        import urllib,urllib2
        data = {'miss':miss}
        data_enc = urllib.urlencode(data)
        urllib2.urlopen('http://wolflion.org/cgi-bin/report.py?%s' % data_enc)
    except:
        pass

def padre_get(args):
    subject_match = process.extractOne(args.something,all_subjects)
    if subject_match[1]>=fuzzyness:
        p.load(subject_match[0]).pretty_print()

def padre_list(args):
    possible_names = [x for s in listable_objects.values() for x in s]
    best_match = process.extractOne(args.something,possible_names)
    if best_match[1]<fuzzyness:
        report(args.something)
        nl.notify('I\'m sorry, I couldn\'t understand "%s"' %args.something)
        return
    if best_match[0]=='atlases':
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
    if best_match[0]=='subjects':
        print '\n'.join([str(x) for x in p.subjects(label=args.label,experiment=args.experiment)])
        return
    if best_match[0]=='labels':
        print '\n'.join(all_labels)
        return
    if best_match[0]=='experiments':
        print '\n'.join(p.subject.experiments)
        return
    if best_match[0]=='sessions' or best_match[0]=='dsets':
        if args.subject:
            subj = p.load(args.subject)
            if subj:
                if best_match[0]=='sessions':
                    print subj.sessions(label=args.label,experiment=args.experiment).keys()                    
                if best_match[0]=='dsets':
                    print subj.dsets(label=args.label,experiment=args.experiment)
        else:
            nl.notify('Error: you need to specify a subject to list sessions or dsets',level=nl.level.error)
        return
        
            

def read_neuropsych_from_excel(excel_file):
    '''read the neuropsych variables from an excel file
    
    assumes the format given in "ExampleNeuropsych.xlsx"
    if the file "metadata.json" exists, will use the following keys:
        :approved_columns:  list of names of columns that will be imported
        :column_transforms: dictionary containing column names as keys and string values
                            that will be executed as a ``lambda x: [value]`` to transform
                            the imported values
        :column_groups:     dictionary with keys as group names and values as lists of 
                            column names. Will import given column names under the attribute
                            group name
    '''
    data_row = lambda sheet,row: [sheet.cell(row=row,column=i+1).value for i in xrange(sheet.get_highest_column())]
    column_named = lambda header,row,name: row[header.index(name)]
    approved_columns = None
    column_transforms = None
    column_groups = None
    if os.path.exists(os.path.join(p.padre_root,'metadata.json')):
        with open(os.path.join(p.padre_root,'metadata.json')) as f:
            metadata = json.loads(f.read())
        if 'approved_columns' in metadata:
            approved_columns = metadata['approved_columns']
        if 'column_transforms' in metadata:
            column_transforms = metadata['column_transforms']
        if 'column_groups' in metadata:
            # in the JSON file they're listed as group->column, so invert that
            inverse_groups = metadata['column_groups']
            column_groups = {}
            for group in inverse_groups:
                for col in inverse_groups[group]:
                    column_groups[col] = group
    wb = openpyxl.load_workbook(excel_file)
    for sheet_name in wb.get_sheet_names():
        sheet = wb.get_sheet_by_name(sheet_name)
        if sheet.calculate_dimension() != 'A1:A1':
            # There's some data in this worksheet
            header = data_row(sheet,1)
            import_cols = []
            for col in header:
                if col and col.lower()!='name' and col.lower()!='subject_id':
                    if approved_columns and col.lower() not in approved_columns:
                        nl.notify('Ignoring column: %s (not a designated column name)' % col,level=nl.level.warning)
                    else:
                        import_cols.append(col)
            for row_i in xrange(2,sheet.get_highest_row()+1):
                row = data_row(sheet,row_i)
                if ((isinstance(row[0],basestring) and row[0][0]=='#') or
                    ''.join([str(x) for x in row if x])==''):
                    # This row starts with a "#" or doesn't contain any data
                    continue
                subject_id = column_named(header,row,'subject_id')
                if subject_id==None or subject_id=='':
                    nl.notify('No subject_id listed for the following row:\n\t%s' % '  '.join([str(x) for x in row]),level=nl.level.error)
                    continue
                s = p.Subject.load(subject_id)
                if s:
                    with nl.notify('Importing for subject %s' % s):
                        for col in import_cols:
                            data = column_named(header,row,col)
                            if data!=None and data!='' and not (isinstance(data,basestring) and data.lower()=='na'):
                                if column_transforms and col in column_transforms:
                                    data = (lambda x: eval(column_transforms[col]))(data)
                                if column_groups and col in column_groups:
                                    nl.notify('setting %s.%s = %s' % (column_groups[col],col,repr(data)))
                                    if column_groups[col] not in dir(s):
                                        s.add_attr(column_groups[col])
                                    if not isinstance(getattr(s,column_groups[col]),dict):
                                        setattr(s,column_groups[col],{})
                                    getattr(s,column_groups[col])[col] = data
                                else:
                                    nl.notify('setting %s = %s' % (col,repr(data)))
                                    if col not in dir(s):
                                        s.add_attr(col)
                                    setattr(s,col,data)
                    s.save()
                else:
                    nl.notify('Couldn\'t find subject %s' % subject_id,level=nl.level.error)

def padre_create(args):
    if args.subject:
        subj = p.Subject.create(args.subject)
        subj.save()
        nl.notify('Creating new subject %s' % args.subject)
    else:
        nl.notify('Error: you need to specify a subject id',level=nl.level.error)

def padre_rename(args):
    if args.subject:
        subj = p.load(args.subject)
        if subj:
            try:
                os.rename(p.subject_dir(subj),p.subject_dir(args.new_name))
            except OSError:
                nl.notify('Error: filesystem reported error moving %s to %s' % (subj,args.new_name),level=nl.level.error)
            else:
                subj.subject_id = args.new_name
                subj.save()
                if os.path.exists(p.subject_json(args.new_name)):
                    try:
                        os.remove(os.path.join(p.subject_dir(args.new_name),'%s.json' % args.subject))
                    except OSError:
                        pass
                if args.deep:
                    subj.dsets.session_dict.session_dir = p.sessions_dir(args.new_name)
                    for dset in subj.dsets():
                        if args.subject in os.path.basename(dset):
                            new_name = os.path.join(os.path.dirname(dset),os.path.basename(dset).replace(args.subject,args.new_name))
                            try:
                                os.rename(dset,new_name)
                            except OSError:
                                nl.notify('Error: filesystem reported error moving %s to %s' % (dset,new_name),level=nl.level.error)                            
                nl.notify('Successfully renamed %s to %s' % (args.subject,args.new_name))
                if not args.deep:
                    nl.notify('(NOTE: none of the dataset names are changed in this process. Use "--deep" to change filenames)')
    else:
        nl.notify('Error: you need to specify a subject id to rename',level=nl.level.error)

def padre_add(args):
    if args.neuropsych:
        read_neuropsych_from_excel(args.neuropsych)

def padre_dir(args):
    if args.subject:
        print p.subject_dir(args.subject)
    else:
        nl.notify('Error: you need to specify a subject id to print their directory',level=nl.level.error)
    
def padre_json(args):
    if args.subject:
        print p.subject_json(args.subject)
    else:
        nl.notify('Error: you need to specify a subject id to print their JSON file',level=nl.level.error)

def padre_edit_session(args):
    pass

def padre_remove(args):
    pass

def padre_set(args):
    pass

def padre_report(args):
    pass

def padre_import(args):
    subject_guess = args.subject
    if subject_guess==None:
        subject_guess = os.path.basename(args.directory)
    import padre_demon
    padre_demon.import_archive(args.directory,subject_guess)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quiet','-q',action='store_true',help='just print the bare information (good for scripts)')
    specify_group = parser.add_argument_group(title='explicitly specify object',description='(certain commands are also able to parse fuzzy keyword arguments)')
    specify_group.add_argument('-s','--subject',help='subject id')
    specify_group.add_argument('-n','--session',help='session identifier, by convention date of the scanning session in the format YYYYMMDD, but could really be any unique string')
    specify_group.add_argument('-l','--label',help='label for dataset (the type of dataset; anatomy, sdtones)')
    specify_group.add_argument('-e','--experiment',help='experiment identifier')
    subparsers = parser.add_subparsers(title='commands')
    
    parser_get = subparsers.add_parser('get',help='retrieve one thing')
    parser_get.add_argument('something',nargs='*',help='keywords identifying what you want')
    parser_get.set_defaults(func=padre_get)
    
    parser_list = subparsers.add_parser('list',help='retrieve a list of things')
    parser_list.add_argument('something',nargs='*',help='keyword identifying all the things you want')
    parser_list.set_defaults(func=padre_list)
    
    parser_create = subparsers.add_parser('create',help='create a brand-new empty subject')
    parser_create.set_defaults(func=padre_create)
    
    parser_rename = subparsers.add_parser('rename',help='rename the specified subject to a new id')
    parser_rename.add_argument('new_name',help='new subject id')
    parser_rename.add_argument('--deep',action='store_true',help='also rename all of the datasets')
    parser_rename.set_defaults(func=padre_rename)
    
    parser_dir = subparsers.add_parser('dir',help='print the directory for a subject')
    parser_dir.set_defaults(func=padre_dir)
    
    parser_json = subparsers.add_parser('json',help='print the location of the JSON file for a subject')
    parser_json.set_defaults(func=padre_json)
    
    parser_add = subparsers.add_parser('add',help='add new data to an existing subject')
    parser_add.add_argument('-d','--dset',help='filename to dataset to add')
    parser_add.add_argument('-p','--neuropsych',help='filename to neuropsych file to add')
    parser_add.add_argument('-t','--scansheet',help='filename to PDF of scan sheet to add')
    parser_add.set_defaults(func=padre_add)
    
    parser_remove = subparsers.add_parser('remove',help='remove a file or dataset from a subject')
    parser_remove.add_argument('-d','--dset',help='dataset name to remove')
    parser_remove.add_argument('-p','--neuropsych',help='neuropsych name to remove')
    parser_remove.set_defaults(func=padre_remove)
    
    parser_set = subparsers.add_parser('set',help='set an attribute of a subject')
    parser_set.add_argument('attr_name',help='name of attribute')
    parser_set.add_argument('new_value',help='value to set')
    parser_set.set_defaults(func=padre_set)  
    
    parser_report = subparsers.add_parser('report',help='get database statistics')
    parser_report.add_argument('something',help='something identifying what you want')
    parser_report.set_defaults(func=padre_report)
    
    parser_import = subparsers.add_parser('import',help='manually import directory. If subject not explicitly set, will use directory name as subject id')
    parser_import.add_argument('directory',help='directory containing raw data to import')
    parser_import.set_defaults(func=padre_import)
    
    args = parser.parse_args()
    args.func(args)