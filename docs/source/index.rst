.. padre documentation master file, created by
   sphinx-quickstart on Tue Jan 21 13:57:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PaDRe (Patient Data Repository) documentation!
===========================================================

This library provides an organized way to query patient data libraries.

At a minimum, read the :doc:`organization` page to orient yourself to the 
directory structure and :doc:`setup`. For instructions on how to install
the system and setup client machines, see :doc:`installation`

A couple quick examples to get you started:
	
.. tip:: 
	Loop through all the subjects and do something to all their datasets::
	
		import padre as p
	
		for subject in p.subjects():
			print 'Processing subject %s' % subject
			for dset in subject.dsets:
				do_something_to_a_dset(dset)

	Find all the subjects for a particular experiment and do something 
	to the functional task datasets::
		
		for subject in p.subjects('experiment-name'):
			# This usage will give us the first session with complete
			# data that contains a dataset that is labeled 'functional-task'
			with session in subject.sessions(label='functional-task'):
				for dset in session['labels']['functional-task']:
					do_something_to_a_dset(dset)
	
	Find all subjects in an experiment and do something to the anatomy that
	was collected in the same session as a functional task::
	
		for subject in p.subjects('experiment-name'):
			with session in subject.sessions(label='functional-task'):
				for dset in session['labels']['anatomy']:
					do_something_to_an_anatomy(dset)


The Contents
=============
.. toctree::
   :maxdepth: 2
   
   setup
   organization
   padre
   subject

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

