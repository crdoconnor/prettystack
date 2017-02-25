"""
Traceback and exception related code.
"""

from path import Path


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
            'filename': self.filename,
            'lineno': self.lineno,
            'function': self.func,
            'line': self._location.line_no,
            'location': self.location,
        }

    @property
    def location(self):
        return self._location

    @property
    def filename(self):
        return self.traceback.tb_frame.f_code.co_filename

    @property
    def abspath(self):
        return Path(self.filename).abspath()

    @property
    def lineno(self):
        return self.traceback.tb_lineno

    @property
    def func(self):
        return self.traceback.tb_frame.f_code.co_name

    @property
    def localvars(self):
        return self.traceback.tb_frame.f_locals

    @property
    def globalvars(self):
        return self.traceback.tb_frame.f_globals

    @property
    def frame(self):
        return self.traceback.tb_frame

    def __repr__(self):
        return "[{}] File {}, line {} in {}.".format(
            self.tb_id,
            self.filename,
            self.lineno,
            self.func,
        )
