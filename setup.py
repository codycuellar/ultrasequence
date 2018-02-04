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
	copyright=COPYRIGHT,
	description=DESCRIPTION,
	keywords='sequence file parser image ultra frames',
	platforms=['MacOS 10.10', 'MacOS 10.11', 'MacOS 10.12'],
	python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
	install_requires=[],
	entry_points={
		'console_scripts': [
			'findseq=ultrasequence.bin.findseq:main'
		]
	}
)
