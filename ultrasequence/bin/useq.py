import argparse
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


def arg_handler():
	parser = argparse.ArgumentParser()

	parser.add_argument('source',
						type=str,
						help='path to source file or directory to scan.'
						)

	parser.add_argument('output',
						type=str,
						help='output file to save results to.'
						)

	# parser.add_argument('-c', '--configfile',
	# 					action='store_true',
	# 					help='this will read all values from config file '
	# 						 '~/.ultrasequence - setting flags will override'
	# 					)

	parser.add_argument('-M', '--make-user-cfg',
						action=UserConfig,
						)

	parser.add_argument('-v', '--version',
						action='version',
						version='%s v%s' % (NAME, __version__))

	return parser.parse_args()

	# parser.add_argument('-r', '--disable-recurse',
	# 					action='store_false',
	# 					help='this will force disable directory recursion. if '
	# 						 'not specified, will fall back to config file.'
	# 					)
	#
	# parser.add_argument('-c', '--csv')
	# parser.add_argument('-s', '--csv-sep')
	# parser.add_argument('-c', '--csv')
	#
	# parser.add_argument('-i', '--include',
	# 					help=''
	# 					)
	#
	# parser.add_argument('-e', '--exclude',
	# 					help=''
	# 					)
	#
	# parser.add_argument('-S', '--get-stats',
	# 					action='store_false',
	# 					default=cfg.get_stats
	# 					)
	#
	# parser.add_argument('-p', '--ignore-padding')
	# parser.add_argument('-D', '--debug')
	# parser.add_argument('-l', '--logfile')
	# parser.add_argument('-H', '--suppress-logging')
	# parser.add_argument('-H', '--suppress-logging')
	# parser.add_argument('-H', '--suppress-logging')


def main(args):
	pass


if __name__ == '__main__':
	args = arg_handler()
	print('got here')
	main(args)
