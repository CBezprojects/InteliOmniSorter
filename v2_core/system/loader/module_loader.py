# InteliOmniSorter V2 - Manual module loader

import importlib.util
import os

def load_module_from_path(path, module_name):
    if not os.path.exists(path):
        print("Loader error: path does not exist:", path)
        return None

    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print("Loader error:", e)
        return None
