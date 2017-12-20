import os
import re


FRAMENUM_RE = re.compile(r'((.*)(\D))?(\d+)(.*)')
DEFAULT_FORMAT = '%H%r%T'


def extract_frame(name):
	"""
	This function extracts the last set of digits in the string name and
	assumes it is the frame number when returning the parts.
	
	It's a good idea to only pass basenames without extenions so it doesn't
	attempt to sequence directory names or digits in the extension.

	:param str name: file basename without dir or extension
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
	base filename and the extension (without the dot).
	"""
	parts = filename.split('.')
	if len(parts) < 2:
		return parts[0], ''
	ext = parts.pop(-1)
	head = '.'.join(parts)
	return head, ext


def frame_ranges_to_string(frame_list):
	"""
	Take a flat list of ordered numbers and make a string representation
	of the ranges.
	
	:param iterable frame_list: sorted list of frame numbers
	:return: string of broken frame ranges (i.e '[10-14, 16, 20-25]')
	"""
	if not frame_list:
		return '[]'
	if not isinstance(frame_list, list):
		frame_list = list(frame_list)
	ranges = [[frame_list.pop(0)]]
	range_i = 0
	for x in frame_list:
		if x - 1 == ranges[range_i][-1]:
			ranges[range_i].append(x)
		else:
			range_i += 1
			ranges.append([x])
	list_of_ranges = []
	for x in ranges:
		if len(x) > 1:
			list_of_ranges.append('-'.join([str(x[0]), str(x[-1])]))
		else:
			list_of_ranges.append(str(x[0]))
	complete_string = '[' + ', '.join(list_of_ranges) + ']'
	return complete_string


class Stat(object):
	"""
	This class mocks object returned by os.stat on Unix platforms. The File
	class passes dicts with **kwargs and iterables with *args. When passing
	an iterable to File class, make sure the stats are int-like items in
	the same order as the params in Stat.__init__.
	
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
		While initializing this object, it can be fed stat values
		directly or can attempt to call them on the fly by setting
		get_stats to True.
		
		When passing data into the stat argument, the object passed
		in can be either an actual os.stat_result object, a dictionary
		mapping that matches the sequencer.Stat parameter names, or an
		iterable of int like items that matches the order of the 
		sequencer.Stat class params in the __init__ method.
		
		:param str filepath: the absolute filepath of the file
		:param stats: dict or iterable to map to sequencer.Stat params
			or os.stat_result object.
		:param bool get_stats: when True, attempt to call os.stat on the file.
			If file does not exists, revert back to applying stats values
			if they were supplied.
		"""
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

	@property
	def frame(self):
		""" Integer frame number """
		try:
			return int(self._framenum)
		except ValueError:
			return None

	@property
	def frame_as_str(self):
		""" String frame number extracted from original filename """
		return self._framenum

	@property
	def size(self):
		""" Stat size of file on disk. None if stat not run or supplied. """
		try:
			return int(self.stat.st_size)
		except TypeError:
			return

	@property
	def inode(self):
		""" Stat inode of file on disk. None if stat not run or supplied. """
		try:
			return int(self.stat.st_ino)
		except TypeError:
			return

	@property
	def nlink(self):
		""" Stat nlink of file on disk. None if stat not run or supplied. """
		try:
			return int(self.stat.st_nlink)
		except TypeError:
			return

	@property
	def dev(self):
		""" Stat dev of file on disk. None if stat not run or supplied. """
		try:
			return int(self.stat.st_dev)
		except TypeError:
			return

	@property
	def mode(self):
		""" Stat mode of file on disk. None if stat not run or supplied. """
		try:
			return int(self.stat.st_mode)
		except TypeError:
			return

	@property
	def uid(self):
		""" Stat uid of file on disk. None if stat not run or supplied. """
		try:
			return int(self.stat.st_uid)
		except TypeError:
			return

	@property
	def gid(self):
		""" Stat gid of file on disk. None if stat not run or supplied. """
		try:
			return int(self.stat.st_gid)
		except TypeError:
			return

	@property
	def ctime(self):
		""" Stat ctime of file on disk. None if stat not run or supplied. """
		try:
			return float(self.stat.st_ctime)
		except TypeError:
			return

	@property
	def mtime(self):
		""" Stat mtime of file on disk. None if stat not run or supplied. """
		try:
			return float(self.stat.st_mtime)
		except TypeError:
			return

	@property
	def atime(self):
		""" Stat atime of file on disk. None if stat not run or supplied. """
		try:
			return float(self.stat.st_atime)
		except TypeError:
			return

	def get_seq_key(self, ignore_padding=True):
		"""
		Make sequence name identifier
		
		:param bool ignore_padding: enforce padding 
		:return: sequence name with '#' for frame number if padding ignored
			or standerd padding format '%0#d' where '#' is padding amount. 
		"""
		if not self._framenum:
			digits = ''
		elif ignore_padding:
			digits = '#'
		else:
			digits = '%%0%dd' % self.padding
		return self.head + digits + self.tail


class Sequence(object):
	def __init__(self, file=None, ignore_padding=True):
		"""
		Class representing a sequence of matching file names. The frames
		are stored in a dictionary with the frame numbers as keys. Sets
		are used for fast operations in calculating missing frames.
		
		:param file: File object or filename string to base the object
			instantiation off of.
		:param bool ignore_padding: Setting to False will disallow
			new frames from being appended if the frame padding differs.
		"""
		self._frames = {}
		self.seq_name = ''
		self.path = ''
		self.namehead = ''
		self.head = ''
		self.tail = ''
		self.ext = ''
		self.padding = 0
		self.inconsistent_padding = False
		self.ignore_padding = ignore_padding
		if file is not None:
			self.append(file)

	def __str__(self):
		return self.formatter(DEFAULT_FORMAT)

	def __repr__(self):
		return "Sequence('%s', frames=%d)" % (
			self.formatter(DEFAULT_FORMAT), self.frames)

	def __len__(self):
		return len(self._frames)

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
	def start(self):
		""" First frame of sequence """
		return min(self._frames)

	@property
	def end(self):
		""" Last frame of sequence """
		return max(self._frames)

	@property
	def frames(self):
		""" Number of total frames actually in sequence """
		return len(self)

	@property
	def implied_frames(self):
		""" Number of expected frames in sequence """
		return self.end - self.start + 1

	@property
	def missing_frames(self):
		""" Number of missing frames in sequence """
		return self.end - (self.start - 1) - self.frames

	@property
	def is_missing_frames(self):
		""" True if non-contiguous portions of the frame numbers """
		return self.frames != self.implied_frames

	@property
	def size(self):
		""" Sum of all filesizes in sequence if available """
		try:
			return sum([file.size for file in self])
		except TypeError:
			return

	def get_frames(self):
		""" Get a list of all frame numbers actually existing in sequence """
		return sorted(list(self._frames))

	def get_missing_frames(self):
		""" Get list of frame numbers missing between start and end frame """
		implied = set(range(self.start, self.end + 1))
		actual = set(self._frames)
		return list(sorted(implied - actual))

	def append(self, file):
		"""
		Add a new frame to the sequence.
		 
		:param file: File object or string to append to Sequence
		"""
		if not isinstance(file, File):
			if isinstance(file, str):
				file = File(file)
				if len(self._frames) > 0 and file.get_seq_key(
						self.ignore_padding) != self.seq_name:
					raise ValueError('%s is not a member of %s. Not appending.'
									 % (file, repr(self)))
		if file.frame is None:
			raise ValueError('%s can not be sequenced.' % str(file))
		if not self.frames:
			self.namehead = file.namehead
			self.path = file.path
			self.head = file.head
			self.tail = file.tail
			self.ext = file.ext
			self.padding = file.padding
			self.seq_name = file.get_seq_key(self.ignore_padding)
		elif file.frame in self._frames:
			raise IndexError('%s already in sequence as %s' %
						   (file.name, self._frames[file.frame]))
		elif self.padding < file.padding:
			self.inconsistent_padding = True
			self.padding = file.padding
		self._frames[file.frame] = file

	def formatter(self, format=DEFAULT_FORMAT):
		"""
		This formatter will replace any of the formatting directives
		found in the format argument with it's string part.
		
		 --------------------------------------------------------------------
		|  SAMPLE NAME:   '/path/to/file_name.0101.final.ext'
		 --------------------------------------------------------------------
		
		  FMT     DESCRIPTION                      EXAMPLE
		 --------------------------------------------------------------------
		| '%p' |  pathaname                      |  '/path/to/'
		|--------------------------------------------------------------------
		| '%h' |  head chars of filename         |  'file_name.'
		|--------------------------------------------------------------------
		| '%H' |  all chars preceeding frame #   |  '/path/to/file_name.'
		|--------------------------------------------------------------------
		| '%f' |  number of actual frames        |  '42'
		|--------------------------------------------------------------------
		| '%r' |  implied frame range            |  '[0101-0150]'
		|--------------------------------------------------------------------
		| '%R' |  broken explicit frame range    |  '[101-140, 148, 150]'
		|      |  ignores padding                |
		|--------------------------------------------------------------------
		| '%m' |  total number of missing frames |  '8'
		|--------------------------------------------------------------------
		| '%M' |  broken explicit missing ranges |  '[141-147, 149]'
		|      |  ignores padding                |
		|--------------------------------------------------------------------
		| '%d' |  '#' signs denoting padding     |  '####'
		|--------------------------------------------------------------------
		| '%D' |  '%' style padding              |  '%04d'
		|--------------------------------------------------------------------
		| '%t' |  tail chars after frame, no ext |  '.final'
		|--------------------------------------------------------------------
		| '%T' |  all tail chars after frame     |  '.final.ext'
		|--------------------------------------------------------------------
		| '%e' |  extension without dot          |  'ext'
		 --------------------------------------------------------------------

		:param format: the string directive for the formatter to convert
		:return: the formatted string
		"""

		# Call functions to minimize processes run during formatter execution.
		directive_mapper = {
			'%p': self.__path,
			'%h': self.__namehead,
			'%H': self.__head,
			'%f': self.__num_frames,
			'%r': self.__short_range,
			'%R': self.__explicit_range,
			'%m': self.__num_missing_frames,
			'%M': self.__explicit_missing_range,
			'%d': self.__pound_padding,
			'%D': self.__formatted_padding,
			'%t': self.__tail_without_ext,
			'%T': self.__tail,
			'%e': self.__ext,
		}
		for x in directive_mapper:
			if x in format:
				format = format.replace(x, directive_mapper[x]())
		return format

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

	def __short_range(self):
		""" Internal formatter method """
		return '[' + str(self[self.start].frame_as_str) + \
			   '-' + str(self[self.end].frame_as_str) + ']'

	def __explicit_range(self):
		""" Internal formatter method """
		return frame_ranges_to_string(self.get_frames())

	def __num_missing_frames(self):
		""" Internal formatter method """
		return str(self.missing_frames)

	def __explicit_missing_range(self):
		""" Internal formatter method """
		return frame_ranges_to_string(self.get_missing_frames())

	def __pound_padding(self):
		""" Internal formatter method """
		return '#' * self.padding

	def __formatted_padding(self):
		""" Internal formatter method """
		return '%%0%dd' % self.padding

	def __tail_without_ext(self):
		""" Internal formatter method """
		return '.'.join('.'.split(self.tail)[:-1])

	def __tail(self):
		""" Internal formatter method """
		return self.tail

	def __ext(self):
		""" Internal formatter method """
		return self.ext


def make_sequences(filelist, include_exts=None, stats=None, get_stats=False,
				   ignore_padding=True):
	"""
	This function takes a list of filename path strings and attempts
	to build sequence items out of groups of files in the same path
	with the same naming structure.

	:param filelist: list of filenames to process. These can have different
	:param include_exts: an iterable of string extensions to include in the
		sequencing process
	:param force_consistent_padding: force sequences with different padding to
		to be separate sequences.
	:return: *sequences, *non_sequences, *excluded, *collisions
	"""
	if not include_exts:
		include_exts = set()
	else:
		set(include_exts)

	if not stats:
		stats = {}

	sequences = {}
	non_sequences = []
	excluded = []
	collisions = []

	for file in filelist:
		if isinstance(file, str):
			_file = File(file, stats=stats, get_stats=get_stats)
		elif isinstance(file, (tuple, list)) and len(file) == 2:
			_file = File(file[0], stats=file[1], get_stats=get_stats)
		if include_exts and _file.ext not in include_exts:
			excluded.append(_file)
		elif _file.frame is None:
			non_sequences.append(_file)
		else:
			seq_name = _file.get_seq_key(ignore_padding)
			if seq_name not in sequences:
				sequences[seq_name] = Sequence(_file, ignore_padding)
			else:
				try:
					sequences[seq_name].append(_file)
				except IndexError:
					collisions.append(_file)

	sequences = [sequences[seq] for seq in sequences]
	non_sequences += [sequences.pop(i)[seq.start] for i, seq in
					  reversed(list(enumerate(sequences))) if seq.frames == 1]

	return sequences, non_sequences, excluded, collisions
