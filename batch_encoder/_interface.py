import inquirer
import logging
import re

class Interface:
    # Time Duration Specification: https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax
    time_pattern = re.compile('^([0-5]?\d:){1,2}[0-5]?\d(?=\.\d+$|$)|\d+(?=\.\d+$|$)')

    # Prompt the mode options to run to the user
    def choose_mode():
        modes = {
            'Generate commands': 1,
            'Execute commands': 2,
            'Generate and execute commands': 3
        }

        question = [inquirer.List('mode', message='Mode (Enter)', choices=list(modes.keys()))]
        answer = inquirer.prompt(question)

        logging.debug(f'[Interface.choose_mode] answer["mode"]: \'{answer["mode"]}\'')

        return modes[answer['mode']]
    
    # Prompt the source files to choose
    def choose_source_files(source_files):
        question = [inquirer.Checkbox('source_files', message='Source Files (Space)', choices=source_files)]
        answer = inquirer.prompt(question)

        logging.debug(f'[Interface.choose_source_files] answer["source_files"]: \'{answer["source_files"]}\'')

        return answer['source_files']
    
    # Prompt the audio filters options
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
            question = [inquirer.List('audio_filters', message='Audio Filters (Enter)', choices=list(audio_filters.keys()))]
            answer = inquirer.prompt(question)

            if answer['audio_filters'] == 'Fade In':
                while True:
                    exp_value = input('Exponential Value: ').strip() or '0'

                    if exp_value == 0 or Interface.time_pattern.match(exp_value):
                        audio_filters['Fade In'] = exp_value
                        break
                    else:
                        logging.error('Invalid Time')
    
            elif answer['audio_filters'] == 'Fade Out':
                while True:
                    start_time = input('Start Time: ').strip() or '0'
                    exp_value = input('Exponential Value: ').strip() or '0'

                    if Interface.time_pattern.match(start_time) and Interface.time_pattern.match(exp_value):
                        audio_filters['Fade Out']['Start Time'] = start_time
                        audio_filters['Fade Out']['Exp'] = exp_value
                        break
                    else:
                        logging.error('Invalid Time')

            elif answer['audio_filters'] == 'Mute':
                while True:
                    start_time = input('Start Time: ').strip() or '0'
                    end_time = input('End Time: ').strip() or '0'

                    if Interface.time_pattern.match(start_time) and Interface.time_pattern.match(end_time):
                        audio_filters['Mute']['Start Time'] = start_time
                        audio_filters['Mute']['End Time'] = end_time
                        break
                    else:
                        logging.error('Invalid Time')

            elif answer['audio_filters'] == 'Custom':
                custom_audio_filter = input('Custom Audio Filter(s): ').strip()
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