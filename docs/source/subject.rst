padre.subject - Subject Objects
=================

.. currentmodule:: padre.subject
.. autoclass:: Subject
	
**Loading a subject from the disk:**

	.. automethod:: Subject.load

	*Standard instance variables:*
	
		.. autoinstanceattribute:: Subject.subject_id
			:annotation:
		
		.. autoinstanceattribute:: Subject.include
			:annotation:
		
		.. autoinstanceattribute:: Subject.notes
			:annotation:
		
			

Accessing Datasets
--------------------

	Datasets can be accessed several ways. Each of these methods deliver the filenames, organized
	in different ways. All datasets are stored in the directory returned by :meth:`padre.sessions_subject_dir`.

	.. currentmodule:: padre.subject
	
	.. class:: Subject
		
		.. autoinstanceattribute:: sessions
			:annotation:
	
		.. warning::
	
			The following two shortcut methods(``subject.labels`` and ``subject.dsets``) are convenient
			but don't cover every possibility. For example, if the anatomy scan for a functional session
			was lost, but there is another anatomy scan obtained at another date, these datasets will 
			appear normally as ``subject.labels['functional']`` and ``subject.labels['anatomy']`` with
			no reference to the fact that they were obtained in different sessions. If you write your
			script session-centric, you can explicitly address these exception cases.
	
		.. autoinstanceattribute:: labels
			:annotation:
	
		.. autoinstanceattribute:: dsets
			:annotation:
	

		
Session Format
-----------------

Sessions are stored as simple dictionaries, but have a standard format. In addition to the
"standard" data listed here, there may also be extra meta-data added in particular subjects

Sessions are usually labeled by the date, although the actual label is arbitrary, and should
not be relied upon. Sessions should always include:

	.. data:: session['date']
	
		The session date stored as a standard string of format "YYYY-MM-DD"
		
	.. data:: session['type']
	
		A descriptive label to classify this session, like "preop" or "postop"
	
	.. data:: session['labels']
	
		A dictionary containing all of the datasets, organized by descriptive label.
		
		*Example*::
		
			{
				'anatomy': [
					'anatomy-dset.nii.gz'
				],
				'functional': [
					'functional-dset-1.nii.gz',
					'functional-dset-2.nii.gz'
				]
			}

Helper Methods
----------------

These methods are designed to make manipulating the data a little easier

	.. automethod:: Subject.session_for_label

Maintenance Functions
----------------------

These functions require write-access to the repository, so should not be used in standard scripts

	.. automethod:: Subject.create
	.. automethod:: Subject.save
	.. automethod:: Subject.add_attr
	.. automethod:: Subject.new_session
	.. automethod:: Subject.init_directories
	
	