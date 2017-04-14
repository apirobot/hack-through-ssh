# -*- coding: utf-8 -*-
import sys
import argparse
import logging
import logging.config

from base import SFTPServer, SSHServer
from utils import get_info_from_yaml


def create_parser():
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('yaml', help='path to the yaml file that contains '
                                     'server settings')
    parser.add_argument('host_key', help='path to the host key')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    settings = get_info_from_yaml(args.yaml)

    logging.config.dictConfig(settings['logging'])
    logger = logging.getLogger(__name__)

    try:
        SFTPServer(settings['sftp_server_info'], args.host_key).run()
        SSHServer(settings['ssh_server_info'], args.host_key).run()
    except Exception as e:
        logger.exception('*** Caught exception: ' + str(e.__class__) +
                         ': ' + str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
