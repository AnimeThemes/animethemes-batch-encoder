from ._bitrate_mode import BitrateMode

import inquirer
import logging
import re
import sys

class Interface:
    # Time Duration Specification: https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax
    time_pattern = re.compile('^([0-5]?\d:){1,2}[0-5]?\d(?=\.\d+$|$)|\d+(?=\.\d+$|$)')

    # Validations
    validate_time = lambda _, x: all(Interface.time_pattern.match(y) for y in x.split(','))
    validate_encoding_modes = lambda _, x: all(y.strip().upper() in [BitrateMode.VBR.name, BitrateMode.CBR.name, BitrateMode.CQ.name] for y in x.split(','))
    validate_digits = lambda _, x: all(y.strip().isdigit() for y in x.split(',')) or len(x.strip()) == 0

    # Prompt the user for text questions
    def prompt_text(message, validate=lambda _, x: x):
        answer = inquirer.prompt([inquirer.Text('text', message=message, validate=validate)])

        if answer is None:
            return 'NoName'

        logging.debug(f'[Interface.prompt_text] answer["text"]: \'{answer["text"]}\'')

        return answer['text']
    
    # Prompt the user for time questions
    def prompt_time(message, validate=validate_time):
        answer = inquirer.prompt([inquirer.Text('time', message=message, validate=validate)])

        if answer is None:
            return ''

        logging.debug(f'[Interface.prompt_time] answer["time"]: \'{answer["time"]}\'')

        return answer['time']

    # Prompt the user for our mode options to run to the user
    def choose_mode():
        modes = [('Generate commands', 1), ('Execute commands', 2), ('Generate and execute commands', 3)]
        answer = inquirer.prompt([inquirer.List('mode', message='Mode (Enter)', choices=modes)])

        if answer is None:
            sys.exit()

        logging.debug(f'[Interface.choose_mode] answer["mode"]: \'{answer["mode"]}\'')

        return answer['mode']
    
    # Prompt the user for source files to choose
    def choose_source_files(source_files):
        answer = inquirer.prompt([inquirer.Checkbox('source_files', message='Source Files (Space to select)', choices=source_files)])

        if answer is None:
            sys.exit()

        if len(answer['source_files']) == 0:
            logging.error('Select at least one file')
            sys.exit()

        logging.debug(f'[Interface.choose_source_files] answer["source_files"]: \'{answer["source_files"]}\'')

        return answer['source_files']
      
    # Prompt the user for audio filters options
    def audio_filters_options(output_name):
        audio_filters = {
            'Exit': False,
            'Custom': '',
            'Fade In': 0,
            'Fade Out': {
                'Start Time': 0,
                'Exp': 0
            },
            'Mute': {
                'Start Time': 0,
                'End Time': 0
            } 
        }

        while not audio_filters['Exit']:
            print(f'\n\033[92mOutput Name: {output_name}\033[0m')
            answer = inquirer.prompt([inquirer.List('audio_filters', message='Audio Filters (Enter)', choices=list(audio_filters.keys()))])

            if answer is None:
                audio_filters['Exit'] = True

            elif answer['audio_filters'] == 'Fade In':
                audio_filters['Fade In'] = Interface.prompt_time('Exponential Value').strip() or '0'

            elif answer['audio_filters'] == 'Fade Out':
                audio_filters['Fade Out']['Start Time'] = Interface.prompt_time('Start Time').strip() or '0'
                audio_filters['Fade Out']['Exp'] = Interface.prompt_time('Exponential Value').strip() or '0'
                     
            elif answer['audio_filters'] == 'Mute':
                audio_filters['Mute']['Start Time'] = Interface.prompt_time('Start Time').strip() or '0'
                audio_filters['Mute']['End Time'] = Interface.prompt_time('End Time').strip() or '0'

            elif answer['audio_filters'] == 'Custom':
                custom_audio_filter = Interface.prompt_text('Custom Audio Filter(s)').strip()
                audio_filters['Custom'] = custom_audio_filter

            else:
                audio_filters['Exit'] = True

        audio_filters_list = []

        if float(audio_filters['Fade In']) > 0:
            audio_filters_list.append(f"afade=d={audio_filters['Fade In']}:curve=exp")
        if float(audio_filters['Fade Out']['Exp']) > 0:
            audio_filters_list.append(f"afade=t=out:st={audio_filters['Fade Out']['Start Time']}:d={audio_filters['Fade Out']['Exp']}")
        if float(audio_filters['Mute']['Start Time']) > 0 or float(audio_filters['Mute']['End Time']) > 0:
            audio_filters_list.append(f"volume=enable='between(t,{audio_filters['Mute']['Start Time']},{audio_filters['Mute']['End Time']})':volume=0")
        if len(audio_filters['Custom']) > 0:
            audio_filters_list.append(audio_filters['Custom'])

        logging.debug(
            f'[Interface.audio_filters_options] '
            f'audio_filters["Fade In"]: \'{audio_filters["Fade In"]}\', '
            f'audio_filters["Fade Out"]["Start Time"]: \'{audio_filters["Fade Out"]["Start Time"]}\', '
            f'audio_filters["Fade Out"]["Exp"]: \'{audio_filters["Fade Out"]["Exp"]}\', '
            f'audio_filters["Mute"]["Start Time"]: \'{audio_filters["Mute"]["Start Time"]}\', '
            f'audio_filters["Mute"]["End Time"]: \'{audio_filters["Mute"]["End Time"]}\', '
            f'audio_filters["Custom"]: \'{audio_filters["Custom"]}\''
        )

        return ','.join(audio_filters_list)
    
    # Prompt the user for our list of video filters
    def video_filters(encoding_config):
        video_filters_options = {
            'No Filters': None,
            'scale=-1:720': '720p',
            'scale=-1:720,hqdn3d=0:0:3:3,gradfun,unsharp': 'filtered-720p',
            'hqdn3d=0:0:3:3,gradfun,unsharp': 'filtered',
            'hqdn3d=0:0:3:3': 'lightdenoise',
            'hqdn3d=1.5:1.5:6:6': 'heavydenoise',
            'unsharp': 'unsharp',
            'Custom': 'custom'
        }
        
        if encoding_config.include_unfiltered:
            encoding_config.video_filters.append((None, 'No Filters'))

        answer = inquirer.prompt([
            inquirer.Checkbox('video_filters', message='Select Video Filters (Space to select)',
                            choices=video_filters_options.keys(), default=[tp[1] for tp in encoding_config.video_filters])
        ])

        if answer is None:
            return encoding_config

        tp_list = [(name, filter_string) for filter_string, name in video_filters_options.items() if filter_string in answer['video_filters']]

        if 'Custom' in answer['video_filters']:
            tp_list.remove(('custom', 'Custom'))
            custom_video_filters = Interface.prompt_text('Custom Video Filters (Separate with ",," if more than one)').split(',,')
            tp_list.extend([(f'custom{i + 1}', value) for i, value in enumerate(custom_video_filters)])

        encoding_config.video_filters = tp_list

        logging.debug(f'[Interface.video_filters] tp_list: \'{tp_list}\'')

        return encoding_config

    # Prompt the user for custom options if requested
    def custom_options(encoding_config):
        create_preview = encoding_config.create_preview
        limit_size_enable = encoding_config.limit_size_enable
        encoding_modes = encoding_config.encoding_modes
        crfs = encoding_config.crfs
        cbr_bitrates = encoding_config.cbr_bitrates
        cbr_max_bitrates = encoding_config.cbr_max_bitrates

        answer = inquirer.prompt([
            inquirer.Confirm('create_preview', message='Create Preview?', default=create_preview),
            inquirer.Confirm('limit_size_enable', message='Limit Size Enable?', default=limit_size_enable),
            inquirer.Text('encoding_modes', message='Encoding Modes', default=','.join(encoding_modes), validate=Interface.validate_encoding_modes),
        ])

        if answer is None:
            return encoding_config
        
        encoding_mode_questions = []
        for encoding_mode in answer['encoding_modes'].split(','):
            if encoding_mode == BitrateMode.VBR.name or encoding_mode == BitrateMode.CQ.name:
                encoding_mode_questions.append(inquirer.Text('crfs', message='CRFs', default=','.join(crfs), validate=Interface.validate_digits))
            if encoding_mode == BitrateMode.CBR.name:
                encoding_mode_questions.append(inquirer.Text('cbr_bitrates', message='Bit Rates', default=','.join(cbr_bitrates), validate=Interface.validate_digits))
                encoding_mode_questions.append(inquirer.Text('cbr_max_bitrates', message='Max Bit Rates', default=','.join(cbr_max_bitrates), validate=Interface.validate_digits))

        answer_em = inquirer.prompt(encoding_mode_questions)

        encoding_config.create_preview = answer['create_preview']
        encoding_config.limit_size_enable = answer['limit_size_enable']
        encoding_config.encoding_modes = answer['encoding_modes'].split(',')

        if 'crfs' in answer_em:
            encoding_config.crfs = answer_em['crfs'].split(',')
        if 'cbr_bitrates' in answer_em and 'cbr_max_bitrates' in answer_em:
            encoding_config.cbr_bitrates = [x + 'k' for x in answer_em['cbr_bitrates'].split(',')] if len(answer_em['cbr_bitrates'].strip()) != 0 else None
            encoding_config.cbr_max_bitrates = [x + 'k' for x in answer_em['cbr_max_bitrates'].split(',')] if len(answer_em['cbr_max_bitrates'].strip()) != 0 else None

        logging.debug(
            f'[Interface.custom_options] '
            f'encoding_config.create_preview: \'{encoding_config.create_preview}\', '
            f'encoding_config.limit_size_enable: \'{encoding_config.create_preview}\', '
            f'encoding_config.encoding_modes: \'{encoding_config.encoding_modes}\', '
            f'encoding_config.crfs: \'{encoding_config.crfs}\', '
            f'encoding_config.cbr_bitrates: \'{encoding_config.cbr_bitrates}\', '
            f'encoding_config.cbr_max_bitrates: \'{encoding_config.cbr_max_bitrates}\''
        )

        return encoding_config