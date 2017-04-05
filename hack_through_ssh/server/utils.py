# -*- coding: utf-8 -*-
import sys
import json
import socket
import traceback


def get_server_info_from_json(json_file_path):
    with open(json_file_path) as file_handler:
        return json.load(file_handler)


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