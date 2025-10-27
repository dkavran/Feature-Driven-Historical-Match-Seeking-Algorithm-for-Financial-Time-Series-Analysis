@echo off
setlocal

:: ===== Start timestamp (human + ticks) =====
for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"`) do set "START_HUMAN=%%a"
for /f %%a in ('powershell -NoProfile -Command "(Get-Date).Ticks"') do set "START_TICKS=%%a"
echo [START TIME] %START_HUMAN%

:: Include the variables from the external file
call ./create_environment_scripts/vars.bat

set venv=whiteshark

:: Use the variables instead of hardcoded paths
call %ANACONDA_SCRIPTS_ACTIVATE% %ANACONDA_DIR%
call activate %venv%

set K_NEIGHBORS=100
set INDIVIDUAL_FEATURE_DIFF_THRESHOLD=0.15
set HISTORY_SPAN_START_YEAR=2014
set TARGET_DATE=None

::available distances: eucledian, minkowski, chebyshev
set DISTANCE_METRIC=minkowski

::used only by minkowski distance
set DISTANCE_METRIC_POWER=5

python ./historical_matching_scripts/historical_matching_all.py %K_NEIGHBORS% %INDIVIDUAL_FEATURE_DIFF_THRESHOLD% %HISTORY_SPAN_START_YEAR% %TARGET_DATE% %DISTANCE_METRIC% %DISTANCE_METRIC_POWER%

:: ===== End timestamp and duration =====
for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"`) do set "END_HUMAN=%%a"
for /f %%a in ('powershell -NoProfile -Command "(Get-Date).Ticks"') do set "END_TICKS=%%a"
for /f "delims=" %%a in ('powershell -NoProfile -Command "$d=%END_TICKS% - %START_TICKS%; [timespan]::FromTicks($d).ToString(\"hh\:mm\:ss\")"') do set "DURATION=%%a"

echo [END TIME ] %END_HUMAN%
echo [DURATION ] %DURATION%

endlocal