padre_buddy.py - Your friendly command-line helper
===================================================

This script was created as a blending of my desire to make a very easy, user-friendly script,
my interest in artificial intelligence, and my loose grip on reality. The result is a sometimes
amazing, sometimes broken script.

Usage:
----------

padre_buddy.py [action_word] [direct_objects] [modifiers]

The syntax is very loose. The library tries to match each word to a known concept. It will try to correct for
simple spelling errors and has an internal dictionary of synonyms as well.

Actions (currently working):

	:list:		Currently the most useful. Try to match a direct object and
			list all of them that match the modifiers. For example, if the
			direct object was "dsets" and the modifier was "subject-4", it
			would print out all of the datasets for "subject-4"
	:link:		Will find all datasets matching the given modifiers and
			create symbolic links within the current working directory. Useful
			if you want to "play" with the data without moving it out of Padre
			or using really long filenames

Direct Objects:

	* Atlases
	* Subjects
	* Experiments
	* Labels
	* Tags
	* Sessions
	* Dsets
	* Metadata
	* Edat, Eprime-txt

Example of command line usage::

	padre_buddy.py list subjects ExperimentName
	
	padre_buddy.py list labels
	
	padre_buddy.py list dsets subject_one task_name


Example of script usage (although CSH burns my eyes...)::

	#!/bin/csh

	echo 'Running the weird, crazy, padre machine to try to figure out where the heck my data is...'

	set subject = "11334"
	set task = "sdtones"

	set dsets = `padre_buddy.py list dsets $task $subject`

	if( "$dsets" == "" ) then
		echo 'AHHH! No DATA! '
		echo ''
		echo 'Did you make sure everything looks good in Padre Web? '
		echo '...'
		echo '...'
		exit
	endif

	echo ''
	echo 'Ok... phew. Found the data. Now I can return to the sanity of CSH'
	echo ''
	echo 'First SDT dataset:'
	echo $dsets[1]

	echo '...and the second:'
	echo $dsets[2]

	echo ''
	echo 'not necessarily in chronological order'