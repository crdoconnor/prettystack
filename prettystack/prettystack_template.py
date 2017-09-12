from prettystack.traceback import PrettyTraceback
from prettystack import exceptions, utils
from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from path import Path
from copy import copy
import colorama


TEMPLATE_FOLDER = Path(__file__).abspath().dirname()


class PrettyStackTemplate(object):
    """
    Template for generating pretty stacktraces on command.
    """
    def __init__(self):
        self._template = TEMPLATE_FOLDER.joinpath("console.jinja2")
        self._cut_calling_code = None

    def to_console(self):
        """
        Returns a template that will render stacktraces to the console, in color.
        """
        new_template = copy(self)
        new_template._template = TEMPLATE_FOLDER.joinpath("console.jinja2")
        return new_template

    def cut_calling_code(self, filename):
        """
        Display all stacktrace lines until the exception hits this filename.

        Will not show any part of the stacktrace in this filename or beneath it.
        """
        if not Path(filename).exists():
            raise exceptions.StackTraceFilenameNotFound(filename)
        new_template = copy(self)
        new_template._cut_calling_code = Path(filename).abspath()
        return new_template

    def from_stacktrace_data(self, data):
        """
        Display a nicely formatted string representing a prettified
        form of the stacktrace data supplied in the data dict.
        """
        ## Cut out lower level tracebacks that we were instructed to ignore
        tracebacks = [PrettyTraceback(traceback) for traceback in data['tracebacks']]
        
        if self._cut_calling_code is not None:
            updated_tracebacks = []
            start_including = False
            for traceback in tracebacks:
                if start_including and traceback.abspath != self._cut_calling_code:
                    updated_tracebacks.append(traceback)

                if traceback.abspath == self._cut_calling_code:
                    start_including = True
            tracebacks = updated_tracebacks

        # Render list of tracebacks to template
        env = Environment()
        env.loader = FileSystemLoader(str(self._template.dirname()))
        tmpl = env.get_template(str(self._template.basename()))
        return tmpl.render(
            stacktrace={
                'tracebacks': [traceback.to_dict() for traceback in tracebacks],
                'exception': data['exception_string'],
                'exception_type': data['exception_type'],
                'docstring': data['docstring'],
            },
            Fore=colorama.Fore,
            Back=colorama.Back,
            Style=colorama.Style,
        )

    def current_stacktrace(self):
        """
        Return a nicely formatted string representing a prettified form
        of the current stacktrace.
        """
        return self.from_stacktrace_data(utils.current_stack_trace_data())
