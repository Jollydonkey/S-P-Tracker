# Remote build settings for create_release.py
#
# Uses OpenSSH on macOS/Linux instead of PuTTY plink.
# Assumes:
# 1) You can `ssh lemon` without password prompt (SSH keys configured).
# 2) Repo is checked out on remote host at `remote_path`.

plink = "/usr/bin/ssh"
git = "/usr/bin/git"

# Path of this repo on the remote machine.
remote_path = "/home/lemon/S-P-Tracker"
host = "lemon"

# Run Linux build remotely.
REMOTE_BUILD_CMD = [
    plink,
    host,
    "~/.local/bin/micromamba run -n sp341 bash -lc 'cd " + remote_path + " && sh create_release.sh'",
]

# Copy generated Linux package back to local workspace.
REMOTE_COPY_RESULT = [
    "/usr/bin/scp",
    host + ":" + remote_path + "/stracker/stracker_linux_x86.tgz",
    "stracker/stracker_linux_x86.tgz",
]
