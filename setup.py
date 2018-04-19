"""
Ultrasequence is a highly efficient Python image sequencer. It will parse
a list or directory of filenames and sequence any files that share a common
name with incremental frame numbers. It comes with a command line tool and is
highly customisable. It operates much faster than most other tools due to it's
use of key matching rather than recursively searching existing sequences for
matches. It's speed should be roughly O(n).
"""
from setuptools import setup, find_packages
import os


packagedir = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(packagedir, 'ultrasequence', 'version.py'), 'r') as v:
	exec(v.read(), globals())


setup(
	packages=find_packages(),
	name=NAME,
	version=__version__,
	author=AUTHOR,
	author_email=EMAIL,
	package_dir={'ultrasequece': 'ultrasequence'},
	url=URL,
	license=LICENSE,
	description=DESCRIPTION,
	long_description=open('readme.rst').read(),
	keywords='sequence file parser image ultra frames',
	platforms=['MacOS 10.10', 'MacOS 10.11', 'MacOS 10.12', 'MacOS 10.13'],
	python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
	install_requires=[],
	entry_points={
		'console_scripts': [
			'findseq=ultrasequence.bin.findseq:main'
			]
		}
	)
