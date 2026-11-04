# Custom sTracker 3.4.1

This fork maintains the custom 3.4.1 fixes on **stable-3.4.1**. The upstream
project's README and GPL license remain in `README.txt` and `LICENSE.txt`.

The custom changes preserve driver identity on reconnect and fix incomplete
APSW query results when querying personal/server best laps, sectors, and history.

## Windows test builds

The **Windows build and validation** Actions workflow builds the server-side
`stracker.exe` on Windows x64. It uses Python 3.6.8, PyInstaller 4.10, and APSW
3.39.4.0, with dependencies pinned in `requirements-windows-build.txt`.

Each successful run provides an **Actions artifact**, containing a ZIP package,
SHA256 checksum, and installed package versions. This is a validation build;
the workflow does **not** create a tag or publish a GitHub Release.

The workflow checks:

- Driver name/team/car synchronization after reconnect.
- Repeated PB/SB and sector queries through the actual APSW backend.
- Best-lap queries with, without, and missing history.
- The extracted frozen executable, external web resources, creation of a
  synthetic SQLite database, and a backup round trip.

It does not validate an actual Windows 11 AC multiplayer session, public port
forwarding, or a production database. Those remain deployment acceptance checks.

Copy the **entire** extracted `stracker/` directory to a test server, then use
copies of your configuration and database. Server Manager expects
`server/stracker/stracker.exe`. Linux binaries and Python `.so` files cannot be
used as Windows dependencies.

For a local Windows build in a separate checkout/environment:

```powershell
python -m pip install pip==21.3.1 setuptools==58.0.4 wheel==0.37.1
python -m pip install -r requirements-windows-build.txt
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build_windows.py
python scripts/verify_windows_package.py artifacts/stracker-3.4.1-windows-x64.zip
```

## Linux and development

Existing Linux deployments are not modified by the Actions workflow. Legacy
Linux build notes are in `LEMON_BUILD_NOTES.md`; the upstream base is `aa0b82a`,
and custom revisions are recorded in this branch's Git history.

Keep local release settings, databases, logs, Python caches and build output out
of new commits. Use `remote_settings.py.in` as a configuration template when
needed by the original upstream release script. Preserve the source history;
this branch does not reset or replace upstream commits.
