import asyncio
import os
import time
import datetime
import psutil
ptimer = time.time()

with open('logs/global_systems_logs.txt', 'w') as file:
	file.write('')
exit_check = False
while not exit_check:
	batery: psutil._common.sbattery = psutil.sensors_battery()
	with open('logs/global_systems_logs.txt', 'a') as file:
		file.write(f"Battery: {batery.percent} {datetime.datetime.now().strftime('%c')}\n")
	time.sleep(10)
	ptimer = time.time()
	if batery.percent<25:
		with open('logs/auto_poweroff.txt', 'w') as file:
			file.write(f'Auto poweroff at {datetime.datetime.now().strftime("%c")}')
		os.system('systemctl poweroff')