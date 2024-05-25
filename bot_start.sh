pkill python3
git pull
apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
nohup python3 main.py &
nohup python3 mainBeta.py &
python3 mainGamma.py