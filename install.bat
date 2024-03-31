@echo off

type COPYRIGHT
echo.

echo [*] ��� Python ������...
:check_python
python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] Python ����ȷ��װ��[0m
) else (
    goto :install_python
)
python -m pip -V > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] pip ����ȷ��װ��[0m
) else (
    echo [33m[!] δ�ҵ� pip �������������ذ�װ Python��[0m
    goto :install_python
)
:check_pipx
pipx --version > nul 2>&1
pipx ensurepath > nul 2>&1
for /f "delims=" %%a in ('python -c "import os; print(os.environ['PATH'])"') do (
    set "PATH=%%a"
)
if %errorlevel% equ 0 (
    echo [32m[+] pipx ����ȷ��װ��[0m
    goto :setup_env
) else (
    goto :install_pipx
)


:install_python
echo [*] �������� Python ��װ����...
curl https://cdn.npmmirror.com/binaries/python/3.12.2/python-3.12.2-amd64.exe -o python_installer.exe

echo [*] ��װ Python...
echo [33m[!] ע��: ����ع�ѡ Add Python 3.12 to PATH[0m
start /wait python_installer.exe

del /q python_installer.exe
echo [32m[+] Python ��װ��ɣ�������������װ�ű��Լ���ִ�д˳�ʽ��[0m
goto :end

:install_pipx
echo [*] ��װ pipx ��...
pip install pipx -i https://mirrors.aliyun.com/pypi/simple/
goto :check_pipx

:install_pdm
echo [*] ��װ PDM ��...
pipx install pdm -i https://mirrors.aliyun.com/pypi/simple/
goto :check_pdm

:install_ipm
echo [*] ��װ IPM ��...
pipx install ipdm^>=0.2.0-beta -i https://mirrors.aliyun.com/pypi/simple/
goto :check_ipm

:install_nb_cli
echo [*] ��װ nb-cli ��...
pipx install nb-cli -i https://mirrors.aliyun.com/pypi/simple/
goto :check_nb_cli


:setup_env
echo [*] ���û�����...
:check_pdm
pdm --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] PDM ����ȷ��װ��[0m
) else (
    goto :install_pdm
)
:check_ipm
ipm --help > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] IPM ����ȷ��װ��[0m
) else (
    goto :install_ipm
)
:check_nb_cli
nb --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] nb-cli ����ȷ��װ��[0m
) else (
    goto :install_nb_cli
)
echo [*] �����������...
ipm check
if %errorlevel% equ 0 (
    echo [32m[+] ��������������ɡ�[0m
) else (
    echo [31m[-] �����������ʱ�����쳣��[0m
    goto :end
)
echo [*] ͬ������������...
ipm sync
if %errorlevel% equ 0 (
    echo [32m[+] �������������ͬ����ɡ�[0m
) else (
    echo [31m[-] �����������ʱ�����쳣��[0m
    goto :end
)
echo [*] ��װ����������...
ipm install
if %errorlevel% equ 0 (
    echo [32m[+] ���������������װ��ɡ�[0m
) else (
    echo [31m[-] ��װ���������ʱ�����쳣��[0m
    goto :end
)

:run
run.bat

:end
pause
