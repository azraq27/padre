from distutils.core import setup
setup(
  name = 'padre',
  packages = ['padre'],
  scripts = ['padre_demon.py','padre_web.py','padre_buddy.py'],
  data_files = [
      ('views',[
          "header.stpl",
          "footer.stpl",
          "sidebar.stpl",
          "index.stpl",
          "list_subjects.stpl",
          "edit_session.stpl", 
          "edit_subject.stpl",
          "favicon.ico"
      ]),
      ('views/style',[
          "back.png",
          "bullet.png",
          "datepicker.css",
          "footer.png",
          "graphic.png",
          "link.png",
          "search.png",
          "side_back.png",
          "side_base.png",
          "side_top.png",
          "style.css",
          "tab.png",
          "tab_selected.png"
      ])
  ],
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
  ],
  install_requires=[
      'neural-fmri',
      'pydicom'
  ]
)