from distutils.core import setup
setup(
  name = 'padre',
  packages = ['padre'], # this must be the same as the name above
  version = '0.3',
  description = 'patient data repository',
  long_description = '''PaDRe - a patient data repository library (in Python)
--------------------------------------------------------

This library is used to organize a large data repository of imaging data. The functions
consist of several helper functions that make accessing the data easier, and contain 
meta-data about subjects

Documentation: http://padre.readthedocs.org
''',
  author = 'Bill Gross',
  author_email = 'bill.gross@me.com',
  url = 'https://github.com/azraq27/padre',
  download_url = 'https://github.com/azraq27/padre/tarball/0.5',
  keywords = ['neuroimaging', 'afni', 'fsl', 'fmri'],
  classifiers = [
      'Topic :: Scientific/Engineering',
      'Intended Audience :: Science/Research',
      'Development Status :: 3 - Alpha'
  ]
)