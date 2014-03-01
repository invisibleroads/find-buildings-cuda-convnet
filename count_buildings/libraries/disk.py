import os


def make_folder(*parts):
    folder = os.path.join(*parts)
    try:
        os.makedirs(folder)
    except OSError:
        pass
    return folder
