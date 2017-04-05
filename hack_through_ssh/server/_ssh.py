# -*- coding: utf-8 -*-
import sys
import threading
import traceback

import paramiko

from utils import create_server_socket, accept_connection_from_outside


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