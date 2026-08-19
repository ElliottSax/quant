@echo off
REM Nightly compute plane (plan story 1.2 + 1.5). Registered with Task Scheduler.
REM
REM Order matters and the gate is real: if the ingest does not report a clean night
REM the calibration record is NOT written. A gap in the record is honest; a row
REM recorded from stale or partial data is a lie that compounds for years, because
REM the whole value of the log is that its history can be trusted.
REM
REM Reads FMP_API_KEY from quant\pipeline\.env.local (git-ignored, one KEY=VALUE per
REM line). Log lines append to quant\logs\pipeline.log.

setlocal enabledelayedexpansion
set "ROOT=%~dp0.."
cd /d "%ROOT%"

if not exist "logs" mkdir "logs"
set "LOG=%ROOT%\logs\pipeline.log"

for /f "usebackq tokens=1,* delims==" %%A in ("%ROOT%\pipeline\.env.local") do (
  if not "%%A"=="" set "%%A=%%B"
)

echo. >> "%LOG%"
echo ================ %DATE% %TIME% ================ >> "%LOG%"

python -m pipeline.run_nightly >> "%LOG%" 2>&1
if errorlevel 1 (
  echo NOT A CLEAN NIGHT - calibration record skipped, publish blocked >> "%LOG%"
  exit /b 1
)

python -m pipeline.calibration record >> "%LOG%" 2>&1
python -m pipeline.calibration verify >> "%LOG%" 2>&1
if errorlevel 1 (
  echo CALIBRATION INTEGRITY FAILURE - the record was altered after the fact >> "%LOG%"
  exit /b 2
)

echo daily run OK >> "%LOG%"
exit /b 0
