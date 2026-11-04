"""Build the custom sTracker server on Windows without touching a live install."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    if sys.platform != 'win32':
        raise SystemExit('Run with Windows Python. Linux builds are not Windows executables.')
    if sys.version_info[:2] != (3, 6) or platform.architecture()[0] != '64bit':
        raise SystemExit('This build is pinned to 64-bit Python 3.6.')
    build = ROOT / 'build' / 'windows'
    # Cleanup is restricted to this repository's generated output.
    if build.exists():
        shutil.rmtree(str(build))
    build.mkdir(parents=True)
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
            '--onefile', '--console', '--noupx', '--name', 'stracker',
            '--distpath', str(build / 'dist'), '--workpath', str(build / 'work'),
            '--specpath', str(build / 'spec'),
            '--paths', str(ROOT), '--paths', str(ROOT / 'stracker' / 'externals'),
            '--additional-hooks-dir', str(ROOT / 'stracker' / 'pyinstaller-hooks'),
            '--exclude-module', 'http_templates']
    for module in ['apsw', 'psycopg2', 'ptracker_lib.async_worker',
                   'cherrypy.wsgiserver', 'win32api', 'win32process', 'win32con']:
        args += ['--hidden-import', module]
    args.append(str(ROOT / 'stracker' / 'stracker.py'))
    subprocess.check_call(args, cwd=str(ROOT / 'stracker'))
    package = build / 'package' / 'stracker'
    package.mkdir(parents=True)
    shutil.copy2(str(build / 'dist' / 'stracker.exe'), str(package / 'stracker.exe'))
    for folder in ['http_templates', 'http_static']:
        shutil.copytree(str(ROOT / 'stracker' / folder), str(package / folder),
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copy2(str(ROOT / 'LICENSE.txt'), str(package / 'LICENSE.txt'))
    (package / 'README_WINDOWS.txt').write_text(
        'Custom sTracker 3.4.1 for Windows x64\n\n'
        'This is a single-file executable with Python and native modules embedded.\n'
        'For an existing install, replace stracker.exe only; keep its configuration, database and web resources.\n'
        'For a fresh install, copy this folder including http_templates and http_static.\n'
        'Use a COPY of your configuration and database for initial testing.\n'
        'Server Manager expects server/stracker/stracker.exe and writes stracker.ini.\n'
        'A standalone launch needs --stracker_ini PATH.\n'
        'This Actions artifact is a test build, not a GitHub Release.\n'
        'CI does not certify real multiplayer operation on Windows 11.\n', encoding='utf-8')
    commit = os.environ.get('GITHUB_SHA') or subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=str(ROOT), universal_newlines=True).strip()
    metadata = dict(source_commit=commit, packaging='onefile', python=sys.version, platform=platform.platform(),
                    build_command=args, exe_sha256=sha256(package / 'stracker.exe'),
                    tests='See Actions validation logs; no production database used')
    (package / 'BUILD_METADATA.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    artifacts = ROOT / 'artifacts'
    artifacts.mkdir(exist_ok=True)
    shutil.copy2(str(package / 'stracker.exe'), str(artifacts / 'stracker.exe'))
    zip_path = Path(shutil.make_archive(str(artifacts / 'stracker-3.4.1-windows-x64'),
                                       'zip', root_dir=str(package.parent), base_dir='stracker'))
    (artifacts / 'SHA256SUMS.txt').write_text(
        sha256(zip_path) + '  ' + zip_path.name + '\n' +
        sha256(artifacts / 'stracker.exe') + '  stracker.exe\n', encoding='utf-8')
    print('Built', zip_path)


if __name__ == '__main__':
    main()
