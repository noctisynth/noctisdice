@echo off

echo [*] 检查 Python 环境中...
:check_python
python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] Python 已正确安装。
) else (
    goto :install_python
)
python -m pip -V > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] pip 已正确安装。
) else (
    echo [!] 未找到 pip 环境，重新下载安装 Python。
    goto :install_python
)
:check_pipx
pipx --version > nul 2>&1
pipx ensurepath > nul 2>&1
for /f "delims=" %%a in ('python -c "import os; print(os.environ['PATH'])"') do (
    set "PATH=%%a"
)
if %errorlevel% equ 0 (
    echo [+] pipx 已正确安装。
    goto :setup_env
) else (
    goto :install_pipx
)


:install_python
echo [*] 正在下载 Python 安装程序...
curl https://cdn.npmmirror.com/binaries/python/3.12.2/python-3.12.2-amd64.exe -o python_installer.exe

echo [*] 安装 Python...
echo [!] 注意: 请务必勾选 Add Python 3.12 to PATH
start /wait python_installer.exe

del /q python_installer.exe
echo [+] Python 安装完成，请重新启动安装脚本以继续执行此程式。
goto :end

:install_pipx
echo [*] 安装 pipx 中...
pip install pipx -i https://mirrors.aliyun.com/pypi/simple/
goto :check_pipx

:install_pdm
echo [*] 安装 PDM 中...
pipx install pdm -i https://mirrors.aliyun.com/pypi/simple/
goto :check_pdm

:install_ipm
echo [*] 安装 IPM 中...
pipx install ipdm^>=0.2.0-beta -i https://mirrors.aliyun.com/pypi/simple/
goto :check_ipm

:install_nb_cli
echo [*] 安装 nb-cli 中...
pipx install nb-cli -i https://mirrors.aliyun.com/pypi/simple/
goto :check_nb_cli


:setup_env
echo [*] 配置环境中...
:check_pdm
pdm --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] PDM 已正确安装。
) else (
    goto :install_pdm
)
:check_ipm
ipm --help > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] IPM 已正确安装。
) else (
    goto :install_ipm
)
:check_nb_cli
nb --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] nb-cli 已正确安装。
) else (
    goto :install_nb_cli
)
echo [*] 检查规则包环境...
ipm check
if %errorlevel% equ 0 (
    echo [+] 规则包环境检查完成。
) else (
    echo [-] 检查规则包环境时出现异常。
    goto :end
)
echo [*] 同步依赖环境中...
ipm sync
if %errorlevel% equ 0 (
    echo [+] 规则包依赖环境同步完成。
) else (
    echo [-] 检查规则包环境时出现异常。
    goto :end
)
echo [*] 安装依赖环境中...
ipm install
if %errorlevel% equ 0 (
    echo [+] 规则包依赖环境安装完成。
) else (
    echo [-] 安装规则包环境时出现异常。
    goto :end
)

:run
run.bat

:end
pause
