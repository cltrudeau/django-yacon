import datetime

def right_now(request, context, block):
    return '%s' % datetime.datetime.now()
