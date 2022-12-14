import os
from random import randrange

def authorInVoiceChannel(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        return False
    else:
        return True

def getPath():
    return os.path.join(os.path.dirname(__file__), "..", "..", "data", "phasmo_roles.txt")

def get_role():
    role_list = open(getPath(), "r", encoding = "utf-8")
    line = next(role_list)
    for num, aline in enumerate(role_list, 2):
        if randrange(num):
            continue
        line = aline

    return line