ULTRASEQUENCE
-------------
Author: Cody Cuellar

An ultra-fast Python file sequencing tool with useful custom features. This
package is exponentially faster than many of the similar packages.

Since it is impossible to guess every file naming case, this tool makes two
assumptions:

1) The last set of digits in the filename before the extension is the 
potential frame number for matching.
2) Matching sequences cannot be in different paths.

In most cases, with standard naming conventions, these two assumptions will be
very accurate at proprerly sorting the sequences with roughly O(n) speeds.
Other similar tools are generally O(n²) or worse due to the nested iterations.

## License
This project is licensed under the terms of the 
[MIT license.](https://choosealicense.com/licenses/mit/)
 
## Features
* Compatible with the latest versions of Python 2 and 3.
* Ultra-fast O(n) sequencing. Can handle hundreds of thousands of input files 
in a matter of seconds.
* Custom include extensions so only the file extensions you want will be
sequenced, otherwise they will immediately move into a skipped list.
* Get file stats on the fly, or supply them in an ordered tuple, dictionary,
or pass an os.stat_result object directly.
* Force file naming with different padding levels to be treated as different
sequences.
* Custom string formatting of the sequenced file names.

## Usage
One easy way to use this tool is to make a text file with absolute paths to
each file. This can be done with a simple Unix find command, or Python's
os.walk. Or you can simply make a list of strings and pass it into the
make_sequences() function.

```python
import ultrasequence as us

file_list = [
    '/path/to/file.01.ext',
    '/path/to/file.02.ext',
    '/path/to/file.03.ext',
    ]

sequences, non_sequences, skipped, collisions = us.make_sequences(file_list)
```

**sequences** returns a list of ultrasequence.Sequence objects, while the
latter three results return lists of ultrasequence.File objects.