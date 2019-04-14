![Build Status](https://travis-ci.org/dyntopia/ossaudit.svg?branch=master)
![Cov](https://codecov.io/github/dyntopia/ossaudit/coverage.svg?branch=master)

# ossaudit

## About

`ossaudit` uses [Sonatype OSS Index][1] to audit Python packages for
known vulnerabilities.

It can check installed packages and/or packages specified in dependency
files.  The following formats are supported with [dparse][2]:

- PIP requirement files
- Pipfile
- Pipfile.lock
- tox.ini
- conda.yml


## Installation

Clone this repository and:

```sh
make install
```

This installs `ossaudit` with `pip`.  Note that each dependency in
`requirements/*` is pinned with the hash for their respective source
tarball.  If you don't care about that you could simply:

```sh
./setup.py install
```


## Usage

```sh
$ ossaudit --help
Usage: ossaudit [OPTIONS]

Options:
  -i, --installed
  -f, --file FILENAME
  --help               Show this message and exit.
```


[1]: https://ossindex.sonatype.org/
[2]: https://github.com/pyupio/dparse
