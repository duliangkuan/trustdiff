# feat: add median() to the stats module

We already expose `mean`, but skewed datasets need a median too. This PR
adds `median(values)` to `stats.py`: it sorts a copy of the input and
returns the middle value for odd-length inputs, or the average of the two
middle values for even-length inputs. Empty input raises `ValueError`,
consistent with `mean`.

Added tests for odd, even, and empty cases, and documented the new function
in the README.
