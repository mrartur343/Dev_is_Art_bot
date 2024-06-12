import datetime
import typing

def get_album_times2(albums_names_sort: typing.List[str], albums_duration: typing.Dict[str,int], current_album: int, next_time: datetime.datetime,song_names_paths: typing.List[str],song_paths: typing.List[str]):
	path_by_name = {}
	for s_name, s_path in zip(song_names_paths,song_paths):
		path_by_name[s_name] = s_path
	
	albums_names_sort = albums_names_sort[(current_album+1):]+albums_names_sort[:(current_album+1)]

	timetable: list = []

	iter_time = next_time
	for album_name in albums_names_sort:
		if album_name in path_by_name:
			album_duration=albums_duration[path_by_name[album_name]]
			timetable.append((path_by_name[album_name],iter_time))
			iter_time = iter_time+datetime.timedelta(seconds=album_duration)


	return timetable