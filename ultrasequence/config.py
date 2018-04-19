"""
CONFIGURATION
=============
The configuration file setup module for ultrasequence. The cfg variable
contains the initialized Config instance which has either the default
attributes, or values found in an .ultrasequence.conf file if one was
available.

GLOBALS
-------
CONFIG

"""
import logging
try:
	import configparser
	PYTHON_VERSION = 3
except ImportError:
	import ConfigParser as configparser
	PYTHON_VERSION = 2
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig()


class UsConfig(object):
	"""
	This class sets up a default configuration, and then tries to overload
	all the attributes with the values from a user configuration file. All
	available config options are accessible as instance attributes.
	"""
	def __init__(self):
		"""
		Init the default parser, and then overload with values found in a
		local config file.
		"""
		self.default_config = {
			'global': {
				'format': '%H%r%T',
				'recurse': 'false',
				'ignore_padding': 'true',
				'include_exts': '',
				'exclude_exts': '',
				'get_stats': 'false',
			},
			'regex': {
				'frame_extract': r'((.*)(\D))?(\d+)(.*)',
				'head_group': 0,
				'frame_group': 3,
				'tail_group': 4,
			}
		}
		self.user_config_file = os.path.expanduser('~/.ultrasequence.conf')
		self.default_parser = configparser.RawConfigParser()

		if PYTHON_VERSION == 3:
			self.default_parser.read_dict(self.default_config)
		else:
			self.default_parser.add_section('global')
			for key in self.default_config['global'].keys():
				self.default_parser.set(
					'global', key, self.default_config['global'][key])
			self.default_parser.add_section('regex')
			for key in self.default_config['regex'].keys():
				self.default_parser.set(
					'regex', key, self.default_config['regex'][key])

		self._load_config(self.default_parser)
		self._load_user_config()

	def __repr__(self):
		return (
			'Config({recurse={0}, ignore_padding={1}, include_exts={2},'
			'exclude_exts={3}, get_stats={4}, format={5})'.format(
				self.recurse, self.ignore_padding, self.include_exts,
				self.exclude_exts, self.get_stats, self.format))

	def _load_config(self, cfgparser):
		"""
		Assign all config values to Config instance attributes.

		:param cfgparser: the ConfigParser object to load values from
		"""
		self.format = cfgparser.get('global', 'format')
		self.recurse = cfgparser.getboolean('global', 'recurse')
		self.ignore_padding = cfgparser.getboolean('global', 'ignore_padding')
		self.include_exts = cfgparser.get('global', 'include_exts').split()
		self.exclude_exts = cfgparser.get('global', 'exclude_exts').split()
		self.get_stats = cfgparser.getboolean('global', 'get_stats')
		self.frame_extract_re = cfgparser.get('regex', 'frame_extract')
		self.head_group = cfgparser.getint('regex', 'head_group')
		self.frame_group = cfgparser.getint('regex', 'frame_group')
		self.tail_group = cfgparser.getint('regex', 'tail_group')

	def _load_user_config(self):
		""" Check for user config file and overload instance attributes. """
		if os.path.exists(self.user_config_file):
			cfgparser = configparser.RawConfigParser()
			cfgparser.read(self.user_config_file)
			self._load_config(cfgparser)

	def reset_defaults(self):
		self._load_config(self.default_parser)

	def write_user_config(self):
		""" Save a user config file with the default values. """
		with open(self.user_config_file, 'w') as f:
			self.default_parser.write(f)
		print('Made user config file at %s' % CONFIG.user_config_file)


CONFIG = UsConfig()
