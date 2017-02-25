from jinja2.environment import Environment
from prettystack import exceptions
from jinja2 import FileSystemLoader
from path import Path
import colorama
from copy import copy
import sys


TEMPLATE_FOLDER = Path(__file__).abspath().dirname()


class PrettyStackTemplate(object):
    """
    Template for generating pretty stacktraces on command.
    """
    def __init__(self):
        self._template = TEMPLATE_FOLDER.joinpath("console.jinja2")
        self._stop_before_filename = None

    def to_console(self):
        """
        Returns a template that will render stacktraces to the console, in color.
        """
        new_template = copy(self)
        new_template._template = TEMPLATE_FOLDER.joinpath("console.jinja2")
        return new_template

    def stop_before(self, filename=None):
        """
        Display all stacktrace lines until the exception hits this filename.

        Will not show any part of the stacktrace in this filename or beneath it.
        """
        if not Path(filename).exists():
            raise exceptions.StackTraceFilenameNotFound(filename)
        new_template = copy(self)
        new_template._stop_before_filename = Path(filename).abspath()
        return new_template

    def current_stacktrace(self):
        tb_id = 0
        self.exception = sys.exc_info()[1]
        tb = sys.exc_info()[2]
        # Create list of tracebacks
        self.tracebacks = []
        keep_getting_tracebacks = True
        while tb is not None and keep_getting_tracebacks:
            filename = tb.tb_frame.f_code.co_filename
            if filename == '<frozen importlib._bootstrap>':
                break

            if Path(filename).exists():
                if self._stop_before_filename is not None:
                    if Path(filename).abspath() == self._stop_before_filename:
                        break

            self.tracebacks.append(PrettyTraceback(tb_id, tb))
            tb_id = tb_id + 1
            tb = tb.tb_next

        env = Environment()
        env.loader = FileSystemLoader(str(self._template.dirname()))
        tmpl = env.get_template(str(self._template.basename()))
        return tmpl.render(
            stacktrace={
                'tracebacks': [traceback.to_dict() for traceback in self.tracebacks],
                'exception': str(self.exception),
                'exception_type': "{}.{}".format(
                    type(self.exception).__module__, type(self.exception).__name__
                ),
                'docstring': str(self.exception.__doc__) if self.exception.__doc__ is not None else None
            },
            Fore=colorama.Fore,
            Back=colorama.Back,
            Style=colorama.Style,
        )



class LOC(object):
    """
    Line of python code.
    """
    def __init__(self, code, no, focus):
        self.code = code
        self.no = no
        self.focus = focus

class Location(object):
    """
    Represents a location in a filename where an exception occurred.
    """
    def __init__(self, filename, line_no):
        self._line_no = line_no
        self._contents = Path(filename).bytes().decode("utf8").split("\n") \
            if Path(filename).exists() else None

    @property
    def line_no(self):
        return self._line_no

    @property
    def lines(self):
        if self._contents is None:
            return None
        _lines = []
        for i in range(self._line_no - 3, self._line_no + 1):
            if i > 0 and i < len(self._contents):
                _lines.append(LOC(self._contents[i], i, i == self._line_no - 1))
        return _lines

class PrettyTraceback(object):
    """Representation of a python traceback."""

    def __init__(self, tb_id, traceback):
        self.tb_id = tb_id
        self.traceback = traceback
        self._location = Location(
            self.traceback.tb_frame.f_code.co_filename,
            self.traceback.tb_lineno,
        )

    def to_dict(self):
        return {
            'id': self.tb_id,
            'filename': self.filename(),
            'lineno': self.lineno(),
            'function': self.func(),
            'line': self._location.line_no,
            'location': self.location(),
        }

    def location(self):
        return self._location

    def filename(self):
        return self.traceback.tb_frame.f_code.co_filename

    def lineno(self):
        return self.traceback.tb_lineno

    def func(self):
        return self.traceback.tb_frame.f_code.co_name

    def localvars(self):
        return self.traceback.tb_frame.f_locals

    def globalvars(self):
        return self.traceback.tb_frame.f_globals

    def frame(self):
        return self.traceback.tb_frame

    def __repr__(self):
        return "[{}] File {}, line {} in {}: {}".format(
            self.tb_id,
            self.filename(),
            self.lineno(),
            self.func(),
            self._loc.line_no,
        )
