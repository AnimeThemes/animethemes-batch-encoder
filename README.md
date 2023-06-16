### Description

Generate and execute collection of FFmpeg commands sequentially from external file to produce WebMs that meet [AnimeThemes.moe](https://animethemes.moe/) encoding standards.

Take advantage of sleep, work, or any other time that we cannot actively monitor the encoding process to produce a set of encodes for later quality checking and/or tweaking for additional encodes.

Ideally we are iterating over a combination of filters and settings, picking the best one at the end.

### Install

**Requirements:**

* FFmpeg
* Python >= 3.6

**Install:**

    pip install animethemes-batch-encoder

### Usage

        python -m batch_encoder [-h] --mode [{1,2,3}] [--file [FILE]] [--configfile [CONFIGFILE]] --loglevel [{debug,info,error}]

**Mode**

`--mode 1` generates commands from input files in the current directory.

The user will be prompted for values that are not determined programmatically, such as inclusion/exclusion of a source file candidate, start time, end time, output file name and new audio filters.

`--mode 2` executes commands from file in the current directory line-by-line.

By default, the program looks for a file named `commands.txt` in the current directory. This file name can be specified by the `--file` argument.

`--mode 3` generates commands from input files in the current directory and executes the commands sequentially.

**File**

The file that commands are written to or read from.

By default, the program will write to or read from `commands.txt` in the current directory.

**Config File**

The configuration file in which our encoding properties are defined.

By default, the program will write to or read from `batch_encoder.ini` in the user config directory of appname `batch_encoder` and author `AnimeThemes`.

Example: `C:\Users\Kyrch\AppData\Local\AnimeThemes\batch_encoder\batch_encoder.ini`

**Encoding Properties**

`AllowedFileTypes` is a comma-separated listing of file extensions that will be considered for source file candidates.

`EncodingModes` is a comma-separated listing of [bitrate control modes](https://developers.google.com/media/vp9/bitrate-modes) for inclusion and ordering of commands.

Available bitrate control modes are:

* `CBR` Constant Bitrate Mode
* `VBR` Variable Bitrate Mode
* `CQ` Constrained Quality Mode

`CRFs` is a comma-separated listing of ordered CRF values to use with `VBR` and/or `CQ` bitrate control modes.

`Threads` is the number of threads used to encode. Default is 4.

`LimitSizeEnable` is a flag for including the `-fs` argument to terminate an encode when it exceeds the allowed size. Default is True.

`AlternateSourceEnable` is a flag for alternate command lines between source files. Default is False.

`IncludeUnfiltered` is a flag for including or excluding an encode without video filters for each bitrate control mode and CRF pairing. Default is True.

`VideoFilters` is a configuration item list used for named video filtergraphs for each bitrate control mode and CRF pairing.

**Logging**

Determines the level of the logging for the program.

`--loglevel error` will only output error messages.

`--loglevel info` will output error messages and script progression info messages.

`--loglevel debug` will output all messages, including variable dumps.
