.. padre documentation master file, created by
   sphinx-quickstart on Tue Jan 21 13:57:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PaDRe (Patient Data Repository) documentation!
===========================================================

This library provides an organized way to store and analyze imaging data.

The :doc:`setup` page explains the basics on how to use the library, and the
:doc:`padre` and :doc:`subject` pages have the documentation for all of the functions you'll need.

If you're interested in the nuts and bolts of the library, :doc:`organization`
explains the internals of the library, and :doc:`installation` explains how to
setup a new repository or client machine.

Here are a couple quick examples to get you started, and more full-length examples in :doc:`examples`:
	
.. tip:: 
	Loop through all the subjects and do something to all their datasets::
	
		import padre as p
	
		for subject in p.subjects():
			print 'Processing subject %s' % subject
			for dset in subject.dsets():
				do_something_to_a_dset(dset)

	Find all the subjects for a particular experiment and do something 
	to the functional task datasets::
		
		for subject in p.subjects('experiment-name'):
			for dset in subject.dsets('functional-task'):
				do_something_to_a_dset(dset)
		
	Find all subjects in an experiment and do something to all the anatomies that
	were collected in the same session as a functional task::
	
		for subject in p.subjects('experiment-name'):
			for session in subject.sessions:
				if len(subject.dsets('functional-task',session=session)):
					for dset in subject.dsets('anatomy',session=session):
						do_something_to_an_anatomy(dset)


The Contents
=============
.. toctree::
   :maxdepth: 2
   
   setup
   examples
   padre
   subject
   padre_buddy.py
   organization
   installation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

