# -*- coding: utf-8 -*-
import sys
import time
import socket
import argparse
import threading
import traceback

import paramiko
from sftpserver.stub_sftp import StubServer, StubSFTPServer

from helpers import get_server_info_from_json


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


def create_server_socket(host, port, backlog):
    """
    Creates a server socket that listening for connections.

    :param backlog: the number of unaccepted connections that the system
                    will allow before refusing new connections.
    :type backlog: int
    """

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
    except Exception as e:
        print '*** Bind failed: ' + str(e)
        traceback.print_exc()
        sys.exit(1)

    try:
        server_socket.listen(backlog)
    except Exception as e:
        print '*** Listen failed: ' + str(e)
        traceback.print_exc()
        sys.exit(1)

    return server_socket


def accept_connection_from_outside(server_socket):
    """
    Accepts a connection from outside.

    :returns: (socket object, address info)
    :rtype: tuple
    """

    try:
        return server_socket.accept()
    except Exception as e:
        print '*** Accept failed: ' + str(e)
        traceback.print_exc()
        sys.exit(1)


def start_ssh_server(host, port, backlog, username, password, host_key):
    server_socket = create_server_socket(host, port, backlog)
    client_socket, address = accept_connection_from_outside(server_socket)

    print 'Got a connection from ' + str(address)

    with paramiko.Transport(client_socket) as transport:
        transport.add_server_key(host_key)

        server = Server(username, password)
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            print '*** SSH negotiation failed'
            sys.exit(1)

        channel = transport.accept()
        if channel is None:
            print '*** No channel'
            sys.exit(1)

        print 'Authenticated!'

        print 'Enter your shell commands:'
        while True:
            command = raw_input('$ ')
            channel.send(command)
            response = channel.recv(1024)
            if response == 'exit':
                channel.close()
                break
            print response


def start_sftp_server(host, port, backlog, host_key):
    server_socket = create_server_socket(host, port, backlog)

    while True:
        client_socket, address = accept_connection_from_outside(server_socket)

        with paramiko.Transport(client_socket) as transport:
            transport.add_server_key(host_key)
            transport.set_subsystem_handler(
                'sftp', paramiko.SFTPServer, StubSFTPServer
            )

            server = StubServer()
            try:
                transport.start_server(server=server)
            except Exception as e:
                print '*** SFTP negotiation failed: ' + str(e)
                traceback.print_exc()
                sys.exit(1)

            channel = transport.accept()
            while transport.is_active():
                time.sleep(1)


def main():
    parser = create_parser()
    args = parser.parse_args()

    server_info = get_server_info_from_json(args.json)
    host_key = paramiko.RSAKey(filename=args.host_key)

    try:
        sftp_server_info = {
            'host': server_info['hostname'],
            'port': 3373,
            'backlog': 10,
            'host_key': host_key
        }
        thread = threading.Thread(target=start_sftp_server,
                                  kwargs=sftp_server_info)
        thread.daemon = True
        thread.start()

        ssh_server_info = {
            'host': server_info['hostname'],
            'username': server_info['username'],
            'password': server_info['password'],
            'port': 22,
            'backlog': 1,
            'host_key': host_key
        }
        start_ssh_server(**ssh_server_info)
    except Exception as e:
        print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
