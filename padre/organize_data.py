import os,subprocess
import filecmp
import re
import padre

data_dir = os.path.join(padre.padre_root,'Data')
subdirs = ['sessions','raw','analyses','clinical','other']

def max_diff(dset_a,dset_b):
	for dset in [dset_a,dset_b]:
		if not os.path.exists(dset):
			raise IOError('Could not find file: %s' % dset)
	try:
		with open(os.devnull,'w') as null:
			return float(subprocess.check_output(['3dBrickStat','-max','3dcalc( -a %s -b %s -expr abs(a-b) )' %(dset_a,dset_b)],stderr=null))
	except subprocess.CalledProcessError:
		return float('inf')

def make_subdirs(subj):
	for d in subdirs:
		full_d = os.path.join(data_dir,subj,d)
		if not os.path.exists(full_d):
			os.makedirs(full_d)

def dirs_from_tree(dirname):
	dirs = []
	for root, subdirs, files in os.walk(dirname):
		for d in subdirs:
			full_dir = os.path.join(root,d)
			if any([os.path.isfile(os.path.join(full_dir,x)) for x in os.listdir(full_dir)]):
				dirs.append(full_dir)
	return dirs

def dirs_equal(dirs):
	try:
		first_dir = dirs[0]
		other_dirs = list(dirs)
		del(other_dirs[other_dirs.index(first_dir)])
		for root, dirs, files in os.walk(first_dir):
			common_root = root[len(first_dir):]
			other_roots = [os.path.join(x,common_root) for x in other_dirs]
			this_content = os.listdir(root)
			other_contents = [os.listdir(x) for x in other_roots]
			if not all([len(this_content)==len(x) for x in other_contents]):
				return False
			for f in this_content:
				if not all([filecmp.cmp(os.path.join(root,f),os.path.join(x,f),False) for x in other_roots]):
					return False
	except OSError:
		return False
	return True

label_map = {
	'storymath': ['story[\W_]*math'],
	'sdtones': ['s[md][\W_]*tones', 'fmri_tones', '[1-9]time'],
	'prep': ['3_plane_loc_', 'ASSET_CALIBRATION_', 'practice'],
	'anatomy': ['spgr', 'AX_3D_', 'anat'],
	'field_map': ['Ax_GRE'],
	'dti': ['dti'],
	'flair': ['flair'],
	'rest': ['rest'],
	'text': ['text_[0-9]'],
	'semphon': ['semphon'],
	'defname': ['def[\W_]name', 'dn\d', 'dn_run'],
	'aphname': ['aphname']
}

def categorize_dset(dset):
	standard_form = re.match(r'.*ep.\d+-\d+_\d+-(.*?)(\d+_reps)?(_\d+rows)?.nii.gz',dset)
	if standard_form:
		label = standard_form.group(1)
		for d in label_map:
			for m in label_map[d]:
				if re.search(m,label,re.IGNORECASE):
					return d

def scan_subjects_dir():
	for subject_id in os.listdir(padre.data_dir):
		subj = padre.Subject.create(subject_id)
		for session in os.listdir(padre.sessions_subject_dir(subj)):
			if session not in subj.sessions:
				subj.new_session(session)
				try:
					if str(int(session))==session:
						subj.sessions[session]['date'] = session
				except ValueError:
					pass
			already_found_dsets = []
			for set_type in subj.sessions[session]['sets']:
				already_found_dsets += subj.sessions[session]['sets'][set_type]
			for dset in sorted(os.listdir(os.path.join(padre.sessions_subject_dir(subj),session))):
				if dset not in already_found_dsets:
					type_guess = categorize_dset(dset)
					if type_guess:
						if type_guess not in subj.sessions[session]['sets']:
							subj.sessions[session]['sets'][type_guess] = []
						subj.sessions[session]['sets'][type_guess].append(dset)
		subj.save()
	

def find_dup_sessions():
	''' find sessions that are complete duplicates and delete them
	
	**Not complete**'''
	raise Exception('This function is not complete')
	for subj in p.subjects():
	    for sess in subj.sessions:
	        if sum([len(subj.sessions[sess]['labels'][x]) for x in subj.sessions[sess]['labels']])==0:
	            continue
	        matches = dict(subj.sessions)
	        del(matches[sess])
	        for label in subj.sessions[sess]['labels']:
	            for dset in subj.sessions[sess]['labels'][label]:
	                loop_matches = list(matches)
	                for other_dir in loop_matches:
	                    match = False
	                    try:
	                        for other_label in subj.sessions[other_dir]['labels']:
	                            for other_dset in subj.sessions[other_dir]['labels'][other_label]:
	                                d = org.max_diff(os.path.join(p.sessions_subject_dir(subj),sess,dset),os.path.join(p.sessions_subject_dir(subj),other_dir,other_dset))
	                                if d<1.0:
	                                    match = True
	                                    raise ValueError
	                    except ValueError:
	                        pass
	                    if not match:
	                        del(matches[other_dir])
	        if matches:
	            print '%s: %s is duplicated within %s' % (subj,sess,matches.keys()[0])

if __name__=='__main__':
	import sys
	label = categorize_dset(sys.argv[1])
	print '%s: %s' % (label,sys.argv[1])
	
# find un-JSON'ed files
# create/update JSON with guesses
# print unknown labels
# scan raw for dups, del them
# autocreate each session
# label autocreated sessions