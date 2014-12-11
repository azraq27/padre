How to use this library
=========================

Accessing the data
--------------------

Recommended Method
	Since Python is a great language, and the library provides a lot of convenience functions for you, 
	the recommended method for accessing the data is using Python scripts that directly include the
	library. It's terribly easy. Just import the library in any script, and get going.
	
	.. highlight::
	
		import padre as p
	
	Since it's just a Python library, it can be imported from anywhere, and all of the file references
	are absolute, so it doesn't matter what folder you are in. Take a look at the functions and examples 
	here for fun things to do with the library.

The Not-Recommended Method
	If you hate Python, kittens, and love, you could write all of your scripts in some awful language,
	like C shell + awk, and lookup the location of the data using the command-line script :doc:`padre_buddy.py <padre_buddy.py>`.
	The :doc:`padre_buddy.py <padre_buddy.py>` script is really designed to help you have quick access to 
	the datasets on the command line, and wasn't meant to be a crutch to hold you back from migrating to Python. But, it's
	there if you need it.

Basic workflow concepts
-------------------------

The raw data is stored within padre, and is accessible from anywhere through the library functions. For efficiency, it's 
not recommended to copy the raw data out of 