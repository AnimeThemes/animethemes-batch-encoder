from ._encode_webm import EncodeWebM
from ._encoding_config import EncodingConfig
from ._interface import Interface
from ._seek_collector import SeekCollector
from ._source_file import SourceFile
from ._utils import commandfile_arg_type
from ._utils import configfile_arg_type
from appdirs import AppDirs

import argparse
import configparser
import copy
import logging
import os
import shutil
import subprocess
import sys


def main():
    # Load/Validate Arguments
    parser = argparse.ArgumentParser(prog='batch_encoder',
                                     description='Generate/Execute FFmpeg commands for files in acting directory',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--generate', '-g', action='store_true', help='Generate commands and write to file')
    parser.add_argument('--execute', '-e', action='store_true', help='Execute commands from file')
    parser.add_argument('--custom', '-c', action='store_true', help='Customize some options for each seek')
    parser.add_argument('--file', nargs='?', default='commands.txt', type=commandfile_arg_type,
                        help='1: Name of file commands are written to (default: commands.txt)\n'
                             '2: Name of file commands are executed from (default: commands.txt)\n'
                             '3: Name of file commands are written to (default: commands.txt)')
    parser.add_argument('--configfile', nargs='?', default='batch_encoder.ini', type=configfile_arg_type,
                        help='Name of config file (default: batch_encoder.ini)\n'
                             'If the file does not exist, default configuration will be written\n'
                             'The file is expected to exist in the same directory as this script')
    parser.add_argument('--inputfile', nargs='?', help='Set the input files separated by two commas')
    parser.add_argument('--loglevel', nargs='?', default='info', choices=['debug', 'info', 'error'],
                        help='Set logging level')
    args = parser.parse_args()

    # Logging Config
    logging.basicConfig(stream=sys.stdout, level=logging.getLevelName(args.loglevel.upper()),
                        format='%(levelname)s: %(message)s')

    # Env Check: Check that dependencies are installed
    if shutil.which('ffmpeg') is None:
        logging.error('FFmpeg is required')
        sys.exit()

    if shutil.which('ffprobe') is None:
        logging.error('FFprobe is required')
        sys.exit()

    # Write default config file if it doesn't exist
    config = configparser.ConfigParser()
    dirs = AppDirs('batch_encoder', 'AnimeThemes')
    config_file = os.path.join(dirs.user_config_dir, args.configfile)
    if not os.path.exists(config_file):
        config['Encoding'] = {EncodingConfig.config_allowed_filetypes: EncodingConfig.default_allowed_filetypes,
                              EncodingConfig.config_encoding_modes: EncodingConfig.default_encoding_modes,
                              EncodingConfig.config_crfs: EncodingConfig.default_crfs,
                              EncodingConfig.config_threads: EncodingConfig.default_threads,
                              EncodingConfig.config_limit_size_enable: EncodingConfig.default_limit_size_enable,
                              EncodingConfig.config_alternate_source_files: EncodingConfig.default_alternate_source_files,
                              EncodingConfig.create_preview: EncodingConfig.default_create_preview,
                              EncodingConfig.config_include_unfiltered: EncodingConfig.default_include_unfiltered,
                              EncodingConfig.config_default_video_stream: '',
                              EncodingConfig.config_default_audio_stream: ''}
        config['VideoFilters'] = EncodingConfig.default_video_filters

        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w', encoding='utf8') as f:
            config.write(f)

    # Load config file
    config.read(config_file)
    encoding_config = EncodingConfig.from_config(config)

    commands = []

    # Set the mode to integer or prompt to the user
    if args.generate and args.execute:
        mode = 3
    elif args.generate:
        mode = 1
    elif args.execute:
        mode = 2
    else:
        mode = Interface.choose_mode()

    # Generate commands from source file candidates in current directory
    if mode == 1 or mode == 3:
        if args.inputfile is None:
            source_file_candidates = [f for f in os.listdir('.') if f.endswith(tuple(encoding_config.allowed_filetypes))]

            if not source_file_candidates:
                logging.error('No source file candidates in current directory')
                sys.exit()

            source_files = Interface.choose_source_files(source_file_candidates)
        else:
            source_files = args.inputfile.split(',,')

        source_file_info = {}

        for source_file in source_files:
            source_file_info[source_file] = SourceFile.from_file(source_file, encoding_config)

        for file, file_value in source_file_info.items():
            try:
                is_collector_valid = False
                seek_collector = None
                while not is_collector_valid:
                    print(f'\033[92mSource File: {file}\033[0m')
                    seek_collector = SeekCollector(file_value)
                    is_collector_valid = seek_collector.is_valid()

                for seek in seek_collector.get_seek_list():
                    new_encoding_config = copy.copy(encoding_config)

                    print(f'\033[92mOutput Name: {seek.output_name}\033[0m')
                    new_encoding_config = Interface.video_filters(new_encoding_config)

                    if args.custom:
                        print(f'\033[92mOutput Name: {seek.output_name}\033[0m')
                        new_encoding_config = Interface.custom_options(new_encoding_config)
                        
                    logging.info(f'Generating commands with seek ss: \'{seek.ss}\', to: \'{seek.to}\'')
                    encode_webm = EncodeWebM(file_value, seek)
                    load_commands = encode_webm.get_commands(new_encoding_config)
                    commands = commands + load_commands

            except KeyboardInterrupt:
                logging.info(f'Exiting from inclusion of file \'{file}\' after keyboard interrupt')
        
        # Alternate lines per source files
        if encoding_config.alternate_source_files == True:
            output_list = []
            lines_per_source = len(load_commands)
            for i in range(lines_per_source):
                output_list.append(commands[i])
                for k in range(1, len(commands) // lines_per_source):
                    output_list.append(commands[i + lines_per_source * k])

            commands = output_list

        # Write commands to file
        logging.info(f'Writing {len(commands)} commands to file \'{args.file}\'...')
        with open(args.file, mode='w', encoding='utf8') as f:
            for command in commands:
                f.write(command + '\n')

        # Execute commands in memory and write commands to file if requested
        if mode == 3:
            logging.info(f'Executing {len(commands)} commands...')
            for command in commands:
                subprocess.call(command, shell=True)


    # Read and execute commands from file
    if mode == 2:
        if not os.path.isfile(args.file):
            logging.error(f'File \'{args.file}\' does not exist')
            sys.exit()

        with open(args.file, mode='r', encoding='utf8') as f:
            for command in f:
                commands.append(command)

        logging.info(f'Reading {len(commands)} commands from file \'{args.file}\'...')

        for command in commands:
            subprocess.call(command, shell=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.error('Exiting after keyboard interrupt')