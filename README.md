![Build Status](https://travis-ci.org/illikainen/ossaudit.svg?branch=master)
![Cov](https://codecov.io/github/illikainen/ossaudit/coverage.svg?branch=master)

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

### Normal

```sh
pip install ossaudit
```

### Development

Clone this repository and:

```sh
make install-dev
```

This installs `ossaudit` with `pip`.  Note that each dependency in
`requirements/*` is pinned with the hash for their respective source
tarball.  If you don't care about that you could simply:

```sh
./setup.py develop
```


## Usage

```sh
$ ossaudit --help
Usage: ossaudit [OPTIONS]

Options:
  -c, --config TEXT    Configuration file.
  -i, --installed      Audit installed packages.
  -f, --file FILENAME  Audit packages in file (can be specified multiple
                       times).
  --username TEXT      Username for authentication.
  --token TEXT         Token for authentication.
  --column TEXT        Column to show (can be specified multiple times).
                       [default: name, version, title]
  --ignore-id TEXT     Ignore a vulnerability by Sonatype ID or CVE (can be
                       specified multiple times).
  --ignore-cache       Temporarily ignore existing cache.
  --reset-cache        Remove existing cache.
  --help               Show this message and exit.
```

Possible column names are:
* name (python package name)
* version (python package version)
* coordinate
* id
* cve (optional, might be emtpy)
* cvss_score
* cvss_vector
* short_title
* title
* description
* reference (url with further information on ossindex website)

## Configuration

[Appdirs][3] is used to determine storage paths.  This means that the
location of the configuration file is platform-specific:

- `*nix`: `~/.config/ossaudit/config.ini`
- `macOS`: `~/Library/Preferences/ossaudit/config.ini`
- `Windows`: `C:\Users\<username>\AppData\Local\ossaudit\ossaudit\config.ini`

It can be overridden with the `--config` command-line argument and with
the `OSSAUDIT_CONFIG` environment variable.

Example configuration:

```ini
[ossaudit]
# Optional: OSS Index username.
username = string

# Optional: OSS Index token
token = string

# Optional: comma-separated list of columns to show.
# Default: name, version, title
# Supported: id, name, version, cve, cvss_score, title, description
columns = name, version, title

# Optional: comman-separated list of vulnerability IDs (Sonatype ID or CVE) to ignore.
ignore-ids = x,y,z
```

Authentication is **not** required.  However, requests are rate limited
and authenticated requests are less restricted.  A free account can be
created on [OSS Index][1]


[1]: https://ossindex.sonatype.org/
[2]: https://github.com/pyupio/dparse
[3]: https://github.com/ActiveState/appdirs
