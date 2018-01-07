# -*- coding: utf-8 -*-
"""
--------------------------------------------------
**  An ultra-fast file sequencing tool.  **

© 2017 Cody Cuellar
cody.cuellar@gmail.com

License: MIT

--------------------------------------------------

This tool was built with speed in mind. It is very easy to use, 
highly customizable, and has many neat features to help with file
management.

*** ALL LINKS ARE IGNORED AS IF THEY DO NOT EXIST ***

The core function is sequencing files with matching basenames and
incremental 'frame' digits, which is very useful in film and VFX
workflows. This tool
makes it easy to sort them out and group them together and make it
easy to list seqeunces as single entries in a text manifest.


These files:
	/some/file.1000.dpx
	/some/file.1001.dpx
	/some/file.1002.dpx
	/some/file.1003.dpx
	/some/file.1004.dpx

Become:
	/some/file.[1000-1004].dpx

or by using the format method of the Sequence class such as:

>> seq.format('%r %h%P%T Missing Frames: %m')
'[1000-1004] file.%04d.dpx Missing Frames: 0'


On top of providing simple formatting, it can parse directories, a
text file containing a list of file names, or even just a python list
of file path strings. It can be used both online or offline (whether
or not you have direct access to the file paths) and can fetch all os
stats from the file system if you do have access to the files.

This module provides direct access to the File, Sequence, and Stat
models, as well as the Parser class and the cfg object.
"""

from .version import __version__
from .models import File, Sequence, Stat
from .parsing import Parser
from .config import cfg

__all__ = [File, Sequence, Stat, Parser, cfg]
