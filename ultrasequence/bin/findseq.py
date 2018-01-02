import argparse
import os
import ultrasequence as us
from ultrasequence.version import __version__, NAME
from ultrasequence.config import cfg


class UserConfig(argparse.Action):
	def __init__(self,
				 option_strings,
				 dest=argparse.SUPPRESS,
				 default=argparse.SUPPRESS,
				 help="make a local config file in user home dir and exit"):
		super(UserConfig, self).__init__(
			option_strings=option_strings,
			dest=dest,
			default=default,
			nargs=0,
			help=help)

	def __call__(self, parser, namespace, values, option_string=None):
		cfg.write_user_config()
		parser.exit()


def get_args():
	parser = argparse.ArgumentParser(prog=NAME)

	parser.add_argument('source',
						type=str,
						help='path to source file or directory to scan.'
						)

	# parser.add_argument('output',
	# 					type=str,
	# 					help='output file to save results to.'
	# 					)

	parser.add_argument('-v', '--version',
						action='version',
						version='%s v%s' % (NAME, __version__)
						)

	parser.add_argument('-M', '--make-user-cfg',
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

	parser.add_argument('-c', '--csv',
						action='store_true',
						help=''
						)

	parser.add_argument('--csv-sep',
						type=str,
						help=''
						)

	parser.add_argument('-s', '--get-stats',
						action='store_true',
						help=''
						)

	parser.add_argument('--stat-order',
						type=str,
						nargs='+',
						help='order of stats after separating a csv for file '
							 'parser'
						)

	parser.add_argument('-p', '--strict-padding',
						action='store_true',
						help='disables the ignore_padding rule. This will '
							 'treat all files with different amount of digit '
							 'padding as separate sequences.'
						)

	# parser.add_argument('-H', '--suppress-logging')
	# parser.add_argument('-l', '--logfile')
	# parser.add_argument('-D', '--debug')

	return parser.parse_args()


def main():
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
	if args.csv:
		cfg.csv = True
	if args.csv_sep:
		cfg.csv_sep = args.csv_sep
	if args.get_stats:
		cfg.get_stats = args.get_stats
	if args.strict_padding:
		cfg.ignore_padding = False

	parser = us.Parser(include_exts=cfg.include_exts,
					   exclude_exts=cfg.exclude_exts,
					   get_stats=cfg.get_stats,
					   ignore_padding=cfg.ignore_padding)

	if os.path.isdir(args.source):
		parser.parse_directory(args.source, recurse=cfg.recurse)
	elif os.path.isfile(args.source):
		parser.parse_file(args.source, csv=cfg.csv, csv_sep=cfg.csv_sep,
						  stat_order=cfg.stat_order)

	output = parser.sequences + parser.single_frames + parser.non_sequences + \
			 parser.collisions + parser.excluded
	output.sort(key=lambda x: x.abspath.lower())

	for x in output:
		print(x)


if __name__ == '__main__':
	main()
