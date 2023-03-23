from hitchstory import StoryCollection, BaseEngine, validate
from hitchstory import GivenDefinition, GivenProperty, InfoDefinition, InfoProperty
from strictyaml import Str, Seq, Map, Optional, Enum, MapPattern
from hitchstory import no_stacktrace_for
from hitchrunpy import ExamplePythonCode, HitchRunPyException
from commandlib import Command
from templex import Templex
from path import Path
import colorama
import re


class Engine(BaseEngine):
    """Python engine for running tests."""

    given_definition = GivenDefinition(
        files=GivenProperty(MapPattern(Str(), Str())),
        setup=GivenProperty(Str()),
        code=GivenProperty(Str()),
        example1_py=GivenProperty(Str()),
        example2_py=GivenProperty(Str()),
        example3_py=GivenProperty(Str()),
    )

    info_definition = InfoDefinition(
        status=InfoProperty(schema=Enum(["experimental", "stable"])),
        docs=InfoProperty(schema=Str()),
    )

    def __init__(self, paths, python_path, rewrite=False, cprofile=False):
        self.path = paths
        self._rewrite = rewrite
        self._python_path = python_path
        self._cprofile = cprofile

    def set_up(self):
        """Set up the environment ready to run the stories."""
        self.path.q = Path("/tmp/q")
        self.path.state = self.path.gen.joinpath("state")
        self.path.working = self.path.state / "working"

        if self.path.q.exists():
            self.path.q.remove()
        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()
        
        self._included_files = []

        for filename, contents in list(self.given.get("files", {}).items()):
            self.path.state.joinpath(filename).write_text(self.given["files"][filename])
            self._included_files.append(self.path.state.joinpath(filename))

        self.python = Command(self._python_path)
        
        self.example_py_code = (
            ExamplePythonCode(self.python, self.path.state)
            .with_setup_code(self.given.get("setup", ""))
            .with_terminal_size(160, 100)
            .include_files(*self._included_files)
        )
    
    def run_code(self):
        to_run = self.example_py_code.with_code(self.given["code"])
        
        result = to_run.run()
        self._actual_output = result.output
    
    def output_will_be(self, will_output):
        try:
            Templex(will_output).assert_match(self._actual_output)
        except AssertionError:
            if self._rewrite:
                self.current_step.update(**{"will_output": self._actual_output})
            else:
                raise


    def pause(self, message="Pause"):
        import IPython

        IPython.embed()

    def tear_down(self):
        if self.path.q.exists():
            print(self.path.q.text())

    def on_success(self):
        if self._rewrite:
            self.new_story.save()
