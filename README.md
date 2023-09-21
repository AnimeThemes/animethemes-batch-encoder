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

        python -m batch_encoder [-h] [--generate | -g] [--execute | -e] [--custom | -c] [--file [FILE]] [--configfile [CONFIGFILE]] --loglevel [{debug,info,error}]

**Mode**

`--generate` generates commands from input files in the current directory.

The user will be prompted for values that are not determined programmatically, such as inclusion/exclusion of a source file candidate, start time, end time, output file name and new audio filters.

`--execute` executes commands from file in the current directory line-by-line.

By default, the program looks for a file named `commands.txt` in the current directory. This file name can be specified by the `--file` argument.

`--generate` and `--execute` generates commands from input files in the current directory and executes the commands sequentially.

`None` will give modes options to run.

**Custom**

`--custom` customizes options like Create Preview, Limit Size Enable, CRFs and Encoding Modes for each output file. Default configs are specified in the `--file` argument.

**File**

The file that commands are written to or read from.

By default, the program will write to or read from `commands.txt` in the current directory.

**Config File**

The configuration file in which our encoding properties are defined.

By default, the program will write to or read from `batch_encoder.ini` in the user config directory of appname `batch_encoder` and author `AnimeThemes`.

Example: `C:\Users\Kyrch\AppData\Local\AnimeThemes\batch_encoder\batch_encoder.ini`

**Input File**

`--inputfile` will give the option to insert input files in advance, separated by two commas. Example: `python -m batch_encoder -g --inputfile 'source file.mkv,,source file 2.mkv'`.

**Audio Filters**

* `Exit` Saves audio filters if selected and continues script execution.
* `Custom` Apply a custom audio filter string.
* `Fade In` Select an exponential value to apply Fade In.
* `Fade Out` Select a start position and an exponential value to Fade Out.
* `Mute` Select a start and end position to leave the volume at 0.

**Video Filters**

* `No Filters` Add a line without filter
* `scale=-1:720` Add downscale to 720p
* `scale=-1:720,hqdn3d=0:0:3:3,gradfun,unsharp` Add downscale to 720p and filters by AnimeThemes
* `hqdn3d=0:0:3:3,gradfun,unsharp` Add filters by AnimeThemes
* `hqdn3d=0:0:3:3` Add lightdenoise filter
* `hqdn3d=1.5:1.5:6:6` Add heavydenoise filter
* `unsharp` Add unsharp filter
* `Custom` Apply a custom video filter string.

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

`CreatePreview` is a flag for create a command line to preview seeks. Default is False.

`IncludeUnfiltered` is a flag for including or excluding an encode without video filters for each bitrate control mode and CRF pairing. Default is True.

`VideoFilters` is a configuration item list used for named video filtergraphs for each bitrate control mode and CRF pairing.

**Logging**

Determines the level of the logging for the program.

`--loglevel error` will only output error messages.

`--loglevel info` will output error messages and script progression info messages.

`--loglevel debug` will output all messages, including variable dumps.
