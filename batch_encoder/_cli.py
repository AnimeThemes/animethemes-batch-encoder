from ._audio_filter import AudioFilter
from ._bitrate_mode import BitrateMode
from ._typing import Args, EncodingConfigType
from ._video_filter import VideoFilter
from typing import Literal

import inquirer
import logging
import re
import sys


# Use the inquirer lib to create a CLI
class CLI:
    # Time Duration Specification: https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax
    time_pattern = re.compile(r"^([0-5]?\d:){1,2}[0-5]?\d(?=\.\d+$|$)|\d+(?=\.\d+$|$)")

    # Validations
    validate_time = lambda _, x: all(CLI.time_pattern.match(y) for y in x.split(","))
    validate_encoding_modes = lambda _, x: all(
        y.strip().upper()
        in [BitrateMode.VBR.name, BitrateMode.CBR.name, BitrateMode.CQ.name]
        for y in x.split(",")
    )
    validate_digits = (
        lambda _, x: all(y.strip().isdigit() for y in x.split(","))
        or len(x.strip()) == 0
    )

    # Prompt the user for text questions
    def prompt_text(message, validate=lambda _, x: x) -> str:
        answer = inquirer.prompt(
            [inquirer.Text("text", message=message, validate=validate)]
        )

        if answer is None:
            return "NoName"

        logging.debug(f"[CLI.prompt_text] answer[\"text\"]: '{answer['text']}'")

        return answer["text"]

    # Prompt the user for time questions
    def prompt_time(message, validate=validate_time) -> str:
        answer = inquirer.prompt(
            [inquirer.Text("time", message=message, validate=validate)]
        )

        if answer is None:
            return ""

        logging.debug(f"[CLI.prompt_time] answer[\"time\"]: '{answer['time']}'")

        return answer["time"]

    # Prompt the user for our mode options to run to the user
    def choose_mode(args: Args) -> Literal[1, 2, 3]:
        modes = [
            ("Generate commands", 1),
            ("Execute commands", 2),
            ("Generate and execute commands", 3),
        ]

        if args.generate and args.execute:
            return 3
        elif args.generate:
            return 1
        elif args.execute:
            return 2
        else:
            answer = inquirer.prompt(
                [inquirer.List("mode", message="Mode (Enter)", choices=modes)]
            )

            if answer is None:
                sys.exit()

            logging.debug(f"[CLI.choose_mode] answer[\"mode\"]: '{answer['mode']}'")

            return answer["mode"]

    # Prompt the user for source files to choose
    def choose_source_files(source_files) -> list[str]:
        answer = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "source_files",
                    message="Source Files (Space to select)",
                    choices=source_files,
                )
            ]
        )

        if answer is None:
            sys.exit()

        if len(answer["source_files"]) == 0:
            logging.error("Select at least one file")
            sys.exit()

        logging.debug(
            f"[CLI.choose_source_files] answer[\"source_files\"]: '{answer['source_files']}'"
        )

        return answer["source_files"]

    # Prompt the user for audio filters options
    def audio_filters_options(output_name) -> str:
        af = AudioFilter.get_obj()
        fadein, fadeout, mute, custom = (
            AudioFilter.FADE_IN._value_[0],
            AudioFilter.FADE_OUT._value_[0],
            AudioFilter.MUTE._value_[0],
            AudioFilter.CUSTOM._value_[0],
        )

        while not af["Exit"]:
            print(f"\n\033[92mOutput Name: {output_name}\033[0m")
            answer = inquirer.prompt(
                [
                    inquirer.List(
                        "af", message="Audio Filters (Enter)", choices=list(af.keys())
                    )
                ]
            )

            if answer is None:
                af["Exit"] = True

            elif answer["af"] == fadein:
                af[fadein] = CLI.prompt_time("Exponential Value").strip() or "0"

            elif answer["af"] == fadeout:
                af[fadeout]["Start Time"] = CLI.prompt_time("Start Time").strip() or "0"
                af[fadeout]["Exp"] = CLI.prompt_time("Exponential Value").strip() or "0"

            elif answer["af"] == mute:
                af[mute]["Start Time"] = CLI.prompt_time("Start Time").strip() or "0"
                af[mute]["End Time"] = CLI.prompt_time("End Time").strip() or "0"

            elif answer["af"] == custom:
                custom_audio_filter = CLI.prompt_text("Custom Audio Filter(s)").strip()
                af[custom] = custom_audio_filter

            else:
                af["Exit"] = True

        af_list = []

        if float(af[fadein]) > 0:
            af_list.append(AudioFilter.FADE_IN.toText(af[fadein]))
        if float(af[fadeout]["Exp"]) > 0:
            af_list.append(
                AudioFilter.FADE_OUT.toText(
                    af[fadeout]["Start Time"], af[fadeout]["Exp"]
                )
            )
        if float(af[mute]["Start Time"]) > 0 or float(af[mute]["End Time"]) > 0:
            af_list.append(
                AudioFilter.MUTE.toText(af[mute]["Start Time"], af[mute]["End Time"])
            )
        if len(af[custom]) > 0:
            af_list.append(AudioFilter.CUSTOM.toText(af[custom]))

        logging.debug(
            f"[CLI.af_options] "
            f"af[{fadein}]: '{af[fadein]}', "
            f"af[{fadeout}][\"Start Time\"]: '{af[fadeout]['Start Time']}', "
            f"af[{fadeout}][\"Exp\"]: '{af[fadeout]['Exp']}', "
            f"af[{mute}][\"Start Time\"]: '{af[mute]['Start Time']}', "
            f"af[{mute}][\"End Time\"]: '{af[mute]['End Time']}', "
            f"af[{custom}]: '{af[custom]}'"
        )

        return ",".join(af_list)

    # Prompt the user for our list of video filters
    def video_filters(encoding_config: EncodingConfigType) -> EncodingConfigType:
        video_filters_options = VideoFilter.get_obj()

        if encoding_config.include_unfiltered:
            encoding_config.video_filters.append((None, "No Filters"))

        answer = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "video_filters",
                    message="Select Video Filters (Space to select)",
                    choices=video_filters_options.keys(),
                    default=[tp[1] for tp in encoding_config.video_filters],
                )
            ]
        )

        if answer is None:
            return encoding_config

        tp_list = [
            (name, filter_string)
            for filter_string, name in video_filters_options.items()
            if filter_string in answer["video_filters"]
        ]
        custom = VideoFilter.CUSTOM

        if VideoFilter.CUSTOM._value_[1] in answer["video_filters"]:
            tp_list.remove((custom._value_[0], custom._value_[1]))
            custom_video_filters = CLI.prompt_text(
                'Custom Video Filters (Separate with ",," if more than one)'
            ).split(",,")
            tp_list.extend(
                [
                    (f"{custom._value_[0]}{i + 1}", value)
                    for i, value in enumerate(custom_video_filters)
                ]
            )

        encoding_config.video_filters = tp_list

        logging.debug(f"[CLI.video_filters] tp_list: '{tp_list}'")

        return encoding_config

    # Prompt the user for custom options if requested
    def custom_options(encoding_config: EncodingConfigType) -> EncodingConfigType:
        create_preview = encoding_config.create_preview
        limit_size_enable = encoding_config.limit_size_enable
        encoding_modes = encoding_config.encoding_modes
        crfs = encoding_config.crfs
        cbr_bitrates = encoding_config.cbr_bitrates
        cbr_max_bitrates = encoding_config.cbr_max_bitrates

        answer = inquirer.prompt(
            [
                inquirer.Confirm(
                    "create_preview", message="Create Preview?", default=create_preview
                ),
                inquirer.Confirm(
                    "limit_size_enable",
                    message="Limit Size Enable?",
                    default=limit_size_enable,
                ),
                inquirer.Text(
                    "encoding_modes",
                    message="Encoding Modes",
                    default=",".join(encoding_modes),
                    validate=CLI.validate_encoding_modes,
                ),
            ]
        )

        if answer is None:
            return encoding_config

        encoding_mode_questions = []
        for encoding_mode in answer["encoding_modes"].split(","):
            if (
                encoding_mode == BitrateMode.VBR.name
                or encoding_mode == BitrateMode.CQ.name
            ):
                encoding_mode_questions.append(
                    inquirer.Text(
                        "crfs",
                        message="CRFs",
                        default=",".join(crfs),
                        validate=CLI.validate_digits,
                    )
                )
            if encoding_mode == BitrateMode.CBR.name:
                encoding_mode_questions.append(
                    inquirer.Text(
                        "cbr_bitrates",
                        message="Bit Rates",
                        default=",".join(cbr_bitrates),
                        validate=CLI.validate_digits,
                    )
                )
                encoding_mode_questions.append(
                    inquirer.Text(
                        "cbr_max_bitrates",
                        message="Max Bit Rates",
                        default=",".join(cbr_max_bitrates),
                        validate=CLI.validate_digits,
                    )
                )

        answer_em = inquirer.prompt(encoding_mode_questions)

        encoding_config.create_preview = answer["create_preview"]
        encoding_config.limit_size_enable = answer["limit_size_enable"]
        encoding_config.encoding_modes = answer["encoding_modes"].split(",")

        if "crfs" in answer_em:
            encoding_config.crfs = answer_em["crfs"].split(",")
        if "cbr_bitrates" in answer_em and "cbr_max_bitrates" in answer_em:
            encoding_config.cbr_bitrates = (
                [x + "k" for x in answer_em["cbr_bitrates"].split(",")]
                if len(answer_em["cbr_bitrates"].strip()) != 0
                else None
            )
            encoding_config.cbr_max_bitrates = (
                [x + "k" for x in answer_em["cbr_max_bitrates"].split(",")]
                if len(answer_em["cbr_max_bitrates"].strip()) != 0
                else None
            )

        logging.debug(
            f"[CLI.custom_options] "
            f"encoding_config.create_preview: '{encoding_config.create_preview}', "
            f"encoding_config.limit_size_enable: '{encoding_config.create_preview}', "
            f"encoding_config.encoding_modes: '{encoding_config.encoding_modes}', "
            f"encoding_config.crfs: '{encoding_config.crfs}', "
            f"encoding_config.cbr_bitrates: '{encoding_config.cbr_bitrates}', "
            f"encoding_config.cbr_max_bitrates: '{encoding_config.cbr_max_bitrates}'"
        )

        return encoding_config
