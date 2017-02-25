from prettystack.traceback import PrettyTraceback
from prettystack import exceptions
from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from path import Path
from copy import copy
import colorama
import sys


TEMPLATE_FOLDER = Path(__file__).abspath().dirname()


class PrettyStackTemplate(object):
    """
    Template for generating pretty stacktraces on command.
    """
    def __init__(self):
        self._template = TEMPLATE_FOLDER.joinpath("console.jinja2")
        self._stop_before_filename = None
        self._only_after_filename = None

    def to_console(self):
        """
        Returns a template that will render stacktraces to the console, in color.
        """
        new_template = copy(self)
        new_template._template = TEMPLATE_FOLDER.joinpath("console.jinja2")
        return new_template

    def stop_before_file(self, filename):
        """
        Display all stacktrace lines until the exception hits this filename.

        Will not show any part of the stacktrace in this filename or beneath it.
        """
        if not Path(filename).exists():
            raise exceptions.StackTraceFilenameNotFound(filename)
        new_template = copy(self)
        new_template._stop_before_filename = Path(filename).abspath()
        return new_template

    def only_after_file(self, filename):
        """
        Display all stacktrace lines after this filename.

        Will not show any part of the stacktrace in this filename above it.
        """
        if not Path(filename).exists():
            raise exceptions.StackTraceFilenameNotFound(filename)
        new_template = copy(self)
        new_template._only_after_filename = Path(filename).abspath()
        return new_template

    def current_stacktrace(self):
        tb_id = 0
        self.exception = sys.exc_info()[1]
        tb = sys.exc_info()[2]
        # Create list of tracebacks
        tracebacks = []
        while tb is not None:
            filename = tb.tb_frame.f_code.co_filename
            if filename == '<frozen importlib._bootstrap>':
                break

            tracebacks.append(PrettyTraceback(tb_id, tb))
            tb_id = tb_id + 1
            tb = tb.tb_next

        # Cut out lower level tracebacks that we were instructed to ignore
        if self._stop_before_filename is not None:
            updated_tracebacks = []
            for traceback in tracebacks:
                if self._stop_before_filename == traceback.abspath:
                    break
                updated_tracebacks.append(traceback)
            tracebacks = updated_tracebacks

        # Cut out higher level tracebacks that we were instructed to ignore
        if self._only_after_filename is not None:
            updated_tracebacks = []
            start_appending = False
            for traceback in reversed(tracebacks):
                if start_appending:
                    updated_tracebacks.append(traceback)
                if self._only_after_filename == traceback.abspath:
                    start_appending = True
            tracebacks = list(reversed(updated_tracebacks))

        # Render list of tracebacks to template
        env = Environment()
        env.loader = FileSystemLoader(str(self._template.dirname()))
        tmpl = env.get_template(str(self._template.basename()))
        return tmpl.render(
            stacktrace={
                'tracebacks': [traceback.to_dict() for traceback in tracebacks],
                'exception': str(self.exception),
                'exception_type': "{}.{}".format(
                    type(self.exception).__module__, type(self.exception).__name__
                ),
                'docstring': str(self.exception.__doc__)
                if self.exception.__doc__ is not None else None
            },
            Fore=colorama.Fore,
            Back=colorama.Back,
            Style=colorama.Style,
        )
