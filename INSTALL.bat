@echo off
setlocal EnableDelayedExpansion
title The Deep Diver - Doorman
cd /d "%~dp0"

rem ============================================================
rem  THE DEEP DIVER - DOORMAN (INSTALL.bat)
rem  One press starts the install. The doorman:
rem    1. Finds Python (asks for nothing if it is already there)
rem    2. Installs the text-reading part (pypdf)
rem    3. Lays the Diver in D:\deep-diver (pond and index untouched)
rem    4. Makes a desktop shortcut wearing the Diver's face
rem    5. Checks every piece and writes a receipt
rem  He changes nothing outside the Diver's own folder and your
rem  desktop shortcut. Deleting the folder is the uninstall.
rem ============================================================

set "DEST=D:\deep-diver"
set "LOG=%~dp0install-receipt.txt"
set "FAIL=0"

echo ============================================================
echo.
echo    ***  CLICK WORKED - THE DOORMAN IS INSTALLING  ***
echo    ***         THE DEEP DIVER - WATCH HIM GO       ***
echo.
echo ============================================================
echo.
echo One press started this. Everything from here is machinery:
echo find Python, lay him in D:\deep-diver, shortcut on the
echo desktop wearing his face, verify every piece, receipt.
echo.
> "%LOG%" echo THE DEEP DIVER - INSTALL RECEIPT
>>"%LOG%" echo Started: %DATE% %TIME%
>>"%LOG%" echo Pack folder: %~dp0
>>"%LOG%" echo.

rem ---------- 1. Python ----------
where python >nul 2>nul
if errorlevel 1 (
  echo Python is NOT on this machine, and the Diver swims on Python.
  echo Nothing was installed. Get Python free from python.org,
  echo tick "Add python.exe to PATH" during its setup, then press
  echo INSTALL again. It is safe to run me twice.
  >>"%LOG%" echo RESULT: STOPPED - Python not found on PATH.
  set "FAIL=1"
  goto :finish
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo Found Python %PYVER%.
>>"%LOG%" echo Python: %PYVER%

rem ---------- 2. The text-reading part ----------
python -c "import pypdf" 2>nul
if not errorlevel 1 (
  echo The text-reading part - pypdf - is already here.
  >>"%LOG%" echo pypdf: already installed.
) else (
  echo Installing the text-reading part - pypdf - one moment...
  python -m pip install --user pypdf >>"%LOG%" 2>&1
  python -c "import pypdf" 2>nul
  if errorlevel 1 (
    echo pypdf would not install - the full pip output is in
    echo install-receipt.txt next to me. Nothing else was changed.
    >>"%LOG%" echo RESULT: STOPPED - pypdf install failed.
    set "FAIL=1"
    goto :finish
  )
  echo pypdf installed.
  >>"%LOG%" echo pypdf: installed by the doorman.
)

rem ---------- 3. Lay him in D:\deep-diver ----------
if not exist "%DEST%" mkdir "%DEST%"
set "COPIED="
for %%f in (dive.py diver_face.py jobs.txt DIVE.bat FACE.bat STANDARDS.md HARBOURS.md README-PLAIN.txt README.md deep-diver-icon-512.png deep-diver-icon-1024.png deep-diver.ico) do (
  if exist "%%f" (
    copy /y "%%f" "%DEST%\" >nul
    if errorlevel 1 (
      echo Could not lay %%f into %DEST%.
      >>"%LOG%" echo COPY FAILED: %%f
      set "FAIL=1"
    ) else (
      set "COPIED=!COPIED! %%f"
    )
  )
)
echo Laid the Diver in %DEST% - your pond, index and receipts, if
echo any were already there, were NOT touched.
>>"%LOG%" echo Destination: %DEST%
>>"%LOG%" echo Files laid:!COPIED!

rem ---------- 4. Desktop shortcut (best effort) ----------
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut([IO.Path]::Combine([Environment]::GetFolderPath('Desktop'),'Deep Diver.lnk')); $s.TargetPath='%DEST%\FACE.bat'; $s.WorkingDirectory='%DEST%'; if (Test-Path '%DEST%\deep-diver.ico') { $s.IconLocation='%DEST%\deep-diver.ico' }; $s.Description='The Deep Diver - his window'; $s.Save()" 2>nul
if exist "%USERPROFILE%\Desktop\Deep Diver.lnk" (
  echo Desktop shortcut made: "Deep Diver", wearing his face.
  >>"%LOG%" echo Shortcut: made on the desktop.
) else (
  echo The desktop shortcut did not take - no harm done. He runs
  echo fine by double-clicking DIVE.bat inside %DEST%.
  >>"%LOG%" echo Shortcut: NOT made - best effort, non-fatal.
)

rem ---------- 5. Verify every piece, write the receipt ----------
set "MISSING="
for %%f in (dive.py diver_face.py DIVE.bat FACE.bat jobs.txt STANDARDS.md deep-diver.ico) do (
  if not exist "%DEST%\%%f" set "MISSING=!MISSING! %%f"
)
python -c "import pypdf" 2>nul
if errorlevel 1 set "MISSING=!MISSING! pypdf"
if defined MISSING (
  echo.
  echo FINISHED WITH HOLES - missing:!MISSING!
  echo The receipt next to me - install-receipt.txt - has the details.
  >>"%LOG%" echo RESULT: INCOMPLETE - missing:!MISSING!
  set "FAIL=1"
  goto :finish
)
>>"%LOG%" echo RESULT: COMPLETE - every piece verified in place.
echo.
echo DONE. The Diver is installed at %DEST%.
echo Double-click "Deep Diver" on your desktop and his window
echo opens. The job list still runs from DIVE.bat in his folder.
echo This receipt also lives in install-receipt.txt, next to me.

:finish
>>"%LOG%" echo Finished: %DATE% %TIME%
echo.
pause
exit /b %FAIL%
