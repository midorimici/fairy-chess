@echo off
cd codes
if "%~1" == "d" (
	python dict/play.py 
) else if "%~1" == "p" (
	if "%~3" == "a" (
		python dict/play.py %~2 %~4
	) else (
		python dict/play.py %~2
	)
) else if "%~1" == "w" (
	python main/play.py W
) else if "%~1" == "b" (
	python main/play.py B
) else (
	python main/play.py
)
