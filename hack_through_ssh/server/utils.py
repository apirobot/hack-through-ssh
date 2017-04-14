# -*- coding: utf-8 -*-
import threading
import functools

import yaml


def get_info_from_yaml(yaml_file_path):
    with open(yaml_file_path) as file_handler:
        return yaml.load(file_handler)


def is_want_to_close():
    while True:
        answer = raw_input('Do you want to close the server? [y/n] ')
        if answer == 'y' or answer == 'yes':
            return True
        elif answer == 'n' or answer == 'no':
            return False


def threaded(func=None, daemon=False):
    """
    Decorator that runs `func` in a separate thread.

    :param daemon: if `True` then thread stops if no alive non-daemon threads
                   are left.
    :type daemon: bool
    :returns: created Thread object.
    """
    def _outer_wrapper(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            t = threading.Thread(target=func, args=args, kwargs=kwargs)
            t.daemon = daemon
            t.start()
            return t
        return _wrapper
    return _outer_wrapper(func) if func is not None else _outer_wrapper
