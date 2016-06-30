import sys

from config_probe.exceptions import ConfigNotFound


class MunchWrapper(object):
    def __init__(self, munch):
        self.munch = munch

    def __getattr__(self, item):
        try:
            result = self.munch.__getattr__(item)
        except AttributeError as e:
            raise ConfigNotFound(e)
        if type(result) in _get_primitive_type():
            return result
        return MunchWrapper(self.munch.__getattr__(item))


if sys.version_info < (3,):
    def _get_primitive_type():
        return int, float, long, bool, list, str, unicode
else:
    def _get_primitive_type():
        return int, float, bool, list, str
