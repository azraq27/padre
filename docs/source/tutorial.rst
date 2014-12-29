Usage tutorial
================

This is a quick run-through of how you might analyze a dataset. First, we need to import the library::

	import padre as p

Data organization
-------------------

Here's the organization of our sample data:

	:Name of experiment:	Exp1
	:Types of datasets:	anatomy, flair, task1, task2

We'll process all the data in a subdirectory of our home directory ``~/Exp1``. The datasets are named:

	:raw data:	``[subject].run[#].nii.gz``
	:anatomy:	``[subject].anat.nii.gz``
	:stim files:	``[subject].[task].1D``
	
Get the subject list
----------------------

The easiest way to get the list of subjects is to organize them by experiment, and get them by calling :meth:`padre.subjects`::

	# Return all subjects who have a session labeled with experiment "Exp1"
	subjects = p.subjects('Exp1')
	# The same thing, using keyword arguments
	subjects = p.subjects(experiment='Exp1')

If you want to get any subject with who has any runs of the task ``task1``, you could use this instead::

	subjects = p.subjects(label='task1')

Or, you could keep a list of subject numbers the old fashion way, and load them individually::

	subjects = []
	with open('subjects.txt') as f:
		for line in f.readlines():
			subj = p.load(line.strip())
			if subj:
				subjects.append(subj)

Preprocess data
-----------------

Now that we have our list of subjects, we can loop through the data and run some preprocessing functions on them::

	import neural as nl
	
	for subj in subjects:
		# The dsets function will return the datasets we're interested in.
		# The first argument is the dset label, but you could also specify
		# session parameters like tags or session name
		anatomy = subj.dsets('anatomy')[0]
		# The "[0]" needs to be there because dsets() always returns a list
		epis = subj.dsets('task1') + subj.dsets('task2')
		# epis now is a list of all of the task1 and task2 datasets
		# run the "align_epi_anat.py" script (using the neural library)
		nl.afni.align_epi_anat(anatomy,epis)