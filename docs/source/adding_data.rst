How to add new data to the database
=======================================

Step 1: Double-check the subject ID
-------------------------------------

	The automatic system tries to name the subject and all of the files using the subject ID that
	the scanner tech used in the DICOM files. If that isn't the actual subject ID, then you can change
	it with this (replacing old_id and new_id)::
	
		 padre_buddy -s old_id rename new_id

Step 2: Label each dataset
-------------------------------------

	The system will try to guess the appropriate label
	
Step 3: Mark any incomplete datasets
-------------------------------------

	The system always tries to keep all data (even incomplete datasets), but if you don't want them used in
	analyses, you need to label them as "incomplete"