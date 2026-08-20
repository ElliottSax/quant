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

REM Spec 8: any disagreement between the two engines quarantines BOTH, and nothing
REM publishes until it is reconciled. The harness was previously never invoked here, so
REM a divergence could be recorded to the permanent log unnoticed.
python -m pipeline.cross_check >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ENGINES DISAGREE - both quarantined, calibration record skipped >> "%LOG%"
  exit /b 3
)

python -m pipeline.calibration record >> "%LOG%" 2>&1
python -m pipeline.calibration verify >> "%LOG%" 2>&1
if errorlevel 1 (
  echo CALIBRATION INTEGRITY FAILURE - the record was altered after the fact >> "%LOG%"
  exit /b 2
)

REM Publish only what the record contains: export_verdicts refuses unless the ingest was
REM clean and every tier matches the calibration log.
python -m pipeline.export_verdicts >> "%LOG%" 2>&1
if errorlevel 1 (
  echo EXPORT REFUSED - site data not updated >> "%LOG%"
  exit /b 4
)

python -m pipeline.export_prices >> "%LOG%" 2>&1
if errorlevel 1 (
  echo PRICE EXPORT REFUSED - chart/ticker data not updated >> "%LOG%"
  exit /b 5
)

REM Vendor bench: re-measured nightly so the published comparison cannot go stale.
REM Not gated - a provider failing its probe IS the measurement, not a reason to abort.
python -m pipeline.bench >> "%LOG%" 2>&1

echo daily run OK >> "%LOG%"
exit /b 0
