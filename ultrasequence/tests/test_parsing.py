import unittest
import os
from unittest import TestCase
try:
	from unittest.mock import patch
except ImportError:
	from mock import patch
from ultrasequence import parsing
from ultrasequence.config import CONFIG


def stat_mock(root, files):
	dir_list = [os.path.join(root, file) for file in files]
	return dir_list


class TestScanDir(TestCase):
	def setUp(self):
		CONFIG.reset_defaults()
		self.walk = [
			(
				'/root',
				['seq_one', 'seq_two', 'seq_three'],
			 	['file_a.ext', 'file_b.ext']
			),
			(
				'/root/seq_one',
				[],
				['seq_one.1000.dxp', 'seq_one.1001.dxp', 'seq_one.1002.dxp']
			),
			(
				'/root/seq_two',
				['seq_two.0.dxp', 'seq_two.1.dxp', 'seq_two.3.dxp'],
				[]
			),
			(
				'/root/seq_three',
				[],
				['seq_three.mov']
			)
		]

	@patch('os.listdir')
	def test_scan_dir_default_no_recurse(self, mock_listdir):
		mock_listdir.return_value = self.walk[0][2]
		with patch('ultrasequence.parsing.stat_files') as mock_stat_files:
			mock_stat_files.side_effect = stat_mock
			result = parsing.scan_dir('/root')
			expected = [os.path.join('/root', file)
						for file in self.walk[0][2]]
			self.assertListEqual(result, expected)

	@patch('ultrasequence.parsing.walk')
	def test_scan_dir_recurse(self, mock_walk):
		CONFIG.recurse = True
		mock_walk.return_value = self.walk
		with patch('ultrasequence.parsing.stat_files') as mock_stat_files:
			mock_stat_files.side_effect = stat_mock
			result = parsing.scan_dir('/root')
			expected = []
			for root, dirs, files in self.walk:
				expected += [os.path.join(root, file) for file in files]
			self.assertListEqual(result, expected)

	@patch('os.path.isfile', return_value=True)
	def test_stat_files_default_no_stats(self, mock_isfile):
		result = parsing.stat_files('/root', self.walk[0][2])
		expected = [os.path.join('/root', file) for file in self.walk[0][2]]
		self.assertListEqual(result, expected)

	@patch('os.path.islink', return_value=False)
	def test_stat_files_enable_stats(self, mock_islink):
		CONFIG.get_stats = True
		with patch('os.stat', return_value='stats'):
			result = parsing.stat_files('/root', self.walk[0][2])
		expected = [(os.path.join('/root', file), 'stats')
					for file in self.walk[0][2]]
		self.assertListEqual(result, expected)


if __name__ == '__main__':
	unittest.main()
