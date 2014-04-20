import os
import shutil


def get_basename(path):
    return os.path.splitext(os.path.basename(path))[0]


def suffix_name(path, suffix):
    basepath, extension = os.path.splitext(path)
    return basepath + '-' + suffix + extension


def normalize_path(path):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)
    return path


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
