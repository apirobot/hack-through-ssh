# -*- coding: utf-8 -*-
import sys
import json
import socket
import argparse
import threading
import traceback

import paramiko


def create_parser():
    parser = argparse.ArgumentParser(description='SSH Server')
    parser.add_argument('json', help='path to the json file that '
                                     'contains information about server '
                                     '(hostname, username, password)')
    parser.add_argument('host_key', help='path to the host key')
    return parser


class Server(paramiko.ServerInterface):

    def __init__(self, username, password):
        self.event = threading.Event()
        self._username = username
        self._password = password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == self._username) and (password == self._password):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


def get_server_info_from_json(json_file_path):
    with open(json_file_path) as file_handler:
        return json.load(file_handler)


def main():
    parser = create_parser()
    args = parser.parse_args()

    server_info = get_server_info_from_json(args.json)

    hostname = server_info['hostname']
    username = server_info['username']
    password = server_info['password']

    host_key = paramiko.RSAKey(filename=args.host_key)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((hostname, 22))
    except Exception as e:
        print '*** Bind failed: ' + str(e)
        traceback.print_exc()
        sys.exit(1)

    try:
        sock.listen(1)
        print 'Listening for connection ...'
        client, addr = sock.accept()
    except Exception as e:
        print '*** Listen/accept failed: ' + str(e)
        traceback.print_exc()
        sys.exit(1)

    print 'Got a connection from ' + str(addr)

    try:
        t = paramiko.Transport(client)
        try:
            t.load_server_moduli()
        except:
            print '(Failed to load moduli)'
            raise
        t.add_server_key(host_key)
        server = Server(username, password)
        try:
            t.start_server(server=server)
        except paramiko.SSHException:
            print '*** SSH negotiation failed'
            sys.exit(1)

        chan = t.accept(1)
        if chan is None:
            print '*** No channel'
            sys.exit(1)
        print 'Authenticated!'

        print chan.recv(1024)
        chan.send('Yes, I can see that!')

    except Exception as e:
        print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)


if __name__ == '__main__':
    main()
