# -*- coding: utf-8 -*-
import sys
import time
import traceback

import paramiko
from sftpserver.stub_sftp import StubServer, StubSFTPServer

from utils import create_server_socket, accept_connection_from_outside


def start_sftp_server(host, port, backlog, host_key):
    server_socket = create_server_socket(host, port, backlog)

    while True:
        client_socket, address = accept_connection_from_outside(server_socket)

        transport = paramiko.Transport(client_socket)
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
