#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import argparse
import config
from executor import Executor
import logging
import checkargs
import time
from stats import Stats
from prepare import Prepare


def main():
    parser = argparse.ArgumentParser(description='Running Simcoin. A Bitcoin Network Simulator.')

    parser.add_argument('-v'
                        , '--verbose'
                        , help='Increase output verbosity'
                        , action='store_true'
                        )
    parser.add_argument('--selfish-nodes-args'
                        , help='Set args for selfish nodes. '
                               'Set them as string and if you use just one add a space at the end. Eg.: "--arg "'
                        , default=''
                        )
    parser.add_argument('--tick-duration'
                        , help='Set the duration of one tick in seconds.'
                        , default=1
                        , type=checkargs.check_positive_float
                        )

    args = parser.parse_args()

    log_formatter = logging.Formatter("%(asctime)s.%(msecs)03d000 executor [%(threadName)-12.12s] "
                                      "[%(levelname)-5.5s]  %(message)s", "%Y-%m-%d %H:%M:%S")
    logging.Formatter.converter = time.gmtime
    root_logger = logging.getLogger()

    file_handler = logging.FileHandler(config.log_file, mode='w')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    if args.verbose:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

    for image in [config.node_image, config.selfish_node_image]:
        if os.system("docker inspect " + image + " > /dev/null") != 0:
            raise Exception("Image {} not found".format(image))

    for file in [config.network_config, config.tick_csv]:
        if not os.path.isfile(file):
            raise Exception("{} file not found. Please generate file before starting Simcoin.".format(file))

    logging.info("arguments called with: {}".format(sys.argv))
    logging.info("parsed arguments: {}".format(args))

    executor = Executor(args)

    stats = Stats(executor)
    executor.stats = stats

    prepare = Prepare(executor)
    executor.prepare = prepare

    executor.execute()

if __name__ == "__main__":
    main()
