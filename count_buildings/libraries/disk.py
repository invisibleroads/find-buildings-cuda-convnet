import os
import shutil


def replace_folder(*parts):
    folder = os.path.join(*parts)
    try:
        shutil.rmtree(folder)
    except OSError:
        pass
    return make_folder(*parts)


def make_folder(*parts):
    folder = os.path.join(*parts)
    try:
        os.makedirs(folder)
    except OSError:
        pass
    return folder
