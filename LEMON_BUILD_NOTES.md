# Linux Build Notes (stracker 3.4.1)

This document records an environment and command set that worked for building
`stracker_linux_x86.tgz` from source.

## Source Revision

- Repo: `S-P-Tracker`
- Branch: `v3.4.1`
- Commit: `aa0b82a` (`prepare release 3.4.1`)

## Build Host

- OS: Ubuntu 24.04 LTS
- Python environment manager: micromamba
- Environment name: `sp341`

## Environment That Worked

Use Python 3.6 for this legacy codebase.

```bash
~/.local/bin/micromamba remove -n sp341 --all -y || true
~/.local/bin/micromamba create -n sp341 -y python=3.6.15 pip
~/.local/bin/micromamba run -n sp341 pip install "pip<22" "setuptools<60" "wheel<0.38"
~/.local/bin/micromamba run -n sp341 pip install \
  "pyinstaller==4.10" \
  "bottle==0.12.7" \
  "cherrypy==8.1.2" \
  "python-dateutil==2.5.1" \
  "wsgi-request-logger==0.4.1" \
  "simplejson==3.8.0" \
  "psycopg2-binary<3" \
  "apsw<3.40"
```

## Build Command

```bash
~/.local/bin/micromamba run -n sp341 bash -lc "cd /path/to/S-P-Tracker && sh create_release.sh"
```

Output:

- `/path/to/S-P-Tracker/stracker/stracker_linux_x86.tgz`

## Copy Artifact To Another Machine

```bash
scp user@buildhost:/path/to/S-P-Tracker/stracker/stracker_linux_x86.tgz \
  /local/path/
```

## Repository Patches Required For Ubuntu 24.04 Build

1. `create_release.sh`
- Use `python -m PyInstaller` explicitly.
- Add robust hidden-import handling for CherryPy/Cheroot.
- Add `--paths .. --paths externals`.
- Add hidden imports for `ptracker_lib.async_worker` and `apsw`.
- `set -eu` to fail early on build errors.

2. `stracker/externals/pygal/maps/__init__.py`
- Fix invalid non-UTF8 byte in the copyright line.

3. `stracker/stracker_lib/ac_monitor.py`
- On reconnect, refresh driver identity fields (`name`, `team`, `car`) to keep
  `guids_based_on_driver_names=True` behavior consistent with `Players.Name`.

## Runtime Note

- Missing `bad_words.txt` logs an error message but is not fatal.
- To silence it, place an empty `bad_words.txt` in the runtime working
  directory.
