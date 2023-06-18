import argparse
import os
import sys


# Convert position to seconds, needed for integrity tests
def string_to_seconds(time):
    return sum(x * float(t) for x, t in zip([1, 60, 3600], reversed(time.split(':'))))


# Validate Arguments: check that file can be written to
def file_arg_type(arg_value):
    if not os.access(arg_value, os.W_OK):
        try:
            open(arg_value, 'w').close()
            os.remove(arg_value)
        except OSError:
            raise argparse.ArgumentTypeError(f'File \'{arg_value}\' cannot be created')
    return arg_value


# Validate Arguments: check that command file can be written to and is a TXT file type
# New users were providing source files for this argument and overwriting them
def commandfile_arg_type(arg_value):
    file_arg_type(arg_value)
    if not arg_value.endswith('.txt'):
        raise argparse.ArgumentTypeError(f'Command File \'{arg_value}\' must use \'.txt\' file extension')
    return arg_value


# Validate Arguments: check that config file can be written to and is INI file type
def configfile_arg_type(arg_value):
    config_file = os.path.join(sys.path[0], arg_value)
    file_arg_type(config_file)
    if not arg_value.endswith('.ini'):
        raise argparse.ArgumentTypeError(f'Config File \'{arg_value}\' must use \'.ini\' file extension')
    return arg_value
