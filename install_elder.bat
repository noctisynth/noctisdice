@echo off

echo [*] ��� Python ������...
:check_python
python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] Python ����ȷ��װ��
) else (
    goto :install_python
)
python -m pip -V > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] pip ����ȷ��װ��
) else (
    echo [!] δ�ҵ� pip �������������ذ�װ Python��
    goto :install_python
)
:check_pipx
pipx --version > nul 2>&1
pipx ensurepath > nul 2>&1
for /f "delims=" %%a in ('python -c "import os; print(os.environ['PATH'])"') do (
    set "PATH=%%a"
)
if %errorlevel% equ 0 (
    echo [+] pipx ����ȷ��װ��
    goto :setup_env
) else (
    goto :install_pipx
)


:install_python
echo [*] �������� Python ��װ����...
curl https://cdn.npmmirror.com/binaries/python/3.12.2/python-3.12.2-amd64.exe -o python_installer.exe

echo [*] ��װ Python...
echo [!] ע��: ����ع�ѡ Add Python 3.12 to PATH
start /wait python_installer.exe

del /q python_installer.exe
echo [+] Python ��װ��ɣ�������������װ�ű��Լ���ִ�д˳�ʽ��
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
    echo [+] PDM ����ȷ��װ��
) else (
    goto :install_pdm
)
:check_ipm
ipm --help > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] IPM ����ȷ��װ��
) else (
    goto :install_ipm
)
:check_nb_cli
nb --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [+] nb-cli ����ȷ��װ��
) else (
    goto :install_nb_cli
)
echo [*] �����������...
ipm check
if %errorlevel% equ 0 (
    echo [+] ��������������ɡ�
) else (
    echo [-] �����������ʱ�����쳣��
    goto :end
)
echo [*] ͬ������������...
ipm sync
if %errorlevel% equ 0 (
    echo [+] �������������ͬ����ɡ�
) else (
    echo [-] �����������ʱ�����쳣��
    goto :end
)
echo [*] ��װ����������...
ipm install
if %errorlevel% equ 0 (
    echo [+] ���������������װ��ɡ�
) else (
    echo [-] ��װ���������ʱ�����쳣��
    goto :end
)

:run
run.bat

:end
pause
