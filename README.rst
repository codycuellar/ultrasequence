ULTRASEQUENCE
=============

-  Author: Cody Cuellar
-  URL: https://github.com/codycuellar/ultrasequence

An ultra-fast Python file sequencing tool with useful custom features.
This package is exponentially faster than many of the similar packages.

In most cases, with standard naming conventions where the frame number
is the last set of digits in the filename, this tool will be able to
build the sequences with roughly O(n) speeds. Other similar tools are
generally O(n²) or slower.

License
=======

This project is licensed under the terms of the `MIT
license. <https://choosealicense.com/licenses/mit/>`__

Features
========

-  Compatible with the latest versions of Python 2 and 3.
-  Ultra-fast O(n) sequencing. Can handle hundreds of thousands of input
   files in a matter of seconds.
-  Custom include and exclude extensions so only the file extensions you
   want will be sequenced, otherwise they will immediately move into a
   skipped list.
-  Get file stats on the fly, or supply them in an ordered tuple,
   dictionary, or pass an os.stat_result object directly for each file.
-  Force file naming with different digit padding levels to be treated
   as different sequences, or allow inconsistent padding.
-  Custom string formatting of the sequenced file names.
-  Highly customizable - you can even supply your own regex pattern to
   the sequencer to change how and where it finds the frame number.

Platforms
=========

The following Platforms are tested: \* OSX 10.10, 10.11, 10.12, 10.13

It should run on all recent versions of OSX, and Linux platforms, but
further testing is needed.

Usage
=====

To use UltraSequence in python is very easy. Simply import the
ultrasequence module and then use the Parser object to set up the
options. Then you simply call one of the parser methods of the Parser
class depending on the type of item you are parsing (directoy, file, or
python list).

```python
    >>> import ultrasequence as us
    >>> parser = us.Parser()
    >>> parser.parse_directory('~/Documents', recurse=True)
    >>> print(parser)
    'Parser(sequences=15, single_frames=75, non_sequences=810, excluded=0,
    collisions=0)'
```

These lists can be accessed as normal lists such as:

```python
    >>> for frame in parser.sequences[0]:
    ...     print(frame)
        
    >>> for sequence in parser.sequences:
    ...     print('Sequence %s is missing %s frames' % (
    ...           sequence.format('%h%P%T'), sequence.missing_frames))
```

Command-Line Utility
--------------------

To use the command-line utility, run the findseq command after
installing ultrasequence:

```bash
    $ findseq /path/to/directory -R --include dpx exr png
```

All command line options can be overridden by installing the local
config file to `~/ultrasequence.conf` and updating it with your settings of
choice:

```bash
    $ findseq -M
```

This file will always be used as default for both python and
command-line usage, which can make some command line options impossible
to enable or disable. If using a local config file, you can temporarily
disable it by using the `-I` flag. All command line flags are then
reset to default and can be overridden by using the flags to change the
default behavior.

When using the python code directly, you can pass args into the Parser()
init and the parse_* methods to override this file on the fly.

Configuration
-------------

By default, all the options are pre-defined in the
`ultrasequence.config.UsConfig` class. A CONFIG variable in the
`ultrasequence.config` is pre-instantiated with the defaults. If
`CONFIG.make_local_config` is called, a local configuration file will be
generated with the defaults at `~/.ultrasequence.conf`. You can then modify
this file as you wish and every time the program is run either in Python or
from the command-line utility, the values from this config file will be used
instead. All option can still be overridden with arguments on the
command-line, or by passing new values into the Parser, Sequence, and File
method parameters.

The configuration attributes are:

[global]
++++++++
format = %H%r%T
    A string formatter to use for representing the built sequences. For
    more information on how to use the formatter, refer to the docs on
    `~ultrasequence.models.Sequence.format`
recurse = True
    Whether or not to recurse into child directories when scanning folders
    on the local system.
ignore_padding = True
    Enable or disable strict padding rules. If enabled, each file's sequence
    key is generated with the padding, so file.0001.dpx key would be
    file.%04d.dpx. If disabled, the key would be file.#.dpx, but this can cause
    collisions in some rare cases.
include_exts = exr dpx jpg
    A list of inclusion file extensions. Any files with extensions not in this
    list will be skipped and not sequenced.
exclude_exts = mov pdf xls
    A list of exclusion file extensions. Any files with extensions in this
    list will be skipped and not sequenced.
get_stats = True
    Do a os.stat() on every file found.

[regex]
+++++++
frame_extract = `((.*)(\D))?(\d+)(.*)`
    The regex pattern to extract the frame numbers. This can be modified for
    special cases such as when the frame number isn't the last digit before the
    extension.
head_group = 0
    The regex capture group for all characters preceding the frame digits.
frame_group = 3
    The regex capture group for the frame digits.
tail_group = 4
    The regex capture group for all characters after the digits.
