import os
import re
import logging


logger = logging.getLogger()

FRAMENUM_RE = re.compile(r'((.*)(\D))?(\d+)(.*)')


def extract_frame(name):
	"""
	This function extracts the last set of digits in the string name and
	assumes it is the frame number when attempting to match with other file
	names. This function should be passed basenames only, so it doesn't
	attempt to sequence directory names.

	:param str name: file basename without dir  
	:return: 3-pair tuple consisting of the head (all characters preceding the
			 last set of digits, the frame number (last set of digits), and
			 tail (all digits succeeding the frame number).
	"""
	frame_match = re.match(FRAMENUM_RE, name)
	if frame_match:
		groups = frame_match.groups()
		head, frame, tail = groups[0], groups[3], groups[4]
	else:
		head, frame, tail = (name, '', '')
	if head is None:
		head = ''
	return head, frame, tail


def split_extension(filename):
	"""
	Splits the extension off the filename and returns a tuple of the 
	base filename and the extension.
	"""
	parts = filename.split('.')
	if len(parts) < 2:
		return parts[0], ''
	ext = parts.pop(-1)
	head = '.'.join(parts)
	return head, ext


class Stat(object):
	"""
	This class mocks object returned by os.stat on Unix platforms.
	"""
	def __init__(self, size=None, inode=None, ctime=None, mtime=None,
				 atime=None, mode=None, dev=None, nlink=None, uid=None,
				 gid=None):
		self.st_size = size
		self.st_ino = inode
		self.st_nlink = nlink
		self.st_dev = dev
		self.st_mode = mode
		self.st_uid = uid
		self.st_gid = gid
		self.st_ctime = ctime
		self.st_mtime = mtime
		self.st_atime = atime

	def __getattr__(self, item):
		ints = ['st_size', 'st_ino', 'st_nlink', 'st_dev', 'st_mode',
				'st_uid', 'st_gid']
		floats = ['st_ctime', 'st_mtime', 'st_atime']
		try:
			if item in ints:
				return int(super(Stat, self).__getattribute__(item))
			elif item in floats:
				return float(super(Stat, self).__getattribute__(item))
		except TypeError:
			return None


class File(object):
	def __init__(self, filepath, stats=None, get_stats=False):
		"""
		Class which represents single files or frames on disk.
		
		:param str filepath: the absolute filepath of the file
		"""
		self.abspath = filepath
		self.path, self.name = os.path.split(filepath)
		self._base, self.ext = split_extension(self.name)

		parts = extract_frame(self._base)
		head, self._framenum, tail = parts
		self.head = os.path.join(self.path, head)
		self.tail = '.'.join([tail, self.ext])
		self.padding = len(self._framenum)

		try:
			if get_stats:
				try:
					self.stat = os.stat(filepath)
				except FileNotFoundError:
					logger.info("File %s not found. Can't stat." % filepath)
					raise TypeError
			elif isinstance(stats, os.stat_result):
				self.stat = stats
			elif isinstance(stats, dict):
				self.stat = Stat(**stats)
			elif isinstance(stats, (list, tuple)):
				self.stat = Stat(*stats)
			else:
				raise TypeError
		except TypeError:
			self.stat = Stat()

	def __str__(self):
		return self.abspath

	def __repr__(self):
		return "File('%s')" % self.abspath

	@property
	def frame(self):
		try:
			return int(self._framenum)
		except ValueError:
			return None

	@property
	def frame_as_str(self):
		return self._framenum

	@property
	def size(self):
		try:
			return int(self.stat.st_size)
		except TypeError:
			return

	@property
	def inode(self):
		try:
			return int(self.stat.st_ino)
		except TypeError:
			return

	@property
	def nlink(self):
		try:
			return int(self.stat.st_nlink)
		except TypeError:
			return

	@property
	def dev(self):
		try:
			return int(self.stat.st_dev)
		except TypeError:
			return

	@property
	def mode(self):
		try:
			return int(self.stat.st_mode)
		except TypeError:
			return

	@property
	def uid(self):
		try:
			return int(self.stat.st_uid)
		except TypeError:
			return

	@property
	def gid(self):
		try:
			return int(self.stat.st_gid)
		except TypeError:
			return

	@property
	def ctime(self):
		try:
			return float(self.stat.st_ctime)
		except TypeError:
			return

	@property
	def mtime(self):
		try:
			return float(self.stat.st_mtime)
		except TypeError:
			return

	@property
	def atime(self):
		try:
			return float(self.stat.st_atime)
		except TypeError:
			return

	def get_seq_key(self, padding=False):
		if not self._framenum:
			digits = ''
		elif padding:
			digits = '%%0%dd' % self.padding
		else:
			digits = '#'
		return self.head + digits + self.tail


class Sequence(object):
	def __init__(self, file=None, force_consistent_padding=False):
		"""
		Class representing a sequence of matching filenames. The frames
		are stored in a dicitonary with the frame numbers as keys. Sets
		are used for fast operations in calculating missing frames.
		
		:param file: File object or filename string to base the object
			instantiation off of.
		:param bool force_consistent_padding: Setting to True will disallow
			new frames from being appended if the frame padding differs.
		"""
		self._frames = {}
		self.seq_name = ''
		self.head = ''
		self.tail = ''
		self.ext = ''
		self.padding = 0
		self.inconsistent_padding = False
		self.force_consistent_padding = force_consistent_padding
		if file is not None:
			self.append(file)

	def __str__(self):
		return self.seq_name

	def __repr__(self):
		return "Sequence('%s', frames=%d)" % (self.seq_name, self.frames)

	def __iter__(self):
		return iter([self._frames[frame] for frame in self._frames])

	def __getitem__(self, frames):
		if isinstance(frames, slice):
			return [self._frames[x] for x in
					range(frames.start, frames.stop, frames.step)]
		elif isinstance(frames, (tuple, list)):
			return [self._frames[x] for x in frames]
		return self._frames[frames]

	@property
	def frames(self):
		return len(self._frames)

	@property
	def implied_frames(self):
		return self.end - self.start + 1

	@property
	def start(self):
		return min(self._frames)

	@property
	def end(self):
		return max(self._frames)

	@property
	def is_missing_frames(self):
		return self.frames != self.implied_frames

	@property
	def missing_frame_count(self):
		return self.end - (self.start - 1) - self.frames

	@property
	def size(self):
		try:
			return sum([file.size for file in self])
		except TypeError:
			return

	def get_missing_frames(self):
		expected = set(range(self.start, self.end + 1))
		actual = set(self._frames)
		return expected - actual

	def append(self, file):
		"""
		Append a new frame to the sequence.
		 
		:param file: File object or string to append to Sequence
		"""
		if not isinstance(file, File):
			if isinstance(file, str):
				file = File(file)
				if len(self._frames) > 0 and file.get_seq_key(
						self.force_consistent_padding) != self.seq_name:
					raise ValueError('%s is not a member of %s. Not appending.'
									 % (file, repr(self)))
		if file.frame is None:
			raise ValueError('%s is not a sequencable item.' % str(file))
		if not self.frames:
			self.head = file.head
			self.tail = file.tail
			self.ext = file.ext
			self.padding = file.padding
			self.seq_name = file.get_seq_key(self.force_consistent_padding)
		if file.frame in self._frames:
			raise IndexError('%s already in sequence as %s' %
						   (file.name, self._frames[file.frame]))
		self._frames[file.frame] = file
		if self.padding < file.padding:
			self.inconsistent_padding = True
			self.padding = file.padding


def make_sequences(*filelist, include_exts=None, get_stats=False,
				   force_consistent_padding=False):
	"""
	This function takes a list of filename path strings and attempts
	to build sequence items out of groups of files in the same path
	with the same naming structure.

	:param filelist: list of filenames to process. These can have different
	:param include_exts: 
	:param force_consistent_padding: 
	:return: 
	"""
	if not include_exts:
		include_exts = set()
	else:
		set(include_exts)

	# if not stats:
	# 	stats = {}

	sequences = {}
	non_sequences = []
	excluded = []

	for file in filelist:
		if isinstance(file, str):
			_file = File(file, get_stats=get_stats)
		elif isinstance(file, (tuple, list)) and len(file) == 2:
			_file = File(*file, get_stats=get_stats)
		if include_exts and _file.ext not in include_exts:
			excluded.append(_file)
		elif _file.frame is None:
			non_sequences.append(_file)
		else:
			seq_name = _file.get_seq_key(force_consistent_padding)
			if seq_name not in sequences:
				sequences[seq_name] = Sequence(_file, force_consistent_padding)
			else:
				try:
					sequences[seq_name].append(_file)
				except IndexError:
					excluded.append(_file)

	sequences = [sequences[seq] for seq in sequences]
	non_sequences += [sequences.pop(i)[seq.start] for i, seq in
					  reversed(list(enumerate(sequences))) if seq.frames == 1]

	return sequences, non_sequences, excluded
