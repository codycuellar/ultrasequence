import argparse
from ultrasequence.config import cfg


def arg_handler():
	parser = argparse.ArgumentParser()

	parser.add_argument('source',
						help='path to source file or directory to scan.'
						)

	parser.add_argument('output',
						help='output file to save results to.'
						)

	parser.add_argument('-R', '--recurse',
						help='recurse child directories if source is a directory'
						)

	parser.add_argument('-c', '--csv')
	parser.add_argument('-s', '--csv-sep')
	parser.add_argument('-c', '--csv')

	parser.add_argument('-i', '--include',
						help=''
						)

	parser.add_argument('-e', '--exclude',
						help=''
						)

	parser.add_argument('-S', '--get-stats',
						action='store_false',
						default=cfg.get_stats
						)

	parser.add_argument('-p', '--ignore-padding')
	parser.add_argument('-D', '--debug')
	parser.add_argument('-l', '--logfile')
	parser.add_argument('-H', '--suppress-logging')
	parser.add_argument('-H', '--suppress-logging')
	parser.add_argument('-H', '--suppress-logging')


def main(args):
	pass


if __name__ == '__main__':
	args = arg_handler()
	main(args)
