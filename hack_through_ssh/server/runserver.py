# -*- coding: utf-8 -*-
import sys
import argparse
import traceback

import paramiko

from base import SFTPServer, SSHServer
from utils import get_server_info_from_json


def create_parser():
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('json', help='path to the json file that '
                                     'contains information about server '
                                     '(hostname, username, password, ...)')
    parser.add_argument('host_key', help='path to the host key')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    server_info = get_server_info_from_json(args.json)
    for key in server_info.keys():
        server_info[key]['host_key'] = paramiko.RSAKey(filename=args.host_key)

    try:
        SFTPServer(**server_info['sftp']).run()
        SSHServer(**server_info['ssh']).run()
    except Exception as e:
        print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
