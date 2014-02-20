padre - PaDRe Library Functions
==========================

.. automodule:: padre

Global Functions
------------------

Several functions are available at the root-level of the library, the most important of which
is the :meth:`padre.subjects` function, which is a shortcut to the function :meth:`padre.subject.subjects`

.. automethod:: subject.subjects

Using this list, it is easy to filter again to find a specific subset of subjects. For example,
to get a list of all subjects who have had a left ATL surgery::

	subjects = [s for s in padre.subjects() if s.surgery_type=='left atl']

Helper Functions
------------------

The following functions are also imported to the root level to make using them easier. 
For example, :meth:`padre.utils.run` can be called as :meth:`padre.run`

	:meth:`padre.utils.run`
	
	:meth:`padre.utils.run_in`
	
	:meth:`padre.utils.flatten`

Directory and File Locations
-----------------------------

.. automodule:: padre.config
	
	*Directories:*
	
		.. autodata:: padre_root
			:annotation:
	
		.. autodata:: data_dir
			:annotation:
	
		.. autodata:: analyses_dir
			:annotation:
		
		.. automethod:: padre.config.subject_dir		
		.. automethod:: padre.config.raw_subject_dir
		.. automethod:: padre.config.sessions_subject_dir

	.. automethod:: padre.config.subject_json

		

	