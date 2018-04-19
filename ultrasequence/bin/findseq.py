"""
FindSeq
=======
This module is the command-line utility entry-point. It parses the command-
line for arguments, and overrides any pre-loaded configs with those arguments.
The order of operation option loading is:

# Load default config defined in the ultrasequence.config.UsConfig class the
CONFIG instance
# Check for ~/.ultrasequence.conf and overload all parameters in the CONFIG
instance
# Parse command line and overwrite any options present to CONFIG

For instance, if no config file is present, the defaults will be loaded. If the
user provides the --format flag, the command line values will overwrite the
defaults in CONFIG. On the other hand, if a config file is present and the
user puts no options on the command line, all the values from the local config
file will be used.
"""
import argparse
import logging
import os
from ultrasequence.config import CONFIG as cfg
from ultrasequence.parsing import Parser
from ultrasequence.version import __version__, NAME


logger = logging.getLogger(__name__)


class UserConfig(argparse.Action):
	"""
	A custom class which allows an operation-and-exit style behaviour like
	with --help or --version, but for the case of writing a config file.
	"""
	def __init__(self,
				 option_strings,
				 dest=argparse.SUPPRESS,
				 default=argparse.SUPPRESS,
				 help_="make a local config file in user home dir and exit"):
		super(UserConfig, self).__init__(
			option_strings=option_strings,
			dest=dest,
			default=default,
			nargs=0,
			help=help_)

	def __call__(self, parser, namespace, values, option_string=None):
		cfg.write_user_config()
		parser.exit()


def get_args():
	""" Parse the command line args and return an argparser object. """
	parser = argparse.ArgumentParser(prog=NAME)

	parser.add_argument('source',
						type=str,
						help='path to source file or directory to scan.'
						)

	parser.add_argument('-v', '--version',
						action='version',
						version='%s v%s' % (NAME, __version__)
						)

	parser.add_argument('--make-config',
						action=UserConfig,
						)

	parser.add_argument('-I', '--ignore-config',
						action='store_true',
						help='ignore the user config file if it exists'
						)

	parser.add_argument('-f', '--format',
						type=str,
						help=''
						)

	parser.add_argument('-i', '--include',
						type=str,
						nargs='+',
						help='list of file extensions without preceding dot '
							 'to include in sequencer'
						)

	parser.add_argument('-e', '--exclude',
						type=str,
						nargs='+',
						help='list of file extensions without preceding dot '
							 'to exclude in sequencer'
						)

	parser.add_argument('-R', '--recurse',
						action='store_true',
						help='enable directory recursion for directory parser.'
						)

	parser.add_argument('-s', '--get-stats',
						action='store_true',
						help=''
						)

	parser.add_argument('-p', '--strict-padding',
						action='store_true',
						help='disables the ignore_padding rule. This will '
							 'treat all files with different amount of digit '
							 'padding as separate sequences.'
						)

	return parser.parse_args()


def main():
	""" Set up the args and run the parser. """
	args = get_args()

	if args.ignore_config:
		cfg.reset_defaults()
	if args.format:
		cfg.format = args.format
	if args.include:
		cfg.include_exts = args.include
	if args.exclude:
		cfg.exclude_exts = args.exclude
	if args.recurse:
		cfg.recurse = True
	if args.strict_padding:
		cfg.ignore_padding = False

	parser = Parser(include_exts=cfg.include_exts,
	                exclude_exts=cfg.exclude_exts,
	                get_stats=cfg.get_stats,
	                ignore_padding=cfg.ignore_padding)

	if os.path.isdir(args.source):
		parser.parse_directory(args.source, recurse=cfg.recurse)
	elif os.path.isfile(os.path.expanduser(args.source)):
		parser.parse_file(args.source)

	output = parser.sequences + parser.orphan_frames + \
	         parser.no_frame_numbers + parser.collisions
	output.sort(key=lambda s: s.abspath.lower())

	for x in output:
		print(x)


if __name__ == '__main__':
	main()
