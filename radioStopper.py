import psutil
import sys

kill_only_alpha = bool(int(sys.argv[1]))

if kill_only_alpha:
	PROC_NAMES = ["mainRadio.py"]
else:
	PROC_NAMES = ["mainRadio.py"]


for proc in psutil.process_iter():
	# check whether the process to kill name matches
	if proc.name() in PROC_NAMES:
		proc.kill()
