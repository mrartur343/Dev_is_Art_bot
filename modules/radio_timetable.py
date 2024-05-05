import datetime
import typing

def get_album_times(albums_names: typing.List[str], albums_duration: typing.Dict[str,int], current_album: str, next_time: datetime.datetime=None):
    if next_time==None:
        next_time=datetime.datetime.now()+datetime.timedelta(seconds=100)
    while albums_names[0]!=current_album:
        albums_names = albums_names[1:] + albums_names[:1]
    albums_names = albums_names[1:] + albums_names[:1]

    timetable: list = []

    iter_time = next_time
    for album_name in albums_names:
        album_duration=albums_duration[album_name]
        timetable.append((album_name,iter_time))
        iter_time = iter_time+datetime.timedelta(seconds=album_duration)


    return timetable