# -*- coding: utf-8 -*-
import sys
import threading
import traceback
from collections import namedtuple

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


def authenticate_clients(server_socket, username, password, host_key,
                         connected_clients):
    while True:
        client_socket, address = accept_connection_from_outside(server_socket)

        print 'Got a connection from ' + str(address)

        transport = paramiko.Transport(client_socket)
        transport.add_server_key(host_key)

        server = Server(username, password)
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            print '*** SSH negotiation failed'
            traceback.print_exc()
            sys.exit(1)

        channel = transport.accept()
        if channel is None:
            print '*** No channel'
            sys.exit(1)

        print 'Authenticated!'
        connected_clients.update({address[0]: channel})


def execute_shell_commands(connected_clients):
    Client = namedtuple('Client', 'address, channel')
    current_client = Client(None, None)

    while True:
        if connected_clients:

            if current_client.address is None or current_client.channel is None:
                print '\n'.join(connected_clients.keys())
                address = raw_input('Enter address to connect to: ')
                current_client = Client(address, connected_clients[address])

            if current_client.address:
                shell_prompt = '(%s) $ ' % (current_client.address)
            else:
                shell_prompt = '$ '
            command = raw_input(shell_prompt)

            if command == 'switch':
                address = raw_input('Enter address to connect to: ')
                current_client = Client(address, connected_clients[address])

            elif command == 'list':
                print '\n'.join(connected_clients.keys())

            elif command == 'exit':
                current_client.channel.send(command)
                current_client.channel.recv(1024)
                current_client.channel.close()
                del connected_clients[current_client.address]
                current_client = Client(None, None)
                if not connected_clients:
                    break

            else:
                current_client.channel.send(command)
                response = current_client.channel.recv(1024)
                print response


def start_ssh_server(host, port, backlog, username, password, host_key):
    server_socket = create_server_socket(host, port, backlog)

    connected_clients = {}

    try:
        t = threading.Thread(
            target=authenticate_clients,
            args=(server_socket, username, password, host_key,
                  connected_clients)
        )
        t.daemon = True
        t.start()
    except:
        print '*** SSH authentication failed'
        traceback.print_exc()
        sys.exit(1)

    try:
        execute_shell_commands(connected_clients)
    except:
        print '*** Execution of shell commands failed'
        traceback.print_exc()
        sys.exit(1)
