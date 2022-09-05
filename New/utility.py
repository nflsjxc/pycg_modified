import pathlib
import os
import sys
import importlib


def get_package_dir(module_name):
    try:
        module=importlib.import_module(module_name)
        init_path=os.path.abspath(module.__file__)
        path=pathlib.Path(init_path)
        return os.path.abspath(path.parent)
    except TypeError:
        return None
    except AttributeError:
        return None
    except:
        return None
if __name__=="__main__":
    print(get_package_dir('torch'))
    # print(eval('torchvision.__file__'))
