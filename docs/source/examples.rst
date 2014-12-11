Examples of usage
===================

Here are some "real-life" examples of how I would process data. I also use the `neural <https://github.com/azraq27/neural>` library
for a lot of my processing, so you'll see it pop up here as well.

In these examples, my experiment is called "HitHeads" and it has two conditions: "hard" and "soft".

First, preprocess the data::

	import padre as p
	import neural as nl
	
	# Get me a list of subject objects for my experiment
	subjects_list = p.subjects('HitHeads')
	
	# Learning the "default argument" and "named argument" syntax of Python is important
	# This line is the same as the previous one:
	subjects_list = p.subjects(experiment='HitHeads')
	
	for subj in subjects_list:
		# Loop through the subjects
		anatomy = subj.dsets('anatomy')[0]
		# Since I want to align all of the epis together, I want to collect them in a list:
		epis = []
		for condition in ['hard','soft']:
			epis += subj.dsets(condition)
		# If you're a sharp Python programmer, you'll realize I also could have done:
		epis = [x for y in [subj.dsets(a) for a in ['hard','soft]] for x in y]
		# or maybe more readibly...
		epis = nl.flatten([subj.dsets(a) for a in ['hard','soft]])
		
		# Now we have our anatomy and a list of our epis, so align them!
		nl.afni.align_anat_epi(anatomy,epis)

Next, deconvolve::

	import padre as p
	import neural as nl
	
	# this is the name of a stimfile that we made somewhere else
	stimfile_name = lambda dset: '%s-stimfile.1D' % dset
	
	# Same as before, but just a one-liner
	for subj in p.subjects('HitHeads'):
		# for the details on the decon function, see the neural library
		decon = nl.afni.Decon()
		# Here's another way to get our epis. Not as "slick",
		# but maybe a little more readible
		decon.input_dsets = subj.dsets('hard') + subj.dsets('soft')
		decon.stim_files = [stimfile_name(dset) for dset in [subj.dsets('hard') + subj.dsets('soft')]]
		decon.prefix = "%s-headhit_firstpass" % subj
		decon.run()