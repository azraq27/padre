.. padre documentation master file, created by
   sphinx-quickstart on Tue Jan 21 13:57:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PaDRe (Patient Data Repository) documentation!
===========================================================

This library provides an organized way to query patient data libraries.

At a minimum, read the :doc:`organization` page to orient yourself to the 
directory structure and :doc:`setup`.

.. tip:: 
	A quick usage example to get you started::
	
		import padre
	
		for subject in padre.subjects():
			print 'Processing subject %s' % subject
			for dset in subject.dsets():
				do_something_to_a_dset(dset)


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

