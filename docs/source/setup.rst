How to use this library
=========================

Recommended Method
--------------------

Since python is a great language, and there are lots of convenient functions in this library for
working with the data, the recommended method for accessing the data is including the library
in your python scripts.

Doing this is simple, you just need to make sure python can find it. For example, if your analysis
is in a directory called ``Analyses/test_analysis`` (i.e., two directory levels in from the root
of the library directory). As long as you run your scripts from that directory,
you can just add the following code at the top of any script to import the library::

	import sys
	sys.path.append("../..")
	
	import padre

The first two lines tell Python to search two directories up for any modules, then you simply import
the library

Alternatively, if you want to make it more "robust" (e.g., to be able to run the script from any
location), you can specify the absolute location relative to the location of the script. For example,
if you keep your scripts in a directory called ``Analyses/test_analysis/scripts``, the following
code can also be used to include the padre library::

	import sys,os
	sys.path.append(os.path.abspath(os.path.join(__file__,'..','..','..')))
	
	import padre

Not as pretty, but more stable and portable. ``__file__`` is a Python reference to the filename of
the current script. Joining three ``..``'s moves you up three directories, and using ``os.path.abspath``
provides the absolute path, which will be valid from any relative location.

The Not-Recommended Method
---------------------------

If you hate Python, kittens, and love, there are several command-line-ready scripts that will print
out raw lists of subjects and datasets for use in any way that you please. In this scenario, you can
write a script in c-shell and awk, and just make a single call to the padre library script at the top to
give you your list of subjects or datasets.