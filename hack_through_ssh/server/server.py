# -*- coding: utf-8 -*-
import sys
import argparse
import threading
import traceback

import paramiko

from _ssh import start_ssh_server
from _sftp import start_sftp_server
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
        thread = threading.Thread(target=start_sftp_server,
                                  kwargs=server_info['sftp'])
        thread.daemon = True
        thread.start()

        start_ssh_server(**server_info['ssh'])
    except Exception as e:
        print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
