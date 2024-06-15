import os
import sys

track_url = sys.argv[1]

print(track_url+"...")
os.system(f'cd downloaded_songs;spotdl download {track_url} --port 8734')
print(track_url)
