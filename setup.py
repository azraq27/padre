from distutils.core import setup

version = '2.3'

setup(
  name = 'padre',
  packages = ['padre'],
  scripts = ['padre_demon.py','padre_web.py','padre_buddy.py'],
  data_files = [
      ('padre_web/views',[
          "views/header.stpl",
          "views/footer.stpl",
          "views/sidebar.stpl",
          "views/index.stpl",
          "views/list_subjects.stpl",
          "views/edit_session.stpl", 
          "views/edit_subject.stpl",
          "views/favicon.ico"
      ]),
      ('padre_web/views/style',[
          "views/style/back.png",
          "views/style/bullet.png",
          "views/style/datepicker.css",
          "views/style/footer.png",
          "views/style/graphic.png",
          "views/style/link.png",
          "views/style/search.png",
          "views/style/side_back.png",
          "views/style/side_base.png",
          "views/style/side_top.png",
          "views/style/style.css",
          "views/style/tab.png",
          "views/style/tab_selected.png"
      ])
  ],
  version = version,
  description = 'participant data repository',
  long_description = '''PaDRe - a participant data repository library (in Python)
--------------------------------------------------------

This library is used to organize a large data repository of imaging data. The functions
consist of several helper functions that make accessing the data easier, and contain 
meta-data about subjects

Documentation: http://padre.readthedocs.org
''',
  author = 'Bill Gross',
  author_email = 'bill.gross@me.com',
  url = 'https://github.com/azraq27/padre',
  download_url = 'https://github.com/azraq27/padre/tarball/%s' % version,
  keywords = ['neuroimaging', 'afni', 'fsl', 'fmri'],
  classifiers = [
      'Topic :: Scientific/Engineering',
      'Intended Audience :: Science/Research',
      'Development Status :: 3 - Alpha'
  ],
  install_requires=[
      'neural-fmri',
      'pydicom',
      'fuzzywuzzy',
      'python-Levenshtein',
      'openpyxl',
      'gini'
  ]
)