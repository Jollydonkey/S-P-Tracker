# S/P-Tracker 3.4.1 · 自定义维护版

基于原作者 3.4.1，为 Assetto Corsa 服务端提供圈速统计和网页展示。维护分支：**stable-3.4.1**。

- 修复玩家重连后的姓名、车队和车型同步。
- 修复 APSW 在 PB/SB、分段及最佳圈历史查询中的游标异常。
- 提供 Windows x64 单文件程序和 Linux x86_64 运行包。

## 安装与运行

下载本分支的 **Code → Download ZIP**，解压后取出 `stracker/` 部署到 AC 服务端。使用现成程序无需安装 Python，也无需运行打包脚本。

```text
stracker/
├── http_static/
├── http_templates/
├── stracker.exe                 # Windows
├── stracker.ini                 # Windows 配置，自行生成
└── stracker_linux_x86/          # Linux：解压 tgz 后得到
    ├── stracker
    ├── 运行库及子目录（全部保留）
    └── stracker.ini             # Linux 配置，自行生成
```

Windows 只需 exe 和两个 HTTP 目录；Linux 必须保留完整解压目录，并使用上一层的两个 HTTP 目录。配置、数据库及定制网页在更新时保留。

**使用 Server Manager：** 保持上面的目录结构，由管理器配置并启动 sTracker，无需再手动启动。

**独立启动：** 在部署后的 `stracker/` 目录执行对应命令。

Windows（PowerShell）：

```powershell
.\stracker.exe --stracker_ini .\stracker.ini
```

Linux：

```bash
tar -xzf stracker_linux_x86.tgz
cd stracker_linux_x86
chmod +x ./stracker
./stracker --stracker_ini ./stracker.ini
```

首次启动会生成默认 ini，并因 AC 路径尚未填写而退出。修改 ini 中的以下项目后重新启动；路径换成实际位置，Windows 也可写为 `D:/AC/server/...`。

```ini
[STRACKER_CONFIG]
ac_server_cfg_ini = /path/to/AC/server/cfg/server_cfg.ini
ac_server_working_dir = /path/to/AC/server

[HTTP_CONFIG]
enabled = True
listen_port = 50041
```

插件端口需与 AC 服务端一致。默认数据库为 `./stracker.db3`，新安装自动创建，迁移时使用原库；相对路径按**启动工作目录**解析。程序没有固定安装路径，移动时保留上述资源布局并调整 ini 中的 AC 路径。Linux 构建基于 Ubuntu 24.04 x86_64。

## 重新打包

在独立源码副本中构建，不在运行中的服务目录操作。

### Windows

使用 **Windows x64 Python 3.6.8**，在项目根目录执行：

```powershell
py -3.6 -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install pip==21.3.1 setuptools==58.0.4 wheel==0.37.1
.\.venv-win\Scripts\python.exe -m pip install -r requirements-windows-build.txt
.\.venv-win\Scripts\python.exe scripts/build_windows.py
```

输出：`artifacts/stracker.exe`。环境准备好后，再次打包只需最后一条命令；更新现有安装时只替换 exe。

也可在 **Actions → Windows build → Run workflow** 构建。产物 ZIP 只有 exe，保留 30 天，不自动写回仓库或发布 Release；全新安装仍需两个 HTTP 目录。若云端产物有问题，可在 Windows 本机重新打包。

### Linux

使用独立的 Python 3.6.15 环境。以下以已安装的 micromamba 为例，在项目根目录执行：

```bash
micromamba create -n sp341-build -y python=3.6.15 pip
micromamba run -n sp341-build pip install "pip<22" "setuptools<60" "wheel<0.38"
micromamba run -n sp341-build pip install \
  pyinstaller==4.10 bottle==0.12.7 cherrypy==8.1.2 python-dateutil==2.5.1 \
  wsgi-request-logger==0.4.1 simplejson==3.8.0 psycopg2-binary==2.9.5 apsw==3.39.4.0
micromamba run -n sp341-build sh create_release.sh
```

输出：`stracker/stracker_linux_x86.tgz`。环境准备好后，再次打包只需最后一条命令。脚本会清理源码副本中的旧 tgz 和临时构建目录；部署时整体更新程序及配套运行库，保留配置、数据库和网页资源。

### 脚本区别

- `create_release.sh`：当前 Linux 打包入口，仍然可用。
- `scripts/build_windows.py`：当前 Windows sTracker 打包入口。
- `create_release.py`：原作者的完整发布工具，需要本地 `remote_settings.py` 和对应工具链，默认还涉及 pTracker、NSIS 与远程 Linux 构建。保留供参考，未适配当前整套发布环境；配置模板为 `remote_settings.py.in`。

## 构建来源与许可

当前 Windows exe 来自 [GitHub Actions](https://github.com/Jollydonkey/S-P-Tracker/actions/runs/41798929154)，构建于 2026-11-04，源码为历史整理前的 `cb5c6cb5811da76f3440d12449d61af227f72e95`（Python 3.6.8、PyInstaller 4.10、APSW 3.39.4.0）。Linux 包保留已有的自定义构建。

EXE SHA256：`893b9e1c00452168e3e62647b8b065342c93305302304d75df4aa41de7e8b165`

原作者说明见 [README.txt](README.txt)，许可证见 [LICENSE.txt](LICENSE.txt)。完整修改历史见 Git 提交记录。
