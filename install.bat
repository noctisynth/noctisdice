@echo off

type COPYRIGHT
echo.

echo [*] ¼ì²é Python »·¾³ÖĞ...
:check_python
python --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] Python ÒÑÕıÈ·°²×°¡£[0m
) else (
    goto :install_python
)
python -m pip -V > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] pip ÒÑÕıÈ·°²×°¡£[0m
) else (
    echo [33m[!] Î´ÕÒµ½ pip »·¾³£¬ÖØĞÂÏÂÔØ°²×° Python¡£[0m
    goto :install_python
)
:check_pipx
pipx --version > nul 2>&1
pipx ensurepath > nul 2>&1
for /f "delims=" %%a in ('python -c "import os; print(os.environ['PATH'])"') do (
    set "PATH=%%a"
)
if %errorlevel% equ 0 (
    echo [32m[+] pipx ÒÑÕıÈ·°²×°¡£[0m
    goto :setup_env
) else (
    goto :install_pipx
)


:install_python
echo [*] ÕıÔÚÏÂÔØ Python °²×°³ÌĞò...
curl https://cdn.npmmirror.com/binaries/python/3.12.2/python-3.12.2-amd64.exe -o python_installer.exe

echo [*] °²×° Python...
echo [33m[!] ×¢Òâ: ÇëÎñ±Ø¹´Ñ¡ Add Python 3.12 to PATH[0m
start /wait python_installer.exe

del /q python_installer.exe
echo [32m[+] Python °²×°Íê³É£¬ÇëÖØĞÂÆô¶¯°²×°½Å±¾ÒÔ¼ÌĞøÖ´ĞĞ´Ë³ÌÊ½¡£[0m
goto :end

:install_pipx
echo [*] °²×° pipx ÖĞ...
pip install pipx -i https://mirrors.aliyun.com/pypi/simple/
goto :check_pipx

:install_pdm
echo [*] °²×° PDM ÖĞ...
pipx install pdm -i https://mirrors.aliyun.com/pypi/simple/
goto :check_pdm

:install_ipm
echo [*] °²×° IPM ÖĞ...
pipx install ipdm^>=0.2.0-beta -i https://mirrors.aliyun.com/pypi/simple/
goto :check_ipm

:install_nb_cli
echo [*] °²×° nb-cli ÖĞ...
pipx install nb-cli -i https://mirrors.aliyun.com/pypi/simple/
goto :check_nb_cli


:setup_env
echo [*] ÅäÖÃ»·¾³ÖĞ...
:check_pdm
pdm --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] PDM ÒÑÕıÈ·°²×°¡£[0m
) else (
    goto :install_pdm
)
:check_ipm
ipm --help > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] IPM ÒÑÕıÈ·°²×°¡£[0m
) else (
    goto :install_ipm
)
:check_nb_cli
nb --version > nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[+] nb-cli ÒÑÕıÈ·°²×°¡£[0m
) else (
    goto :install_nb_cli
)
echo [*] ¼ì²é¹æÔò°ü»·¾³...
ipm check
if %errorlevel% equ 0 (
    echo [32m[+] ¹æÔò°ü»·¾³¼ì²éÍê³É¡£[0m
) else (
    echo [31m[-] ¼ì²é¹æÔò°ü»·¾³Ê±³öÏÖÒì³£¡£[0m
    goto :end
)
echo [*] Í¬²½ÒÀÀµ»·¾³ÖĞ...
ipm sync
if %errorlevel% equ 0 (
    echo [32m[+] ¹æÔò°üÒÀÀµ»·¾³Í¬²½Íê³É¡£[0m
) else (
    echo [31m[-] ¼ì²é¹æÔò°ü»·¾³Ê±³öÏÖÒì³£¡£[0m
    goto :end
)
echo [*] °²×°ÒÀÀµ»·¾³ÖĞ...
ipm install
if %errorlevel% equ 0 (
    echo [32m[+] ¹æÔò°üÒÀÀµ»·¾³°²×°Íê³É¡£[0m
) else (
    echo [31m[-] °²×°¹æÔò°ü»·¾³Ê±³öÏÖÒì³£¡£[0m
    goto :end
)

:run
run.bat

:end
pause
