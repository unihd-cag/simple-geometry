from sys import path

path.insert(0, '..')
from setup import version as package_version


project = 'Simple Geometry'
copyright = '2019, Niels Buwen'
author = 'Niels Buwen'
version = package_version
release = version

extensions = ['sphinx.ext.intersphinx', 'sphinx.ext.autodoc']

autoclass_content = 'both'
autodoc_member_order = 'bysource'
set_type_checking_flag = True
always_document_param_types = True

templates_path = ['_templates']
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'

html_static_path = []
