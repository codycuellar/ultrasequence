"""
PARSING
=======
This module contains functions and classes for parsing files and directories
for file sequences.
"""
import logging
import os
import sys
from os import walk
from ultrasequence.config import CONFIG as cfg
from ultrasequence.models import File, Sequence


logger = logging.getLogger(__name__)


if sys.version_info < (3, 5):
	try:
		from scandir import walk
	except ImportError:
		logger.warning('For Python versions < 3.5, scandir module is '
		               'recommended for faster directory parsing. Run:'
		               '\n>>> pip install scandir')


def scan_dir(path):
	"""
	Searches a root directory and returns a list of all files. If 
	cfg.recurse is True, the scanner will descend all child directories.

	:param str path: The root path to scan for files.
	:return: A list of filenames if cfg.get_stats is False, or a list
			 of tuples (filename, file_stats) if cfg.get_stats is True.
	"""
	file_list = []
	if cfg.recurse:
		for root, dirs, files in walk(path):
			file_list += stat_files(root, files)
	else:
		file_list += stat_files(path, os.listdir(path))
	return file_list


def stat_files(root, files):
	"""
	Assembles a list of files for a single directory.

	:param str root: The the root path to the current directory.
	:param list files: The list of filenames in the directory.
	:return: a list of filenames if cfg.get_stats is False, or a list
			 of tuples (filename, file_stats) if cfg.get_stats is True.
	"""
	dir_list = []
	if cfg.get_stats:
		for file_ in files:
			abspath = os.path.join(root, file_)
			# TODO: For links, copy the stat from source, but set size to 0
			# if os.path.islink(abspath):
			# 	continue
			dir_list.append((abspath, os.stat(abspath)))
	else:
		dir_list += [os.path.join(root, file_) for file_ in files
					 if os.path.isfile(os.path.join(root, file_))]
	return dir_list


class Parser(object):
	"""
	The main parser class which handles all data parsing and sorting. It
	can parse a text file with file names, or it can scan a directory on
	a locally mounted volume. It handles include/exclude patterns, and
	controls weather to get stats from a file on disk or not. Once the
	parser has run, it will populate five important attributes:

		Parser.sequences
			A list of sequence objects with two or more frames.
		Parser.orphan_frames
			Any sequences of files that were only one frame long.
		Parser.no_frame_numbers
			Files that could not be parsed for frame numbers, thus could
			not be sequenced.
		Parser.excluded
			Files with extensions that are either not in the include list
			if one exists, or that are in the exclude list.
		Parser.collisions
			If ignore_padding is used when setting up the parser, it is
			possible that two files attempt to insert into the same sequence,
			for instance, file.001.dpx and file.01.dpx will be treated as
			frame 1 of sequence file.#.dpx, therefor the second frame that
			is found that already exists in the matching sequence will get
			added to collisions.

	>>> from ultrasequence import Parser
	>>> include = ['tif', 'jpg', 'dpx', 'exr']
	>>> parser = Parser(include_exts=include, ignore_padding=True)
	>>> parser.parse_directory('~/Desktop', recures=True)
	>>> print(parser)
	'Parser(sequences=2, orphan_frames=10, no_frame_numbers=5,
	excluded=10, collisions=0)'
	"""

	def __init__(self, include_exts=cfg.include_exts,
	             exclude_exts=cfg.exclude_exts, get_stats=cfg.get_stats,
	             ignore_padding=cfg.ignore_padding):
		"""
		Main parser class. Sets up config parameters for parsing methods.
		
		:param list include_exts: file extensions to include in parsing
		:param list exclude_exts: file extensions to explicitly exclude in
		                          parsing
		:param bool get_stats: get file stats from os.stats
		:param bool ignore_padding: ignore the number of digits in the
		                            file's frame number section
		"""
		if not include_exts or not isinstance(include_exts, (tuple, list)):
			self.include_exts = set()
		else:
			self.include_exts = set(include_exts)

		if not exclude_exts or not isinstance(exclude_exts, (tuple, list)):
			self.exclude_exts = set()
		else:
			self.exclude_exts = set(exclude_exts)

		cfg.get_stats = get_stats
		self.ignore_padding = ignore_padding
		self._reset()

	def _reset(self):
		""" Clear and init all parser results. """
		self._sequences = {}
		self.sequences = []
		self.orphan_frames = []
		self.no_frame_numbers = []
		self.excluded = []
		self.collisions = []
		self.parsed = False

	def __str__(self):
		return ('Parser(sequences=%d, orphan_frames=%d, no_frame_numbers=%d, '
				'excluded=%d, collisions=%d)' %
				(len(self.sequences), len(self.orphan_frames),
				 len(self.no_frame_numbers), len(self.excluded),
				 len(self.collisions)))

	def __repr__(self):
		return ('<Parser object at %s, parsed=%s>' %
				(hex(id(self)), self.parsed))

	def _cleanup(self):
		""" Moves single frames out of sequences list. """
		while self._sequences:
			seq = self._sequences.popitem()[1]
			if seq.frames == 1:
				self.orphan_frames.append(seq[0])
			else:
				self.sequences.append(seq)
		self.parsed = True

	def _sort_file(self, filepath, stats=None):
		""" Finds matching sequence for given filepath. """
		file_ = File(filepath, stats=stats)

		if self.include_exts and file_.ext.lower() not in self.include_exts \
				or file_.ext.lower() in self.exclude_exts:
			self.excluded.append(file_)

		elif file_.frame is None:
			self.no_frame_numbers.append(file_)

		else:
			seq_name = file_.get_seq_key()
			if seq_name in self._sequences:
				try:
					self._sequences[seq_name].append(file_)
				except IndexError:
					self.collisions.append(file_)
			else:
				self._sequences[seq_name] = Sequence(file_)

	def parse_directory(self, directory, recurse=cfg.recurse):
		"""
		Parse a directory on the file system.

		:param str directory: Directory path to scan on filesystem.
		:param bool recurse: Recurse all child directories.
		"""
		self._reset()
		cfg.recurse = recurse
		directory = os.path.expanduser(directory)
		if isinstance(directory, str) and os.path.isdir(directory):
			file_list = scan_dir(directory)
			while file_list:  # reduce memory consumption for large lists
				file_ = file_list.pop(0)
				if cfg.get_stats:
					self._sort_file(file_[0], file_[1])
				else:
					self._sort_file(file_)
			self._cleanup()
		else:
			logger.warning('%s is not an available directory.' % directory)

	def parse_file(self, input_file):
		"""
		Parse a text file containing file listings.

		:param str input_file: Path to the file containing a file listing.
		"""
		input_file = os.path.expanduser(input_file)

		self._reset()
		if isinstance(input_file, str) and os.path.isfile(input_file):
			with open(input_file, 'r') as file_list:
				for file_ in file_list:
					self._sort_file(file_.rstrip())
			self._cleanup()
		else:
			logger.warning('%s is not a valid filepath.' % input_file)
