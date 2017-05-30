import os
import imp


def find_module_path(module):
    """
    Returns the path to a given module, without importing it or any parent
    module
    Raises ImportError if the module does not seem to exist
    """

    module_py_path = module.split('.')
    module_py_path.reverse()
    path = imp.find_module(module_py_path.pop())[1]
    while module_py_path:
        path = os.path.join(path, module_py_path.pop())

    if os.path.isfile(path + '.py'):
        return path + '.py'

    if not os.path.isfile(os.path.join(path, '__init__.py')):
        raise ImportError('Could not find module "%s"' % module)

    return path
