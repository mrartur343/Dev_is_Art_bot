import datetime
import typing

def get_album_times2(albums_names: typing.List[str], albums_duration: typing.Dict[str,int], current_album: int, next_time: datetime.datetime):
    albums_names = albums_names[(current_album+1):]+albums_names[:(current_album+1)]

    timetable: list = []

    iter_time = next_time
    for album_name in albums_names:
        album_duration=albums_duration[album_name]
        timetable.append((album_name,iter_time))
        iter_time = iter_time+datetime.timedelta(seconds=album_duration)


    return timetable