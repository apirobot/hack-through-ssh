# -*- coding: utf-8 -*-
import json


def get_server_info_from_json(json_file_path):
    with open(json_file_path) as file_handler:
        return json.load(file_handler)
