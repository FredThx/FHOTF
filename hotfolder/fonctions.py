#! /usr/bin/env python
# -*- coding: utf-8 -*-

def get_dest_path(filename, suffix):
    if suffix == ".txt":
        return './txt/'
    else:
        return './olfa/'

def get_cmd(filename):
    return f"notepad {filename}"

def get_destination_path_for_copy(filename):
    return './olfa/'


def get_txt2pdf(filename):
    return False
