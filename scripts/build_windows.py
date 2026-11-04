"""Build the custom sTracker server on Windows without touching a live install."""
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


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
    artifacts = ROOT / 'artifacts'
    artifacts.mkdir(exist_ok=True)
    executable = artifacts / 'stracker.exe'
    shutil.copy2(str(build / 'dist' / 'stracker.exe'), str(executable))
    print('Built', executable)



if __name__ == '__main__':
    main()
