
def now_time_str():
    import datetime
    local_time = datetime.datetime.now()
    return local_time.strftime('%Y-%m-%d %H:%M:%S')
