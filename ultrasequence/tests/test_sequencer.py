import os
import unittest
from unittest import TestCase
from ultrasequence import sequencer as sq


TEST_SEQUENCES = os.path.join(os.path.dirname(__file__), 'data',
							  'test_sequencer_regular.txt')


class TestExtractFrame(TestCase):

	def test_frame_name(self):
		result = sq.extract_frame('/path/to/file.1000.more.ext')
		self.assertTupleEqual(result, ('/path/to/file.', '1000', '.more.ext'))

	def test_number_only_name(self):
		result = sq.extract_frame('1000.more.ext')
		self.assertTupleEqual(result, ('', '1000', '.more.ext'))

	def test_no_number_name(self):
		result = sq.extract_frame('/path/to/file.more.ext')
		self.assertTupleEqual(result, ('/path/to/file.more.ext', '', ''))

	def test_number_only(self):
		result = sq.extract_frame('1000')
		self.assertTupleEqual(result, ('', '1000', ''))

	def test_no_extension(self):
		result = sq.extract_frame('/path/to/file.1000')
		self.assertTupleEqual(result, ('/path/to/file.', '1000', ''))


class TestSplitExtension(TestCase):

	def test_split_single_dot(self):
		split = sq.split_extension('test.ext')
		self.assertTupleEqual(split, ('test', 'ext'))

	def test_split_multiple_dots(self):
		split = sq.split_extension('test.some.123.ext1')
		self.assertTupleEqual(split, ('test.some.123', 'ext1'))

	def test_split_no_dots(self):
		split = sq.split_extension('testext1')
		self.assertTupleEqual(split, ('testext1', ''))


class TestFile(TestCase):

	def test_normal_file_init(self):
		file = sq.File('/path/to/file.1000.more.ext')
		self.assertEqual(file.abspath, '/path/to/file.1000.more.ext')
		self.assertEqual(file.path, '/path/to')
		self.assertEqual(file.name, 'file.1000.more.ext')
		self.assertEqual(file.ext, 'ext')
		self.assertEqual(file.head, '/path/to/file.')
		self.assertEqual(file._framenum, '1000')
		self.assertEqual(file.frame, 1000)
		self.assertEqual(file.tail, '.more.ext')
		self.assertEqual(file.padding, 4)

	def test_no_number_file_init(self):
		file = sq.File('/path/to/file.ext')
		self.assertEqual(file.abspath, '/path/to/file.ext')
		self.assertEqual(file.path, '/path/to')
		self.assertEqual(file.name, 'file.ext')
		self.assertEqual(file.ext, 'ext')
		self.assertEqual(file.head, '/path/to/file')
		self.assertEqual(file._framenum, '')
		self.assertEqual(file.frame, None)
		self.assertEqual(file.tail, '.ext')
		self.assertEqual(file.padding, 0)

	def test_number_only_file_init(self):
		file = sq.File('/path/to/1234.ext')
		self.assertEqual(file.abspath, '/path/to/1234.ext')
		self.assertEqual(file.path, '/path/to')
		self.assertEqual(file.name, '1234.ext')
		self.assertEqual(file.ext, 'ext')
		self.assertEqual(file.head, '/path/to/')
		self.assertEqual(file._framenum, '1234')
		self.assertEqual(file.frame, 1234)
		self.assertEqual(file.tail, '.ext')
		self.assertEqual(file.padding, 4)

	def test_number_only_no_path_file_init(self):
		file = sq.File('1234.ext')
		self.assertEqual(file.abspath, '1234.ext')
		self.assertEqual(file.path, '')
		self.assertEqual(file.name, '1234.ext')
		self.assertEqual(file.ext, 'ext')
		self.assertEqual(file.head, '')
		self.assertEqual(file._framenum, '1234')
		self.assertEqual(file.frame, 1234)
		self.assertEqual(file.tail, '.ext')
		self.assertEqual(file.padding, 4)

	def test_get_seq_key_no_padding(self):
		file = sq.File('/path/to/file.1000.ext')
		self.assertEqual(file.get_seq_key(), '/path/to/file.#.ext')

	def test_get_seq_key_padding(self):
		file = sq.File('/path/to/file.1000.ext')
		self.assertEqual(file.get_seq_key(True), '/path/to/file.%04d.ext')

	def test_get_seq_key_no_framenum(self):
		file = sq.File('/path/to/file.ext')
		self.assertEqual(file.get_seq_key(), '/path/to/file.ext')
		self.assertEqual(file.get_seq_key(True), '/path/to/file.ext')

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
		file = sq.File('filename.ext', stats=stats)
		self.assertEqual(file.size, 1)
		self.assertEqual(file.inode, 2)
		self.assertEqual(file.nlink, 3)
		self.assertEqual(file.dev, 4)
		self.assertEqual(file.mode, 5)
		self.assertEqual(file.uid, 6)
		self.assertEqual(file.gid, 7)
		self.assertEqual(file.mtime, 8)
		self.assertEqual(file.ctime, 9)
		self.assertEqual(file.atime, 10)

	def test_file_stat_list(self):
		stats = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		file = sq.File('filename.ext', stats=stats)
		self.assertEqual(file.size, 1)
		self.assertEqual(file.inode, 2)
		self.assertEqual(file.ctime, 3)
		self.assertEqual(file.mtime, 4)
		self.assertEqual(file.atime, 5)
		self.assertEqual(file.mode, 6)
		self.assertEqual(file.dev, 7)
		self.assertEqual(file.nlink, 8)
		self.assertEqual(file.uid, 9)
		self.assertEqual(file.gid, 10)

	def test_file_os_stat(self):
		file = sq.File(__file__, os.stat(__file__))
		self.assertIsInstance(file.stat, os.stat_result)

	def test_file_get_stat(self):
		file = sq.File(__file__, get_stats=True)
		self.assertIsInstance(file.stat, os.stat_result)


class TestSequence(TestCase):

	def test_sequence_init(self):
		seq = sq.Sequence()
		self.assertDictEqual(seq._frames, {})
		self.assertEqual(seq.seq_name, '')
		self.assertEqual(seq.head, '')
		self.assertEqual(seq.tail, '')
		self.assertEqual(seq.ext, '')
		self.assertEqual(seq.padding, 0)
		self.assertEqual(seq.inconsistent_padding, False)

	def test_sequence_append_file(self):
		file = sq.File('/path/to/file.0100.ext')
		seq = sq.Sequence(file)
		self.assertDictEqual(seq._frames, {100: file})
		self.assertEqual(seq.seq_name, '/path/to/file.#.ext')
		self.assertEqual(seq.head, '/path/to/file.')
		self.assertEqual(seq.tail, '.ext')
		self.assertEqual(seq.ext, 'ext')
		self.assertEqual(seq.padding, 4)
		self.assertEqual(seq.inconsistent_padding, False)

	def test_sequence_append_string(self):
		file = '/path/to/file.0100.ext'
		seq = sq.Sequence(file)
		self.assertEqual(len(seq._frames), 1)
		self.assertIsInstance(seq._frames[100], sq.File)
		self.assertEqual(seq.seq_name, '/path/to/file.#.ext')
		self.assertEqual(seq.head, '/path/to/file.')
		self.assertEqual(seq.tail, '.ext')
		self.assertEqual(seq.ext, 'ext')
		self.assertEqual(seq.padding, 4)
		self.assertEqual(seq.inconsistent_padding, False)

	def test_sequence_append_exact_dupe(self):
		file = sq.File('/path/to/file.0100.ext')
		seq = sq.Sequence(file)
		with self.assertRaises(IndexError):
			seq.append('/path/to/file.0100.ext')

	def test_sequence_append_non_member(self):
		file = sq.File('/path/to/file.0100.ext')
		seq = sq.Sequence(file)
		with self.assertRaises(ValueError):
			seq.append('/not/a/member.0001.ext')

	def test_sequence_inconsistent_padding_dupe(self):
		file = sq.File('/path/to/file.0100.ext')
		seq = sq.Sequence(file)
		self.assertEqual(seq.seq_name, '/path/to/file.#.ext')
		with self.assertRaises(IndexError):
			seq.append('/path/to/file.00100.ext')

	def test_sequence_force_consistent_padding(self):
		file = sq.File('/path/to/file.0100.ext')
		seq = sq.Sequence(file, force_consistent_padding=True)
		self.assertEqual(seq.seq_name, '/path/to/file.%04d.ext')
		with self.assertRaises(ValueError):
			seq.append('/path/to/file.00100.ext')

	def test_sequence_frame_range(self):
		files = [
			'/abs/path/to/file.101.ext',
			'/abs/path/to/file.103.ext',
			'/abs/path/to/file.105.ext',
			'/abs/path/to/file.106.ext',
		]
		seq = sq.Sequence(files[0])
		[seq.append(x) for x in files[1:]]
		self.assertEqual(seq.start, 101)
		self.assertEqual(seq.end, 106)
		self.assertEqual(seq.frames, 4)
		self.assertEqual(seq.implied_frames, 6)
		self.assertTrue(seq.is_missing_frames)
		self.assertEqual(seq.missing_frame_count, 2)
		self.assertEqual(seq.get_missing_frames(), {102, 104})


class TestMakeSequences(TestCase):

	def setUp(self):
		with open(TEST_SEQUENCES) as testA:
			self.regular_sequence = [x.rstrip() for x in testA.readlines()]

	def test_make_sequence_returns_three_lists(self):
		results = sq.make_sequences(*self.regular_sequence)
		self.assertEqual(len(results), 3)
		for l in results:
			self.assertIsInstance(l, list)

	def test_make_sequence_include_exts_works(self):
		ignore_files = [
			'file.10001.mov',
			'file.10002.mov'
		]
		excluded = sq.make_sequences(*self.regular_sequence, *ignore_files,
									include_exts=['ext', 'dpx'])[2]
		excluded_files = [x.abspath for x in excluded]
		self.assertListEqual(ignore_files, excluded_files)

	def test_make_sequence_returns_proper_instances(self):
		ignore_files = [
			'file.10001.mov',
			'file.10002.mov'
		]
		results = sq.make_sequences(*self.regular_sequence, *ignore_files,
									include_exts=['ext'])
		sequences, non_sequences, excluded = results
		for seq in sequences:
			self.assertIsInstance(seq, sq.Sequence)
		for nseq in non_sequences + excluded:
			self.assertIsInstance(nseq, sq.File)

	def test_make_sequence_ignore_padding(self):
		sequences = sq.make_sequences(*self.regular_sequence)[0]
		sequence_test = [
			'basic_dot.#.ext',
			'basic_underscore_#.ext',
			'trailing.#.chars.ext',
			'#.ext',
			'no#sep.ext',
			'multiple_nums.#.ext',
			'2017_#.ext',
			'ab_010_0010_comp_v023.#.dpx',
			'/abs/path/2/basic_dot.#.ext',
			'/abs/path/2/basic_underscore_#.ext',
			'/abs/path/2/trailing.#.chars.ext',
			'/abs/path/2/#.ext',
			'/abs/path/2/no#sep.ext',
			'/abs/path/2/multiple_nums.#.ext',
			'/abs/path/2/2017_#.ext',
			'/abs/path/2/ab_010_0010_comp_v023.#.dpx',
		]
		sequence_test.sort()
		sequence_results = [x.seq_name for x in sequences]
		sequence_results.sort()
		self.assertListEqual(sequence_test, sequence_results)

	def test_make_sequence_force_consistent_padding(self):
		sequences = sq.make_sequences(*self.regular_sequence,
									  force_consistent_padding=True)[0]
		sequence_test = [
			'basic_dot.%01d.ext',
			'basic_dot.%02d.ext',
			'basic_underscore_%01d.ext',
			'trailing.%04d.chars.ext',
			'%04d.ext',
			'no%02dsep.ext',
			'multiple_nums.%03d.ext',
			'2017_%03d.ext',
			'ab_010_0010_comp_v023.%04d.dpx',
			'/abs/path/2/basic_dot.%01d.ext',
			'/abs/path/2/basic_underscore_%01d.ext',
			'/abs/path/2/trailing.%04d.chars.ext',
			'/abs/path/2/%04d.ext',
			'/abs/path/2/no%02dsep.ext',
			'/abs/path/2/multiple_nums.%03d.ext',
			'/abs/path/2/2017_%03d.ext',
			'/abs/path/2/ab_010_0010_comp_v023.%04d.dpx',
		]
		sequence_test.sort()
		sequence_results = [x.seq_name for x in sequences]
		sequence_results.sort()
		self.assertListEqual(sequence_test, sequence_results)

	def test_make_sequences_non_sequences(self):
		non_sequences = sq.make_sequences(*self.regular_sequence)[1]
		sequence_test = [
			'no_digits.ext',
			'no_sequence_2017.ext',
			'/abs/path/2/no_digits.ext',
			'/abs/path/2/no_sequence_2017.ext',
		]
		sequence_test.sort()
		sequence_results = [x.abspath for x in non_sequences]
		sequence_results.sort()
		self.assertListEqual(sequence_test, sequence_results)

	def test_make_sequence_handles_index_collision(self):
		files = [
			'/abs/path/to/file.101.ext',
			'/abs/path/to/file.102.ext',
			'/abs/path/to/file.103.ext',
			'/abs/path/to/file.0101.ext',
		]
		collisions = sq.make_sequences(*files)[2]
		collision_names = [x.abspath for x in collisions]
		self.assertListEqual(['/abs/path/to/file.0101.ext'], collision_names)


if __name__ == '__main__':
	unittest.main()
