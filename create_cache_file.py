__author__ = 'Tim Michael Heinz Wolf'
__version__ = '0.0'
__license__ = 'GPL'
__email__ = 'tim.wolf@mpi-hd.mpg.de'

import sys
import argparse
from inspire_info.InspireInfo import InspireInfo


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Scraping of inspire for institute publications')
    parser.add_argument('--config',
                        type=str,
                        help="Config file to read.",
                        required=True)

    return dict(vars(parser.parse_args(args)))


def main(arguments):
    parsed_args = parse_args(args=arguments)
    inspire_getter = InspireInfo(config_path=parsed_args["config"])
    inspire_getter.get_data(retrieve=True)
    inspire_getter.write_data()

if __name__ == "__main__":
    main(sys.argv[1:])
