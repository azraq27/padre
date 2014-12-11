padre - PaDRe Library Functions
================================

.. automodule:: padre

Global Functions
------------------

Several functions are available at the root-level of the library, the most important of which
is the :meth:`padre.subjects` function (which is a shortcut to the function :meth:`padre.subject.subjects`)

.. currentmodule:: padre

	.. automethod:: subjects

Using this list, it is easy to filter again to find a specific subset of subjects. For example,
to get a list of all subjects who have had a left ATL surgery::

	subjects = [s for s in padre.subjects() if s.meta['clinical']['surgery_type']=='left atl']

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
		.. automethod:: padre.config.raw_dir
		.. automethod:: padre.config.sessions_dir

	.. automethod:: padre.config.subject_json

		

	