import importlib

PLUGIN_NAMESPACE = 'plugs'

_classes = []
_instances = {}


class PapersPlugin(object):
    """The base class for all plugins. Plugins provide
    functionality by defining a subclass of PapersPlugin and overriding
    the abstract methods defined here.
    """
    def __init__(self, config, ui):
        """Perform one-time plugin setup.
        """
        self.name = self.__module__.split('.')[-1]
        self.config = config
        self.ui = ui

    #config and ui and given again to stay consistent with the core papers cmd.
    #two options:
    #- create specific cases in script papers/papers
    #- do not store self.config and self.ui and use them if needed when command is called
    #this may end up a lot of function with config/ui in argument
    #or just keep it this way...
    def parser(self, subparsers, config):
        """ Should retrun the parser with plugins specific command.
        This is a basic example
        """
        parser = subparsers.add_parser(self.name, help="echo string in argument")
        parser.add_argument('strings', nargs='*', help='the strings')
        return parser

    def command(self, config, ui, strings):
        """This function will be called with argument defined in the parser above
        This is a basic example
        """
        for s in strings:
            print s


def load_plugins(config, ui, names):
    """Imports the modules for a sequence of plugin names. Each name
    must be the name of a Python module under the "PLUGIN_NAMESPACE" namespace
    package in sys.path; the module indicated should contain the
    PapersPlugin subclasses desired.
    """
    for name in names:
        modname = '%s.%s.%s.%s' % ('papers', PLUGIN_NAMESPACE, name, name)
        try:
            try:
                namespace = importlib.import_module(modname)
            except ImportError as exc:
                # Again, this is hacky:
                if exc.args[0].endswith(' ' + name):
                    ui.warning('** plugin %s not found' % name)
                else:
                    raise
            else:
                for obj in namespace.__dict__.values():
                    if isinstance(obj, type) and issubclass(obj, PapersPlugin) \
                            and obj != PapersPlugin:
                        _classes.append(obj)
                        _instances[obj] = obj(config, ui)

        except:
            ui.warning('** error loading plugin %s' % name)


def get_plugins():
    return _instances
