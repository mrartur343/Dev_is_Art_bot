import datetime
import typing

def get_album_times(albums_names: typing.List[str], albums_duration: typing.List[int], current_album: str, next_time: datetime.datetime):
    while albums_names[0]!=current_album:
        albums_names = albums_names[1:] + albums_names[:1]
        albums_duration = albums_duration[1:] + albums_duration[:1]
    albums_names = albums_names[1:] + albums_names[:1]
    albums_duration = albums_duration[1:] + albums_duration[:1]

    timetable = {}

    iter_time = next_time
    for album_name, album_duration in zip(albums_names, albums_duration):
        timetable[album_name] = iter_time
        iter_time = iter_time+datetime.timedelta(seconds=album_duration)


    return timetable