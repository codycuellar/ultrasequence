try:
	import configparser
	PYTHON_VERSION = 3
except ImportError:
	import ConfigParser as configparser
	PYTHON_VERSION = 2
import os


class Config(object):
	def __init__(self):
		self.default_config = {
			'global': {
				'format': '%H%r%T',
				'recurse': 'false',
				'ignore_padding': 'true',
				'include_exts': '',
				'exclude_exts': '',
				'get_stats': 'false',
				'stat_order': '',
				'csv': 'false',
				'csv_sep': r'\t',
				'date_format': '%a %b %d %H:%M:%S %Y',
			},
			'regex': {
				'frame_extract': r'((.*)(\D))?(\d+)(.*)',
				'head_group': 0,
				'frame_group': 3,
				'tail_group': 4,
			}
		}
		self.user_config_file = os.path.expanduser('~/.useq.conf')
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
			'Config({recurse=%s, ignore_padding=%s, include_exts=%s,'
			'exclude_exts=%s, get_stats=%s, stat_order=%s, csv=%s, '
			'csv_sep=%s, format=%s)' %
			(self.recurse, self.ignore_padding, self.include_exts,
			 self.exclude_exts, self.get_stats, self.stat_order, self.csv,
			 self.csv_sep, self.format))

	def _load_config(self, cfgparser):
		self.format = cfgparser.get('global', 'format')
		self.recurse = cfgparser.getboolean('global', 'recurse')
		self.ignore_padding = cfgparser.getboolean('global', 'ignore_padding')
		self.include_exts = cfgparser.get('global', 'include_exts').split()
		self.exclude_exts = cfgparser.get('global', 'exclude_exts').split()
		self.get_stats = cfgparser.getboolean('global', 'get_stats')
		self.stat_order = cfgparser.get('global', 'stat_order').split()
		self.csv = cfgparser.getboolean('global', 'csv')
		self.csv_sep = cfgparser.get('global', 'csv_sep')
		self.frame_extract_re = cfgparser.get('regex', 'frame_extract')
		self.head_group = cfgparser.getint('regex', 'head_group')
		self.frame_group = cfgparser.getint('regex', 'frame_group')
		self.tail_group = cfgparser.getint('regex', 'tail_group')

	def _load_user_config(self):
		if os.path.exists(self.user_config_file):
			cfgparser = configparser.RawConfigParser()
			cfgparser.read(self.user_config_file)
			self._load_config(cfgparser)

	def reset_defaults(self):
		self._load_config(self.default_parser)

	def write_user_config(self):
		with open(self.user_config_file, 'w') as f:
			self.default_parser.write(f)
		print('Made user config file at %s' % cfg.user_config_file)


cfg = Config()
