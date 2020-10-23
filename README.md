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

* `--mode 1`: Generates commands from input files in the current directory. User will be prompted for inclusion/exclusion of input file, start time, end time and output file name.
* `--mode 2`: Execute commands from file line-by-line in the current directory.
* `--mode 3`: Generate commands from input files in the current directory in the same manner as Mode 1 and then execute commands without writing to file.
* `[FILE]`: The file that commands are written to or read from. Default: commands.txt in the current directory. Unused in `--mode 3`.
* `[CONFIGFILE]`: The configuration file in which our properties are defined. Default: batch_encoder.ini written to the same directory as the batch_encoder.py script.
* `AllowedFileTypes`: Configuration property for file extensions that will be considered source file candidates
* `EncodingModes`: Configuration property for the inclusion and order of encoding modes `{CBR, VBR, CQ}`
* `CRFs`: Configuration property for the ordered list of CRF values to use with VBR and/or CQ encoding modes
* `IncludeUnfiltered`: Configuration property that sets the flag for including/excluding an encode without video filters for each EncodingMode
* `VideoFilters`: Configuration items used for named video filtergraphs
* `--loglevel error`: Only show error messages
* `--loglevel info`: Show error messages and script progression info messages
* `--loglevel debug`: Show all messages, including variable dumps