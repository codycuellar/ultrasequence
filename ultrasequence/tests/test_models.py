import os
import unittest
from unittest import TestCase
from ultrasequence import models
from ultrasequence.config import cfg


TEST_SEQUENCES = os.path.join(os.path.dirname(__file__), 'data',
							  'test_sequencer_regular.txt')


class TestExtractFrame(TestCase):
	def setUp(self):
		cfg.reset_defaults()

	def test_frame_name(self):
		result = models.extract_frame('/path/to/file.1000.more.ext')
		self.assertTupleEqual(result, ('/path/to/file.', '1000', '.more.ext'))

	def test_number_only_name(self):
		result = models.extract_frame('1000.more.ext')
		self.assertTupleEqual(result, ('', '1000', '.more.ext'))

	def test_no_number_name(self):
		result = models.extract_frame('/path/to/file.more.ext')
		self.assertTupleEqual(result, ('/path/to/file.more.ext', '', ''))

	def test_number_only(self):
		result = models.extract_frame('1000')
		self.assertTupleEqual(result, ('', '1000', ''))

	def test_no_extension(self):
		result = models.extract_frame('/path/to/file.1000')
		self.assertTupleEqual(result, ('/path/to/file.', '1000', ''))


class TestSplitExtension(TestCase):
	def setUp(self):
		cfg.reset_defaults()

	def test_split_single_dot(self):
		split = models.split_extension('test.ext')
		self.assertTupleEqual(split, ('test', 'ext'))

	def test_split_multiple_dots(self):
		split = models.split_extension('test.some.123.ext1')
		self.assertTupleEqual(split, ('test.some.123', 'ext1'))

	def test_split_no_dots(self):
		split = models.split_extension('testext1')
		self.assertTupleEqual(split, ('testext1', ''))


class TestFrameRangesToString(TestCase):
	def setUp(self):
		cfg.reset_defaults()

	def test_conver_list(self):
		frames = [100, 101, 102, 104, 107, 108, 1010]
		result = models.frame_ranges_to_string(frames)
		self.assertEqual(result, '[100-102, 104, 107-108, 1010]')

	def test_convert_tuple(self):
		frames = (100, 101, 102, 104, 107, 108, 1010)
		result = models.frame_ranges_to_string(frames)
		self.assertEqual(result, '[100-102, 104, 107-108, 1010]')

	def test_convert_empty_list(self):
		result = models.frame_ranges_to_string([])
		self.assertEqual(result, '[]')

	def test_convert_single_item(self):
		result = models.frame_ranges_to_string([5])
		self.assertEqual(result, '[5]')


class TestFile(TestCase):
	def setUp(self):
		cfg.reset_defaults()

	def test_normal_file_init(self):
		_file = models.File('/path/to/file.01000.more.ext')
		self.assertEqual(_file.abspath, '/path/to/file.01000.more.ext')
		self.assertEqual(_file.path, '/path/to')
		self.assertEqual(_file.name, 'file.01000.more.ext')
		self.assertEqual(_file.ext, 'ext')
		self.assertEqual(_file.namehead, 'file.')
		self.assertEqual(_file.head, '/path/to/file.')
		self.assertEqual(_file.frame_as_str, '01000')
		self.assertEqual(_file.frame, 1000)
		self.assertEqual(_file.tail, '.more.ext')
		self.assertEqual(_file.padding, 5)

	def test_no_number_file_init(self):
		_file = models.File('/path/to/file.ext')
		self.assertEqual(_file.abspath, '/path/to/file.ext')
		self.assertEqual(_file.path, '/path/to')
		self.assertEqual(_file.name, 'file.ext')
		self.assertEqual(_file.ext, 'ext')
		self.assertEqual(_file.namehead, 'file')
		self.assertEqual(_file.head, '/path/to/file')
		self.assertEqual(_file.frame_as_str, '')
		self.assertEqual(_file.frame, None)
		self.assertEqual(_file.tail, '.ext')
		self.assertEqual(_file.padding, 0)

	def test_number_only_file_init(self):
		_file = models.File('/path/to/01234.ext')
		self.assertEqual(_file.abspath, '/path/to/01234.ext')
		self.assertEqual(_file.path, '/path/to')
		self.assertEqual(_file.name, '01234.ext')
		self.assertEqual(_file.ext, 'ext')
		self.assertEqual(_file.head, '/path/to/')
		self.assertEqual(_file._framenum, '01234')
		self.assertEqual(_file.frame, 1234)
		self.assertEqual(_file.tail, '.ext')
		self.assertEqual(_file.padding, 5)

	def test_number_only_no_path_file_init(self):
		_file = models.File('1234.ext')
		self.assertEqual(_file.abspath, '1234.ext')
		self.assertEqual(_file.path, '')
		self.assertEqual(_file.name, '1234.ext')
		self.assertEqual(_file.ext, 'ext')
		self.assertEqual(_file.head, '')
		self.assertEqual(_file.frame_as_str, '1234')
		self.assertEqual(_file.frame, 1234)
		self.assertEqual(_file.tail, '.ext')
		self.assertEqual(_file.padding, 4)

	def test_file_stat_dict(self):
		stats = {
			'size': 1,
			'inode': 2,
			'nlink': 3,
			'dev': 4,
			'mode': 5,
			'uid': 6,
			'gid': 7,
			'mtime': 8,
			'ctime': 9,
			'atime': 10
		}
		_file = models.File('filename.ext', stats=stats)
		self.assertEqual(_file.size, 1)
		self.assertEqual(_file.inode, 2)
		self.assertEqual(_file.nlink, 3)
		self.assertEqual(_file.dev, 4)
		self.assertEqual(_file.mode, 5)
		self.assertEqual(_file.uid, 6)
		self.assertEqual(_file.gid, 7)
		self.assertEqual(_file.mtime, 8)
		self.assertEqual(_file.ctime, 9)
		self.assertEqual(_file.atime, 10)

	def test_file_stat_list(self):
		stats = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		_file = models.File('filename.ext', stats=stats)
		self.assertIsInstance(_file.stat, models.Stat)
		self.assertEqual(_file.size, 1)
		self.assertEqual(_file.inode, 2)
		self.assertEqual(_file.ctime, 3)
		self.assertEqual(_file.mtime, 4)
		self.assertEqual(_file.atime, 5)
		self.assertEqual(_file.mode, 6)
		self.assertEqual(_file.dev, 7)
		self.assertEqual(_file.nlink, 8)
		self.assertEqual(_file.uid, 9)
		self.assertEqual(_file.gid, 10)

	def test_file_os_stat(self):
		_file = models.File(__file__, os.stat(__file__))
		self.assertIsInstance(_file.stat, os.stat_result)

	def test_file_get_stat(self):
		_file = models.File(__file__, get_stats=True)
		self.assertIsInstance(_file.stat, os.stat_result)

	def test_file_get_stats_unsuccessful_fallback(self):
		stats = {'size': 15}
		_file = models.File('/not/a/file/path.none', stats=stats,
						   get_stats=True)
		self.assertIsInstance(_file.stat, models.Stat)
		self.assertEqual(_file.size, 15)
		self.assertIsNone(_file.inode)

	def test_get_seq_key_no_padding(self):
		_file = models.File('/path/to/file.1000.ext')
		self.assertEqual(_file.get_seq_key(True), '/path/to/file.#.ext')

	def test_get_seq_key_padding(self):
		_file = models.File('/path/to/file.1000.ext')
		self.assertEqual(_file.get_seq_key(ignore_padding=False),
						 '/path/to/file.%04d.ext')

	def test_get_seq_key_no_framenum(self):
		_file = models.File('/path/to/file.ext')
		self.assertEqual(_file.get_seq_key(True), '/path/to/file.ext')
		self.assertEqual(_file.get_seq_key(ignore_padding=False),
						 '/path/to/file.ext')


class TestSequence(TestCase):
	def setUp(self):
		cfg.reset_defaults()
		missing_files = [
			'/abs/path/to/file_0100_name.ext',
			'/abs/path/to/file_0101_name.ext',
			'/abs/path/to/file_0102_name.ext',
			'/abs/path/to/file_0104_name.ext',
			'/abs/path/to/file_0107_name.ext',
			'/abs/path/to/file_0108_name.ext',
			'/abs/path/to/file_01010_name.ext',
		]
		self.missing = models.Sequence()
		for m in missing_files:
			self.missing.append(m)
		contiguous_files = [
			'/abs/path/to/file_0100_name.ext',
			'/abs/path/to/file_0101_name.ext',
			'/abs/path/to/file_0102_name.ext',
			'/abs/path/to/file_0103_name.ext',
		]
		self.contiguous = models.Sequence()
		for m in contiguous_files:
			self.contiguous.append(m)

	def test_sequence_init_append(self):
		seq = models.Sequence('/path/to/file.0100.ext')
		self.assertListEqual(list(seq._frames), [100])
		self.assertEqual(seq.seq_name, '/path/to/file.#.ext')
		self.assertEqual(seq.namehead, 'file.')
		self.assertEqual(seq.head, '/path/to/file.')
		self.assertEqual(seq.path, '/path/to')
		self.assertEqual(seq.tail, '.ext')
		self.assertEqual(seq.ext, 'ext')
		self.assertEqual(seq.padding, 4)
		self.assertEqual(seq.inconsistent_padding, False)

	def test_sequence_append_file(self):
		file1 = models.File('/path/to/file.0100.ext')
		seq = models.Sequence(file1)
		seq.append(models.File('/path/to/file.0101.ext'))
		self.assertEqual(seq.frames, 2)

	def test_sequence_append_string(self):
		_file = '/path/to/file.0100.ext'
		seq = models.Sequence(_file)
		seq.append('/path/to/file.0101.ext')
		self.assertEqual(seq.frames, 2)

	def test_sequence_append_exact_dupe(self):
		_file = models.File('/path/to/file.0100.ext')
		seq = models.Sequence(_file)
		with self.assertRaises(IndexError):
			seq.append('/path/to/file.0100.ext')

	def test_sequence_append_non_member(self):
		_file = models.File('/path/to/file.0100.ext')
		seq = models.Sequence(_file)
		with self.assertRaises(ValueError):
			seq.append('/not/a/member.0001.ext')

	def test_sequence_inconsistent_padding_dupe(self):
		_file = models.File('/path/to/file.0100.ext')
		seq = models.Sequence(_file)
		self.assertEqual(seq.seq_name, '/path/to/file.#.ext')
		with self.assertRaises(IndexError):
			seq.append('/path/to/file.00100.ext')

	def test_sequence_force_consistent_padding(self):
		_file = models.File('/path/to/file.0100.ext')
		seq = models.Sequence(_file, ignore_padding=False)
		self.assertEqual(seq.seq_name, '/path/to/file.%04d.ext')
		with self.assertRaises(ValueError):
			seq.append('/path/to/file.00100.ext')

	# def test_contiguous_sequence_frame_range(self):
	# 	seq = sq.Sequence(self.contiguous[0])
	# 	[seq.append(x) for x in self.contiguous[1:]]
	# 	self.assertEqual(seq.start, 100)
	# 	self.assertEqual(seq.end, 103)
	# 	self.assertEqual(seq.frames, 4)
	# 	self.assertEqual(seq.implied_frames, 4)
	# 	self.assertEqual(seq.missing_frames, 2)
	# 	self.assertListEqual(seq.get_missing_frames(), [102, 104])

	def test_sequence_size(self):
		files = [
			('file.0.ext', {'size': 10}),
			('file.1.ext', {'size': 10}),
			('file.2.ext', {'size': 10}),
		]
		sequence = models.Sequence()
		for _file in files:
			_file = models.File(*_file)
			sequence.append(_file)
		self.assertEqual(sequence.size, 30)

	def test_get_missing_frames(self):
		files = [
			'/abs/path/to/file_0100_name.ext',
			'/abs/path/to/file_0101_name.ext',
			'/abs/path/to/file_0103_name.ext',
			'/abs/path/to/file_0105_name.ext',
			'/abs/path/to/file_0106_name.ext',
			'/abs/path/to/file_0107_name.ext',
		]
		seq = models.Sequence()
		for _file in files:
			seq.append(_file)
		self.assertListEqual(seq.get_missing_frames(), [102, 104])


class TestSequenceFormatting(TestCase):
	def setUp(self):
		cfg.reset_defaults()
		files = [
			'/abs/path/to/file_0100_name.ext',
			'/abs/path/to/file_0101_name.ext',
			'/abs/path/to/file_0102_name.ext',
			'/abs/path/to/file_0104_name.ext',
			'/abs/path/to/file_0107_name.ext',
			'/abs/path/to/file_0108_name.ext',
			'/abs/path/to/file_0110_name.ext',
		]
		self.seq = models.Sequence()
		for f in files:
			self.seq.append(f)

	def test_format_path(self):
		self.assertEqual(self.seq.format('%p'), '/abs/path/to')
		self.assertEqual(self.seq.format('test%ptest%p'),
						 'test/abs/path/totest/abs/path/to')

	def test_format_namehead(self):
		self.assertEqual(self.seq.format('%h'), 'file_')
		self.assertEqual(self.seq.format('test%htest%h'),
						 'testfile_testfile_')

	def test_format_head(self):
		self.assertEqual(self.seq.format('%H'), '/abs/path/to/file_')
		self.assertEqual(self.seq.format('test%Htest%H'),
						 'test/abs/path/to/file_test/abs/path/to/file_')

	def test_format_numframes(self):
		self.assertEqual(self.seq.format('%f'), '7')
		self.assertEqual(self.seq.format('test%ftest(%f)'),
						 'test7test(7)')

	def test_format_implied_range(self):
		self.assertEqual(self.seq.format('%r'), '[0100-0110]')
		self.assertEqual(self.seq.format('test%rtest%r'),
						 'test[0100-0110]test[0100-0110]')

	def test_format_explicit_range(self):
		self.assertEqual(self.seq.format('%R'),
						 '[100-102, 104, 107-108, 110]')
		self.assertEqual(
			self.seq.format('test%Rtest%R'),
			'test[100-102, 104, 107-108, 110]test[100-102, 104, 107-108, 110]')

	def test_format_num_missing_frames(self):
		self.assertEqual(self.seq.format('%m'), '4')
		self.assertEqual(self.seq.format('test%mtest%m'),
						 'test4test4')

	def test_format_explicit_missing_frames(self):
		self.assertEqual(self.seq.format('%M'), '[103, 105-106, 109]')
		self.assertEqual(self.seq.format('test%Mtest%M'),
						 'test[103, 105-106, 109]test[103, 105-106, 109]')

	def test_format_pound_padding(self):
		self.assertEqual(self.seq.format('%D'), '####')
		self.assertEqual(self.seq.format('test%Dtest%D'),
						 'test####test####')

	def test_format_formatted_padding(self):
		self.assertEqual(self.seq.format('%P'), '%04d')
		self.assertEqual(self.seq.format('test%Ptest%P'),
						 'test%04dtest%04d')

	def test_format_tail_without_ext(self):
		self.assertEqual(self.seq.format('%t'), '_name')
		self.assertEqual(self.seq.format('test%ttest%t'),
						 'test_nametest_name')

	def test_format_tail(self):
		self.assertEqual(self.seq.format('%T'), '_name.ext')
		self.assertEqual(self.seq.format('test%Ttest%T'),
						 'test_name.exttest_name.ext')

	def test_format_ext(self):
		self.assertEqual(self.seq.format('%e'), 'ext')
		self.assertEqual(self.seq.format('test%etest%e'),
						 'testexttestext')

	def test_format_pct(self):
		self.assertEqual(self.seq.format('%%'), '%')
		self.assertEqual(self.seq.format('100%% Success'),
						 '100% Success')

	def test_format_invalid_directive(self):
		with self.assertRaises(KeyError):
			self.seq.format('Try%^Fail')


# class TestMakeSequences(TestCase):
#
# 	def setUp(self):
# 		with open(TEST_SEQUENCES) as testA:
# 			self.regular_sequence = [x.rstrip() for x in testA.readlines()]
#
# 	def test_make_sequence_returns_three_lists(self):
# 		results = sq.make_sequences(self.regular_sequence)
# 		self.assertEqual(len(results), 4)
# 		for l in results:
# 			self.assertIsInstance(l, list)
#
# 	def test_make_sequences_takes_file_instances(self):
# 		file1 = sq.File('/path/to/file.100.ext')
# 		file2 = sq.File('/path/to/file.101.ext')
# 		file3 = sq.File('/path/to/file.102.ext')
# 		results = sq.make_sequences([file1, file2, file3])
# 		self.assertEqual(results[0][0].seq_name, '/path/to/file.#.ext')
#
# 	def test_make_sequence_include_exts_works(self):
# 		ignore_files = [
# 			'file.10001.mov',
# 			'file.10002.mov'
# 		]
# 		excluded = sq.make_sequences(self.regular_sequence + ignore_files,
# 									include_exts=['ext', 'dpx'])[2]
# 		excluded_files = [x.abspath for x in excluded]
# 		self.assertListEqual(ignore_files, excluded_files)
#
# 	def test_make_sequence_returns_proper_instances(self):
# 		ignore_files = [
# 			'file.10001.mov',
# 			'file.10002.mov'
# 		]
# 		results = sq.make_sequences(self.regular_sequence + ignore_files,
# 									include_exts=['ext'])
# 		sequences, non_sequences, excluded, collisions = results
# 		for seq in sequences:
# 			self.assertIsInstance(seq, sq.Sequence)
# 		for nseq in non_sequences + excluded:
# 			self.assertIsInstance(nseq, sq.File)
#
# 	def test_make_sequence_ignore_padding(self):
# 		sequences = sq.make_sequences(self.regular_sequence)[0]
# 		sequence_test = [
# 			'basic_dot.#.ext',
# 			'basic_underscore_#.ext',
# 			'trailing.#.chars.ext',
# 			'#.ext',
# 			'no#sep.ext',
# 			'multiple_nums.#.EXT',
# 			'2017_#.ext',
# 			'ab_010_0010_comp_v023.#.dpx',
# 			'/abs/path/2/basic_dot.#.ext',
# 			'/abs/path/2/basic_underscore_#.ext',
# 			'/abs/path/2/trailing.#.chars.ext',
# 			'/abs/path/2/#.ext',
# 			'/abs/path/2/no#sep.ext',
# 			'/abs/path/2/multiple_nums.#.ext',
# 			'/abs/path/2/2017_#.ext',
# 			'/abs/path/2/ab_010_0010_comp_v023.#.dpx',
# 		]
# 		sequence_test.sort()
# 		sequence_results = [x.seq_name for x in sequences]
# 		sequence_results.sort()
# 		self.assertListEqual(sequence_test, sequence_results)
#
# 	def test_make_sequence_force_consistent_padding(self):
# 		sequences = sq.make_sequences(self.regular_sequence,
# 									  ignore_padding=False)[0]
# 		sequence_test = [
# 			'basic_dot.%01d.ext',
# 			'basic_dot.%02d.ext',
# 			'basic_underscore_%01d.ext',
# 			'trailing.%04d.chars.ext',
# 			'%04d.ext',
# 			'no%02dsep.ext',
# 			'multiple_nums.%03d.EXT',
# 			'2017_%03d.ext',
# 			'ab_010_0010_comp_v023.%04d.dpx',
# 			'/abs/path/2/basic_dot.%01d.ext',
# 			'/abs/path/2/basic_underscore_%01d.ext',
# 			'/abs/path/2/trailing.%04d.chars.ext',
# 			'/abs/path/2/%04d.ext',
# 			'/abs/path/2/no%02dsep.ext',
# 			'/abs/path/2/multiple_nums.%03d.ext',
# 			'/abs/path/2/2017_%03d.ext',
# 			'/abs/path/2/ab_010_0010_comp_v023.%04d.dpx',
# 		]
# 		sequence_test.sort()
# 		sequence_results = [x.seq_name for x in sequences]
# 		sequence_results.sort()
# 		self.assertListEqual(sequence_test, sequence_results)
#
# 	def test_make_sequences_non_sequences(self):
# 		non_sequences = sq.make_sequences(self.regular_sequence)[1]
# 		sequence_test = [
# 			'no_digits.ext',
# 			'no_sequence_2017.ext',
# 			'/abs/path/2/no_digits.ext',
# 			'/abs/path/2/no_sequence_2017.ext',
# 		]
# 		sequence_test.sort()
# 		sequence_results = [x.abspath for x in non_sequences]
# 		sequence_results.sort()
# 		self.assertListEqual(sequence_test, sequence_results)
#
# 	def test_make_sequence_handles_index_collision(self):
# 		files = [
# 			'/abs/path/to/file.101.ext',
# 			'/abs/path/to/file.102.ext',
# 			'/abs/path/to/file.103.ext',
# 			'/abs/path/to/file.0101.ext',
# 		]
# 		collisions = sq.make_sequences(files)[3]
# 		collision_names = [x.abspath for x in collisions]
# 		self.assertListEqual(['/abs/path/to/file.0101.ext'], collision_names)
#
# 	def test_make_sequence_stats_as_dict(self):
# 		files = [
# 			('file.0.ext', {'size': 10}),
# 			('file.1.ext', {'size': 10}),
# 			('file.2.ext', {'size': 10}),
# 		]
# 		sequences = sq.make_sequences(files)[0]
# 		for frame in sequences[0]:
# 			self.assertEqual(frame.size, 10)
#
# 	def test_make_sequence_stats_as_list(self):
# 		files = [
# 			('file.0.ext', [10, 20]),
# 			('file.1.ext', [10, 20]),
# 			('file.2.ext', [10, 20]),
# 		]
# 		sequences = sq.make_sequences(files)[0]
# 		for frame in sequences[0]:
# 			self.assertEqual(frame.size, 10)
# 			self.assertEqual(frame.inode, 20)


if __name__ == '__main__':
	unittest.main()
