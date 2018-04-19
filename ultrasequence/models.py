"""
CORE DATA MODELS
================
Contains the core data structure models for sequencing files.
"""

import logging
import os
import re
from .config import CONFIG as cfg

try:
	FileNotFoundError
except NameError:
	FileNotFoundError = OSError


logger = logging.getLogger(__name__)


def extract_frame(name):
	"""
	This function by default extracts the last set of digits in the
	string name and assumes it is the frame number when returning the
	parts. It's a good idea to only pass basenames without extensions
	so it doesn't attempt to sequence directory names or digits in the
	extension.

	:param str name: File basename without dir or extension.
	:return: 3-pair tuple consisting of the head (all characters
	         preceding the last set of digits), the frame number
	         (last set of digits), and tail (all digits succeeding
	         the frame number).
	"""
	frame_match = re.match(cfg.frame_extract_re, name)
	if frame_match:
		groups = frame_match.groups()
		head, tail = groups[cfg.head_group], groups[cfg.tail_group]
		frame = groups[cfg.frame_group]
	else:
		head, frame, tail = (name, '', '')
	if head is None:
		head = ''
	return head, frame, tail


def split_extension(filename):
	"""
	Splits the extension off the filename and returns a tuple of the
	base filename and the extension (without the dot).
	
	:param str filename: The base filename string to split.
	:return: A tuple of the head (characters before the last '.') and
			 the extension (characters after the last '.').
	"""
	parts = filename.split('.')
	if len(parts) < 2:
		return parts[0], ''
	ext = parts.pop(-1)
	head = '.'.join(parts)
	return head, ext


def frame_ranges_to_string(frames):
	"""
	Take a list of numbers and make a string representation of the ranges.

	>>> frame_ranges_to_string([1, 2, 3, 6, 7, 8, 9, 13, 15])
	'[1-3, 6-9, 13, 15]'

	:param list frames: Sorted list of frame numbers.
	:return: String of broken frame ranges (i.e '[10-14, 16, 20-25]').
	"""
	if not frames:
		return '[]'
	if not isinstance(frames, list):
		frames = list(frames)
	frames.sort()

	# Make list of lists for each consecutive range
	ranges = [[frames.pop(0)]]
	current_range_index = 0  # index of current range
	for x in frames:
		if x - 1 == ranges[current_range_index][-1]:
			ranges[current_range_index].append(x)
		else:
			current_range_index += 1
			ranges.append([x])
	range_strings = []
	for x in ranges:
		if len(x) > 1:
			range_strings.append('-'.join([str(x[0]), str(x[-1])]))
		else:
			range_strings.append(str(x[0]))
	complete_string = '[' + ', '.join(range_strings) + ']'
	return complete_string


class Stat(object):
	"""
	This class mocks objects returned by os.stat on Unix platforms.
	This is useful for instance when working with offline lists where 
	you want to maintain the stat information from a previously parsed
	directory which the current machine does not have access to.
	"""

	def __init__(self, size=None, ino=None, ctime=None, mtime=None,
				 atime=None, mode=None, dev=None, nlink=None, uid=None,
				 gid=None):
		"""
		Refer to the docs for the the built-in os.stat module for more info.
		
		:param int size: File size in bytes.
		:param int ino: Inode number.
		:param float ctime: Unix change timestamp.
		:param float mtime: Unix modify timestamp.
		:param float atime: Unix access timestamp.
		:param int mode: Inode protection mode.
		:param int dev: Device inode resides on.
		:param int nlink: Number of links to the inode.
		:param int uid: User id of the owner.
		:param int gid: Group id of the owner.
		"""
		self.st_size = size
		self.st_ino = ino
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
	"""
	The class that represents a single file and all of it's Stat
	attributes if available. It contains attributes for the 
	various string parts of the path, base filename, frame number
	and extension. All Sequences are comprised of File objects.
	"""

	def __init__(self, filepath, stats=None, get_stats=None):
		"""
		Initalize a single File instance.

		:param str filepath: the absolute filepath of the file
		:param stats: dict or iterable to map Stat class or 
		              os.stat_result object.
		:param bool get_stats: True to attempt to call os.stat on
		                       the file. If file does not exist,
		                       revert back to applying stats values
		                       if they were supplied, else set stats
		                       to None.
		"""
		if get_stats is not None and isinstance(get_stats, bool):
			cfg.get_stats = get_stats
		self.abspath = filepath
		self.path, self.name = os.path.split(filepath)
		self._base, self.ext = split_extension(self.name)

		parts = extract_frame(self._base)
		self.namehead, self._framenum, tail = parts
		self.head = os.path.join(self.path, self.namehead)
		if not self.ext:
			self.tail = ''
		else:
			self.tail = '.'.join([tail, self.ext])
		self.padding = len(self._framenum)

		try:
			if get_stats:
				try:
					stats = os.stat(filepath)
				except FileNotFoundError:
					if stats is None:
						raise TypeError
			if isinstance(stats, os.stat_result):
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

	def __lt__(self, other):
		if isinstance(other, File):
			return self.frame < other.frame
		else:
			raise TypeError('%s not File instance.' % str(other))

	def __gt__(self, other):
		if isinstance(other, File):
			return self.frame > other.frame
		else:
			raise TypeError('%s not File instance.' % str(other))

	def __le__(self, other):
		if isinstance(other, File):
			return self.frame <= other.frame
		else:
			raise TypeError('%s not File instance.' % str(other))

	def __ge__(self, other):
		if isinstance(other, File):
			return self.frame >= other.frame
		else:
			raise TypeError('%s not File instance.' % str(other))

	def __eq__(self, other):
		if isinstance(other, File):
			return (self.head, self.frame, self.tail) == (other.head,
														  other.frame,
														  other.tail)
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, File):
			return (self.head, self.frame, self.tail) != (other.head,
														  other.frame,
														  other.tail)
		else:
			return True

	@property
	def frame(self):
		""" Integer frame number. """
		try:
			return int(self._framenum)
		except ValueError:
			return None

	@property
	def frame_as_str(self):
		""" Str frame number with padding matching original filename. """
		return self._framenum

	@property
	def size(self):
		""" Same as Stat.st_size if available, otherwise None. """
		if not self.stat.st_size:
			try:
				self.stat.st_size = os.stat(self.abspath).st_size
				return self.stat.st_size
			except FileNotFoundError:
				return
		else:
			return self.stat.st_size

	@property
	def inode(self):
		""" Same as Stat.st_ino if available, otherwise None. """
		if not self.stat.st_ino:
			try:
				self.stat.st_ino = os.stat(self.abspath).st_ino
				return self.stat.st_ino
			except FileNotFoundError:
				return
		else:
			return self.stat.st_ino

	@property
	def nlink(self):
		""" Same as Stat.st_nlink if available, otherwise None. """
		if not self.stat.st_nlink:
			try:
				self.stat.st_nlink = os.stat(self.abspath).st_nlink
				return self.stat.st_nlink
			except FileNotFoundError:
				return
		else:
			return self.stat.st_nlink

	@property
	def dev(self):
		""" Same as Stat.st_dev if available, otherwise None. """
		if not self.stat.st_dev:
			try:
				self.stat.st_dev = os.stat(self.abspath).st_dev
				return self.stat.st_dev
			except FileNotFoundError:
				return
		else:
			return self.stat.st_dev

	@property
	def mode(self):
		""" Same as Stat.st_mode if available, otherwise None. """
		if not self.stat.st_mode:
			try:
				self.stat.st_mode = os.stat(self.abspath).st_mode
				return self.stat.st_mode
			except FileNotFoundError:
				return
		else:
			return self.stat.st_mode

	@property
	def uid(self):
		""" Same as Stat.st_uid if available, otherwise None. """
		if not self.stat.st_uid:
			try:
				self.stat.st_uid = os.stat(self.abspath).st_uid
				return self.stat.st_gid
			except FileNotFoundError:
				return
		else:
			return self.stat.st_uid

	@property
	def gid(self):
		""" Same as Stat.st_gid if available, otherwise None. """
		if not self.stat.st_gid:
			try:
				self.stat.st_gid = os.stat(self.abspath).st_gid
				return self.stat.st_gid
			except FileNotFoundError:
				return
		else:
			return self.stat.st_gid

	@property
	def ctime(self):
		""" Same as Stat.st_ctime if available, otherwise None. """
		if not self.stat.st_ctime:
			try:
				self.stat.st_ctime = os.stat(self.abspath).st_ctime
				return self.stat.st_ctime
			except FileNotFoundError:
				return
		else:
			return self.stat.st_ctime

	@property
	def mtime(self):
		""" Same as Stat.st_mtime if available, otherwise None. """
		if not self.stat.st_mtime:
			try:
				self.stat.st_mtime = os.stat(self.abspath).st_mtime
				return self.stat.st_mtime
			except FileNotFoundError:
				return
		else:
			return self.stat.st_mtime

	@property
	def atime(self):
		""" Same as Stat.st_atime if available, otherwise None. """
		if not self.stat.st_atime:
			try:
				self.stat.st_atime = os.stat(self.abspath).st_atime
				return self.stat.st_atime
			except FileNotFoundError:
				return
		else:
			return self.stat.st_atime

	def get_seq_key(self, ignore_padding=None):
		"""
		Make a sequence global name for matching frames to correct
		sequences.

		:param bool ignore_padding: True uses '%0#d' format, else '#'
		:return: sequence key name (i.e. '/path/to/file.#.dpx')
		"""
		if ignore_padding is None or not isinstance(ignore_padding, bool):
			ignore_padding = cfg.ignore_padding
		if not self._framenum:
			digits = ''
		elif ignore_padding is True:
			digits = '#'
		elif ignore_padding is False:
			digits = '%%0%dd' % self.padding
		else:
			raise TypeError('ignore_padding argument must be of type bool.')
		return self.head + digits + self.tail


class Sequence(object):
	"""
	Class representing a sequence of matching file names. The frames
	are stored in a dictionary with the frame numbers as keys. Sets
	are used for fast operations in calculating missing frames.

	This class's usage of dictionaries and sets is the core of the
	speed of this program. Rather than recursively searching existing
	sequences, the file key gnerated from File.get_seq_key() is used to
	instantly match the sequence it belongs to.
	"""

	def __init__(self, frame_file=None, ignore_padding=None):
		"""
		Initialize an image Sequence instance.

		:param File or str frame_file: File object or filename string to
		                         initialze a File object from.
		:param bool ignore_padding: True to allow inconsistent padding
		                            as same sequence, False to treat
		                            as separate sequences.
		"""
		if ignore_padding is not None and isinstance(ignore_padding, bool):
			cfg.ignore_padding = ignore_padding
		self._frames = {}
		self.seq_name = ''
		self.path = ''
		self.namehead = ''
		self.head = ''
		self.tail = ''
		self.ext = ''
		self.padding = 0
		self.inconsistent_padding = False
		if frame_file is not None:
			self.append(frame_file)

	def __str__(self):
		return self.format(cfg.format)

	def __repr__(self):
		return "Sequence('%s', frames=%d)" % (
			self.format(cfg.format), self.frames)

	def __len__(self):
		return len(self._frames)

	def __iter__(self):
		return iter([self._frames[frame] for frame in self._frames])

	def __getitem__(self, frames):
		all_frames = list(sorted(self._frames))
		if isinstance(frames, slice):
			return [self._frames[f] for f in sorted(self._frames)][frames]
		return self._frames[all_frames[frames]]

	def __lt__(self, other):
		if isinstance(other, str):
			return self.seq_name < other
		else:
			return self.seq_name < other.seq_name

	@property
	def abspath(self):
		""" Full sequence path name (i.e. '/path/to/file.#.dpx'). """
		return self.seq_name

	@property
	def name(self):
		""" The base sequence name without the path (i.e 'file.#.dpx'). """
		return os.path.basename(self.seq_name)

	@property
	def start(self):
		""" Int of first frame in sequence. """
		return min(self._frames)

	@property
	def end(self):
		""" Int of last frame in sequence. """
		return max(self._frames)

	@property
	def frames(self):
		""" Int of total frames in sequence. """
		return len(self)

	@property
	def frame_numbers(self):
		""" List of frame ints in sequence. """
		return list(sorted(self._frames))

	@property
	def frame_range(self):
		""" Int of expected frames in sequence. """
		return self.end - self.start + 1

	@property
	def missing(self):
		""" Int of total missing frames in sequence. """
		return self.end - (self.start - 1) - self.frames

	@property
	def is_missing_frames(self):
		""" Return True if any frames are missing from sequence. """
		return self.frames != self.frame_range

	@property
	def size(self):
		""" Sum of all filesizes (in bytes) in sequence. """
		try:
			return sum([file_.size for file_ in self])
		except TypeError:
			return

	def get_frame(self, frame):
		"""
		Get a specific frame number's File object, works like
		__getitem__ except gets exact frame number instead of index
		position in list.
		
		:param int frame: Frame number to extract from sequence.
		:return: File instance.
		"""
		return self._frames[int(frame)]

	def get_frames(self, start=None, end=None, step=1):
		"""
		Get a specific range of frames' File objects, works like
		__getitem__ slice, but gets exact frames or frame ranges
		instead of index positions in list.
		
		:param int start: Frame number to start range.
		:param int end: Frame number to end range.
		:param int step: Steps, like range function uses.
		:return: A list of File objects from the given ranges.
		"""
		frame_list = []
		if start is None:
			return self[:]
		elif end is not None:
			for frame in range(start, end + 1, step):
				if frame in self._frames:
					frame_list.append(self._frames[frame])
				else:
					logger.warning('Cannot get frame %d not in sequence %s.' %
								   (frame, str(self)))
		return frame_list

	def get_missing_frames(self):
		""" Get list of frame numbers missing in sequence. """
		implied = range(self.start, self.end + 1)
		return [frame for frame in implied if frame not in self._frames]

	def append(self, frame_file):
		"""
		Add a new frame to the sequence if it is has a matching
		sequence key. If it is the first file being added to a new
		Sequence object, it will set all the Sequence attributes.

		:param frame_file: File instance or string to append to Sequence.
		"""
		if not isinstance(frame_file, File):
			if isinstance(frame_file, str):
				frame_file = File(frame_file)
				if len(self._frames) > 0 and frame_file.get_seq_key(
						cfg.ignore_padding) != self.seq_name:
					raise ValueError('%s is not a member of %s. Not appending.'
					                 % (frame_file, repr(self)))
		if frame_file.frame is None:
			raise ValueError('%s can not be sequenced.' % str(frame_file))
		if not self.frames:
			self.namehead = frame_file.namehead
			self.path = frame_file.path
			self.head = frame_file.head
			self.tail = frame_file.tail
			self.ext = frame_file.ext
			self.padding = frame_file.padding
			self.seq_name = frame_file.get_seq_key(cfg.ignore_padding)
		elif frame_file.frame in self._frames:
			raise IndexError(
				'%s already in sequence as %s' % (
					frame_file.name, self._frames[frame_file.frame]))
		elif self.padding < frame_file.padding:
			self.inconsistent_padding = True
			self.padding = frame_file.padding
		self._frames[frame_file.frame] = frame_file

	def format(self, str_format=cfg.format):
		"""
		This formatter will replace any of the formatting directives
		found in the format argument with it's string part. It will try
		to format any character after a % sign, so in order to use a
		literal %, it must be escaped with another % - '%%'.

		+-------------------------------------------------------------------+
		| SAMPLE NAME:   '/path/to/file_name.0101.final.ext'                |
		+-------------------------------------------------------------------+

		+------+---------------------------------+--------------------------+
		| FMT  |  DESCRIPTION                    | EXAMPLE                  |
		+------+---------------------------------+--------------------------+
		| '%%' |  literal '%' sign               |  '%'                     |
		+------+---------------------------------+--------------------------+
		| '%p' |  pathname                       |  '/path/to'              |
		+------+---------------------------------+--------------------------+
		| '%h' |  head chars of filename         |  'file_name.'            |
		+------+---------------------------------+--------------------------+
		| '%H' |  all chars preceeding frame #   |  '/path/to/file_name.'   |
		+------+---------------------------------+--------------------------+
		| '%f' |  number of actual frames        |  '42'                    |
		+------+---------------------------------+--------------------------+
		| '%r' |  implied frame range            |  '[0101-0150]'           |
		+------+---------------------------------+--------------------------+
		| '%R' |  broken explicit frame range    |  '[101-140, 148, 150]'   |
		|      |  ignores padding                |                          |
		+------+---------------------------------+--------------------------+
		| '%m' |  total number of missing frames |  '8'                     |
		+------+---------------------------------+--------------------------+
		| '%M' |  broken explicit missing ranges |  '[141-147, 149]'        |
		|      |  ignores padding                |                          |
		+------+---------------------------------+--------------------------+
		| '%D' |  '#' digits denoting padding    |  '####'                  |
		+------+---------------------------------+--------------------------+
		| '%P' |  '%' style padding              |  '%04d'                  |
		+------+---------------------------------+--------------------------+
		| '%t' |  tail chars after frame, no ext |  '.final'                |
		+------+---------------------------------+--------------------------+
		| '%T' |  all tail chars after frame     |  '.final.ext'            |
		+------+---------------------------------+--------------------------+
		| '%e' |  extension without dot          |  'ext'                   |
		+------+---------------------------------+--------------------------+

		:param str_format: The string directive for the formatter to convert.
		:return: The formatted sequence string.
		"""

		# Call functions to minimize processes run during formatter execution.
		directive_mapper = {
			'%%': self.__pct,
			'%p': self.__path,
			'%h': self.__namehead,
			'%H': self.__head,
			'%f': self.__num_frames,
			'%r': self.__implied_range,
			'%R': self.__explicit_range,
			'%m': self.__num_missing_frames,
			'%M': self.__explicit_missing_range,
			'%D': self.__digits_pound_signs,
			'%P': self.__digits_padding,
			'%t': self.__tail_without_ext,
			'%T': self.__tail,
			'%e': self.__ext,
			}
		str_format = [c for c in str_format]
		new_string = ''

		matched = False
		for char in str_format:
			if matched:
				new_string += directive_mapper['%' + char]()
				matched = False
				continue
			if char == '%':
				matched = True
				continue
			else:
				new_string += char
		return new_string

	@staticmethod
	def __pct():
		""" Internal formatter method """
		return '%'

	def __path(self):
		""" Internal formatter method """
		return self.path

	def __namehead(self):
		""" Internal formatter method """
		return self.namehead

	def __head(self):
		""" Internal formatter method """
		return self.head

	def __num_frames(self):
		""" Internal formatter method """
		return str(self.frames)

	def __implied_range(self):
		""" Internal formatter method """
		return '[' + str(self.get_frame(self.start).frame_as_str) + \
			   '-' + str(self.get_frame(self.end).frame_as_str) + ']'

	def __explicit_range(self):
		""" Internal formatter method """
		return frame_ranges_to_string(sorted(self._frames))

	def __num_missing_frames(self):
		""" Internal formatter method """
		return str(self.missing)

	def __explicit_missing_range(self):
		""" Internal formatter method """
		return frame_ranges_to_string(self.get_missing_frames())

	def __digits_pound_signs(self):
		""" Internal formatter method """
		return '#' * self.padding

	def __digits_padding(self):
		""" Internal formatter method """
		return '%%0%dd' % self.padding

	def __tail_without_ext(self):
		""" Internal formatter method """
		return '.'.join(self.tail.split('.')[:-1])

	def __tail(self):
		""" Internal formatter method """
		return self.tail

	def __ext(self):
		""" Internal formatter method """
		return self.ext
