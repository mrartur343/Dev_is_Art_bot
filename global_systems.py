import os
import time
import datetime
import psutil
ptimer = time.time()

exit_check = False
while not exit_check:
	batery: psutil._common.sbattery = psutil.sensors_battery()
	if time.time()-ptimer>10:
		print(batery.percent)
		ptimer = time.time()
	if batery.percent<80:
		os.system('pkill python3')
		with open('logs/auto_pkill.txt', 'w') as file:
			file.write(f'Auto auto pkill python3 at {datetime.datetime.now().strftime("%c")}')
	if batery.percent<15:
		with open('logs/auto_poweroff.txt', 'w') as file:
			file.write(f'Auto poweroff at {datetime.datetime.now().strftime("%c")}')
		os.system('systemctl poweroff')