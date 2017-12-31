import os
from os import walk
from ultrasequence import File, Sequence, Stat
from ultrasequence import config as cfg
import logging


logger = logging.getLogger()


def add_files(root, files):
	dir_list = []
	if cfg.get_stats:
		for file in files:
			abspath = os.path.join(root, file)
			if os.path.islink(abspath):
				continue
			dir_list.append((abspath, os.stat(abspath)))
	else:
		dir_list += [os.path.join(root, file) for file in files]
	return dir_list


def get_files_in_directory(path, recurse=True):
	file_list = []
	if recurse:
		for root, dirs, files in walk(path):
			file_list += add_files(root, files)
	else:
		file_list += add_files(path, os.listdir)
	return file_list


def map_stats(stat_order, stats):
	if not len(stat_order) == len(stats):
		raise ValueError('Stat order and stats not the same length.')
	return dict(zip(stat_order, stats))


class Parser(object):
	def __init__(self, include_exts=None, exclude_exts=None,
				 get_stats=cfg.get_stats, ignore_padding=cfg.ignore_padding):
		cfg.get_stats = get_stats
		cfg.ignore_padding = ignore_padding
		if not include_exts:
			self.include_exts = set()
		else:
			self.include_exts = set([ext.lower() for ext in include_exts])
		self._reset()

	def _reset(self):
		self._sequences = {}
		self.sequences = []
		self.single_frames = []
		self.non_sequences = []
		self.excluded = []
		self.collisions = []
		self.parsed = False

	def __str__(self):
		return ('Parser(sequenced=%d, single_frames=%d, non_sequenced=%d, '
				'excluded=%d, collisions=%d)' %
				(len(self.sequences), len(self.single_frames),
				 len(self.non_sequences), len(self.excluded),
				 len(self.collisions)))

	def __repr__(self):
		return ('<Parser object at %s, parsed=%s>' %
				(hex(id(self)), self.parsed))

	def _cleanup(self):
		while self._sequences:
			seq = self._sequences.popitem()[1]
			if seq.frames == 1:
				self.single_frames.append(seq)
			else:
				self.sequences.append(seq)
		self.parsed = True

	def _sort_file(self, file_, stats=None):
		file_ = File(file_, stats=stats)

		if self.include_exts and file_.ext.lower() not in self.include_exts:
			self.excluded.append(file_)

		elif file_.frame is None:
			self.non_sequences.append(file_)

		else:
			seq_name = file_.get_seq_key()
			if seq_name in self._sequences:
				try:
					self._sequences[seq_name].append(file_)
				except IndexError:
					self.collisions.append(file_)
			else:
				self._sequences[seq_name] = Sequence(file_)

	def parse_directory(self, directory, recurse=True):
		"""
		Parse a directory on the file system.

		:param str directory:
		:param bool recurse:
		:return:
		"""
		self._reset()
		if isinstance(directory, str) and os.path.isdir(directory):
			file_list = get_files_in_directory(
				directory, recurse)
			while file_list:  # reduce memory consumption for large lists
				file_ = file_list.pop(0)
				if cfg.get_stats:
					self._sort_file(file_[0], file_[1])
				else:
					self._sort_file(file_)
			self._cleanup()
		else:
			logger.warning('%s is not an available directory.' % directory)

	def parse_file(self, filepath, csv=False, csv_sep=cfg.csv_sep,
				stat_order=None):
		"""
		Parse a text csv or text file containing file listings.

		:param filepath:
		:return:
		"""
		# test for proper stats names
		if stat_order:
			Stat(dict((x, None) for x in stat_order))

		self._reset()
		if isinstance(filepath, str) and os.path.isfile(filepath):
			with open(filepath, 'r') as file_list:
				for file_ in file_list:
					if csv:
						file_ = file_.rstrip().split(csv_sep)
						filename = file_[0]
						if cfg.get_stats:
							stats = map_stats(stat_order, file_[1:])
							self._sort_file(filename, stats)
						else:
							self._sort_file(filename)
					else:
						self._sort_file(file_.rstrip())
			self._cleanup()
		else:
			logger.warning('%s is not a valid filepath.' % filepath)

	# def parse_list(self, file_list):
	# 	"""
	# 	Parse a list of files.
	#
	# 	:param file_list:
	# 	:return:
	# 	"""
	# 	pass