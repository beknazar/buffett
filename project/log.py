import logging
import os

try:
    import curses
    os.environ['TERM'] = 'xterm'
    curses.setupterm()
except ImportError:
    curses = None


def convert_to_byte(data, encoding='utf-8'):
    if isinstance(data, basestring):
        return data.encode(encoding) if isinstance(data, unicode) else data
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_to_byte, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_to_byte, data))
    else:
        return data


class ColorFormatter(logging.Formatter):
    def __init__(self, color=True, *args, **kwargs):
        super(ColorFormatter, self).__init__(*args, **kwargs)

        self._color = color and bool(curses)
        self._color_map = None

    @property
    def color_map(self):
        if self._color_map is None:
            fg_color = (curses.tigetstr('setaf') or
                        curses.tigetstr('setf') or '')
            self._color_map = {
                logging.INFO: unicode(curses.tparm(fg_color, 2),     # G
                                        'ascii'),
                logging.WARNING: unicode(curses.tparm(fg_color, 3),  # Y
                                            'ascii'),
                logging.ERROR: unicode(curses.tparm(fg_color, 1),    # R
                                        'ascii'),
                logging.CRITICAL: unicode(curses.tparm(fg_color, 1), # R
                                            'ascii'),
            }
            self._normal_color = unicode(curses.tigetstr('sgr0'), 'ascii')
        return self._color_map

    def format(self, record):
        formatted = super(ColorFormatter, self).format(record)
        if self._color:
            prefix = self.color_map.get(record.levelno, self._normal_color)
            formatted = \
                convert_to_byte(prefix) \
                + convert_to_byte(formatted) \
                + convert_to_byte(self._normal_color)
        return formatted
