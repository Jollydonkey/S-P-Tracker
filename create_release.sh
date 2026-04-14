
set -eu

echo Setting environment
export PYTHONPATH=$PWD:$PWD/stracker/externals

echo Cleaning up old version
cd stracker
rm -f stracker_linux_x86.tgz
rm -rf dist
rm -rf build

HIDDEN_MOD="$(python - <<'PY'
import importlib.util
for name in ("cherrypy.wsgiserver.wsgiserver3", "cheroot.wsgi"):
    if importlib.util.find_spec(name) is not None:
        print(name)
        break
PY
)" || HIDDEN_MOD=""

if [ -n "$HIDDEN_MOD" ]; then
  echo "Using hidden import: $HIDDEN_MOD"
  python -m PyInstaller --clean -y -s --exclude-module http_templates --hidden-import "$HIDDEN_MOD" --hidden-import psycopg2 --hidden-import apsw --hidden-import ptracker_lib.async_worker --additional-hooks-dir="$PWD/pyinstaller-hooks/" --paths .. --paths externals stracker.py
else
  echo "Warning: no cherrypy/cheroot hidden import detected; building without that hidden import."
  python -m PyInstaller --clean -y -s --exclude-module http_templates --hidden-import psycopg2 --hidden-import apsw --hidden-import ptracker_lib.async_worker --additional-hooks-dir="$PWD/pyinstaller-hooks/" --paths .. --paths externals stracker.py
fi

mv dist/stracker dist/stracker_linux_x86
tar cvzf stracker_linux_x86.tgz -C dist stracker_linux_x86
rm -rf dist
rm -rf build

exit 0
