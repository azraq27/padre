padre - PaDRe Library Functions
================================

Global Functions
------------------

Several functions are available at the root-level of the library, the most important of which
is the :meth:`padre.subjects` function (which is a shortcut to the function :meth:`padre.subject.subjects`)

.. automethod:: padre.subject.subjects

Once you have the subject objects, you can play with them using the methods in :doc:`subject`

Extra Stuff
-------------

.. autodata:: padre.config.atlases
	:annotation:

.. autodata:: padre.config.stimfiles
	:annotation:

Directory and File Locations
-----------------------------

.. automodule:: padre.config


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

		

	