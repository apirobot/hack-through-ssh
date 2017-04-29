# -*- coding: utf-8 -*-
from hack_through_ssh.server.base import (create_server_socket,
                                          accept_connection_from_outside)


def test_create_server_socket(mocker):
    mock_bind = mocker.patch('hack_through_ssh.server.base.socket.socket.bind')
    mock_listen = mocker.patch('hack_through_ssh.server.base.socket.socket.listen')

    host, port, backlog = '1.2.3.4', 2222, 42

    create_server_socket(host, port, backlog)

    mock_bind.assert_called_once_with((host, port))
    mock_listen.assert_called_once_with(backlog)


def test_accept_connection_from_outside(mocker):
    socket = mocker.MagicMock()
    accept_connection_from_outside(socket.return_value)
    socket.return_value.accept.assert_called()
