"""Validate the EXTRACTED Windows artifact with disposable files only."""
import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='stracker-package-check-') as tmp:
        root = Path(tmp)
        with zipfile.ZipFile(str(args.archive.resolve())) as z:
            z.extractall(str(root))
        package = root / 'stracker'
        exe = package / 'stracker.exe'
        for path in [exe, package / 'http_templates' / 'tmpl_mainpage.py',
                     package / 'http_static' / 'bootstrap' / 'css' / 'custom.css']:
            if not path.is_file():
                raise RuntimeError('Package resource missing: ' + str(path))
        help_result = subprocess.run([str(exe), '--help'], cwd=str(package),
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     universal_newlines=True, timeout=60)
        print(help_result.stdout)
        if help_result.returncode or '3.4.1' not in help_result.stdout:
            raise RuntimeError('Frozen executable --help failed')
        cfg = root / 'server_cfg.ini'
        cfg.write_text('[SERVER]\nUDP_PORT=19600\nTCP_PORT=19600\n', encoding='utf-8')
        database = root / 'synthetic.db3'
        backup = root / 'synthetic-backup.db3'
        ini = root / 'stracker.ini'
        ini.write_text('[STRACKER_CONFIG]\nac_server_cfg_ini={cfg}\n'
                       'log_file={log}\nlower_priority=False\ntee_to_stdout=True\n'
                       '[DATABASE]\ndatabase_file={db}\nperform_backups=False\n'
                       '[HTTP_CONFIG]\nenabled=False\n'.format(
                           cfg=cfg.as_posix(), log=(root / 'stracker.log').as_posix(), db=database.as_posix()), encoding='utf-8')
        result = subprocess.run([str(exe), '--stracker_ini', str(ini), '--perform_backup', str(backup)],
                                cwd=str(package), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                universal_newlines=True, timeout=120)
        print(result.stdout)
        if result.returncode:
            raise RuntimeError('Frozen database initialization/backup failed')
        for db in (database, backup):
            if not db.is_file():
                raise RuntimeError('Database was not created: ' + str(db))
            with sqlite3.connect(str(db)) as conn:
                if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise RuntimeError('Database integrity check failed')
                if conn.execute('PRAGMA user_version').fetchone()[0] <= 0:
                    raise RuntimeError('Database schema was not initialized')
        print(json.dumps({'frozen_help': 'passed', 'bundled_resources': 'passed',
                          'synthetic_database_and_backup': 'passed',
                          'real_ac_server_or_player_test': 'not performed'}, indent=2))


if __name__ == '__main__':
    main()
