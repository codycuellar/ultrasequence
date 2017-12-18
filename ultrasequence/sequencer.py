import os
import re
import logging


logger = logging.getLogger()

FRAMENUM_RE = re.compile(r'((.*)(\D))?(\d+)(.*)')


def extract_frame(name):
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
	parts = filename.split('.')
	if len(parts) < 2:
		return parts[0], ''
	ext = parts.pop(-1)
	head = '.'.join(parts)
	return head, ext


# class Stat(object):
# 	"""
# 	This class mocks object returned by os.stat on Unix platforms.
# 	"""
# 	def __init__(self, size=None, inode=None, ctime=None, mtime=None,
# 				 atime=None, mode=None, dev=None, nlink=None, uid=None,
# 				 gid=None):
# 		self.st_size = size
# 		self.st_ino = inode
# 		self.st_nlink = nlink
# 		self.st_dev = dev
# 		self.st_mode = mode
# 		self.st_uid = uid
# 		self.st_gid = gid
# 		self.st_ctime = ctime
# 		self.st_mtime = mtime
# 		self.st_atime = atime


class File(object):
	# def __init__(self, filepath, stats=None, get_stats=False):
	def __init__(self, filepath):
		"""
		
		:param filepath: 
		:param ext: 
		:param stats: 
		"""
		self.abspath = filepath
		self.path, self.name = os.path.split(filepath)
		self._base, self.ext = split_extension(self.name)

		parts = extract_frame(self._base)
		head, self._framenum, tail = parts
		self.head = os.path.join(self.path, head)
		self.tail = '.'.join([tail, self.ext])
		self.padding = len(self._framenum)

		# if stats:
		# 	self.stat = Stat(*stats)
		# elif get_stats:
		# 	try:
		# 		self.stat = os.stat(filepath)
		# 		logger.info('File %s not found.' % filepath)
		# 	except FileNotFoundError:
		# 		self.stat = Stat()
		# else:
		# 	self.stat = Stat()

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
		
		:param file: 
		:param force_consistent_padding: 
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

	def get_missing_frames(self):
		expected = set(range(self.start, self.end + 1))
		actual = set(self._frames)
		return expected - actual

	def append(self, file):
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


def make_sequences(*filenames, include_exts=None, #stats=None, get_stats=False,
				   force_consistent_padding=False):
	"""
	
	:param filenames: 
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

	for filename in filenames:
		_file = File(filename)
		if include_exts and _file.ext not in include_exts:
			excluded.append(_file)
		elif _file.frame is None:
			non_sequences.append(_file)
		else:
			seq_name = _file.get_seq_key(force_consistent_padding)
			if seq_name not in sequences:
				sequences[seq_name] = Sequence(_file, force_consistent_padding)
			else:
				sequences[seq_name].append(_file)

	sequences = [sequences[seq] for seq in sequences]
	non_sequences += [sequences.pop(i)[seq.start] for i, seq in
					  reversed(list(enumerate(sequences))) if seq.frames == 1]

	return sequences, non_sequences, excluded
