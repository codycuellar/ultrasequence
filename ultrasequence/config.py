try:
	import configparser
except ImportError:
	import ConfigParser as configparser
import shutil
import os


LOCAL_CONFIG = os.path.expanduser('~/.ultrasequence')

if os.path.exists(LOCAL_CONFIG):
	pass
else:
	this_dir = os.path.dirname(__file__)
	CONFIG_TEMPLATE = os.path.join(this_dir, 'config_template.ini')
	try:
		shutil.copy(
			CONFIG_TEMPLATE,
			LOCAL_CONFIG
		)
	except FileNotFoundError:
		LOCAL_CONFIG = CONFIG_TEMPLATE


cfgparser = configparser.ConfigParser()
cfgparser.read(LOCAL_CONFIG)

ignore_padding = cfgparser['global'].getboolean('ignore_padding')
include_exts = cfgparser['global']['include_exts'].split()
exclude_exts = cfgparser['global']['exclude_exts'].split()
get_stats = cfgparser['stats'].getboolean('get_stats')
stat_order = cfgparser['stats']['stat_order'].split()
csv = cfgparser['csv'].getboolean('csv')
csv_sep = cfgparser['csv']['csv_sep']
