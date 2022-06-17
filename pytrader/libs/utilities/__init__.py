import importlib


def get_plugin_function(*args, **kwargs):
    subcommand = kwargs['scmd']
    program = kwargs['program']
    command = kwargs['cmd']
    import_path = kwargs['import_path']

    module_name = import_path + program

    try:
        module = importlib.import_module(module_name, __name__)
        return getattr(module, command)
    except ImportError as msg:
        raise ImportError(msg)
    except AttributeError as msg:
        raise AttributeError(msg)
