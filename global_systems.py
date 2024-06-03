import asyncio
import os
import time
import datetime
import psutil
ptimer = time.time()

exit_check = False
while not exit_check:
	asyncio.sleep(10)
	batery: psutil._common.sbattery = psutil.sensors_battery()
	print(f"Battery: {batery.percent}")
	ptimer = time.time()
	if batery.percent<25:
		with open('logs/auto_poweroff.txt', 'w') as file:
			file.write(f'Auto poweroff at {datetime.datetime.now().strftime("%c")}')
		os.system('systemctl poweroff')