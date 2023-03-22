from commandlib import run
from hitchstory import StoryCollection, StorySchema, BaseEngine, exceptions
from commandlib import Command, python
from strictyaml import MapPattern, Str, Map, Int, Optional, load
from pathquery import pathquery
from hitchrunpy import ExamplePythonCode, ExpectedExceptionMessageWasDifferent
import requests


class Engine(BaseEngine):
    """Python engine for running tests."""
    schema = StorySchema(
        preconditions=Map({
            Optional("files"): MapPattern(Str(), Str()),
            Optional("setup"): Str(),
            Optional("code"): Str(),
            Optional("example1.py"): Str(),
            Optional("example2.py"): Str(),
            Optional("example3.py"): Str(),
            Optional("python version"): Str(),
        }),
        params=Map({
            Optional("python version"): Str(),
            Optional("exception reference"): Str(),
        }),
        about={
            Optional("description"): Str(),
            Optional("importance"): Int(),
        },
    )

    def __init__(self, keypath, settings):
        self.path = keypath
        self.settings = settings

    def set_up(self):
        """Set up your applications and the test environment."""
        self.doc = hitchdoc.Recorder(
            hitchdoc.HitchStory(self),
            self.path.gen.joinpath('storydb.sqlite'),
        )

        self.path.state = self.path.gen.joinpath("state")
        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        self.python_package = hitchpython.PythonPackage(
            self.preconditions['python version']
        )
        self.python_package.build()

        self.pip = self.python_package.cmd.pip
        self.python = self.python_package.cmd.python

        for filename in ["example1.py", "example2.py", "example3.py"]:
            if filename in self.preconditions:
                self.path.state.joinpath(filename).write_text(self.preconditions[filename])

        # Install debugging packages
        with hitchtest.monitor([self.path.key.joinpath("debugrequirements.txt")]) as changed:
            if changed:
                run(self.pip("install", "-r", "debugrequirements.txt").in_dir(self.path.key))

        # Uninstall and reinstall
        with hitchtest.monitor(
            pathq(self.path.project.joinpath("prettystack")).ext("py")
        ) as changed:
            if changed:
                run(self.pip("uninstall", "prettystack", "-y").ignore_errors())
                run(self.pip("install", ".").in_dir(self.path.project))

        self.example_py_code = ExamplePythonCode(self.preconditions.get('code', ''))\
            .with_setup_code(self.preconditions.get('setup', ''))\
            .with_long_strings(
                yaml_snippet=self.preconditions.get('yaml_snippet'),
                modified_yaml_snippet=self.preconditions.get('modified_yaml_snippet'),
            )

    def raises_exception(self, exception_type=None, message=None):
        """
        Expect an exception.
        """
        try:
            self.example_py_code.expect_exception(exception_type, message)\
                                .run(self.path.state, self.python)
        except ExpectedExceptionMessageWasDifferent as error:
            if self.settings.get("rewrite"):
                self.current_step.update(message=error.actual_message)
            else:
                raise

    def run_code(self):
        self.result = self.example_py_code.run(self.path.state, self.python)

    def output_will_be(self, reference, changeable=None):
        from simex import DefaultSimex
        output_contents = self.result.output.strip()

        artefact = self.path.key.joinpath(
            "artefacts", "{0}.txt".format(reference.replace(" ", "-").lower())
        )

        simex = DefaultSimex(
            open_delimeter="(((",
            close_delimeter=")))",
        )

        simex_contents = output_contents

        if changeable is not None:
            for replacement in changeable:
                simex_contents = simex.compile(replacement).sub(replacement, simex_contents)

        if not artefact.exists():
            artefact.write_text(simex_contents)
        else:
            if self.settings.get('overwrite artefacts'):
                artefact.write_text(simex_contents)
                self.services.log(output_contents)
            else:
                if simex.compile(artefact.bytes().decode('utf8')).match(output_contents) is None:
                    raise RuntimeError("Expected to find:\n{0}\n\nActual output:\n{1}".format(
                        artefact.bytes().decode('utf8'),
                        output_contents,
                    ))

    def pause(self, message="Pause"):
        import IPython
        IPython.embed()

    def on_success(self):
        """
        if self.settings.get("rewrite"):
            self.new_story.save()
        """
        pass


def _storybook(settings):
    return StoryCollection(pathq(DIR.key).ext("story"), Engine(DIR, settings))


@expected(exceptions.HitchStoryException)
def tdd(*words):
    """
    Run all tests
    """
    print(
        _storybook({"rewrite": True}).shortcut(*words).play().report()
    )


@expected(exceptions.HitchStoryException)
def testfile(filename):
    """
    Run all stories in filename 'filename'.
    """
    print(
        _storybook({"rewrite": True}).in_filename(filename).ordered_by_name().play().report()
    )


@expected(exceptions.HitchStoryException)
def regression():
    """
    Run regression testing - lint and then run all tests.
    """
    lint()
    print(
        _storybook({}).ordered_by_name().play().report()
    )


def lint():
    """
    Lint all code.
    """
    #python("-m", "flake8")(
        #DIR.project.joinpath("prettystack"),
        #"--max-line-length=100",
        #"--exclude=__init__.py",
    #).run()
    #python("-m", "flake8")(
        #DIR.key.joinpath("key.py"),
        #"--max-line-length=100",
        #"--exclude=__init__.py",
    #).run()
    #print("Lint success!")


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    NAME = "prettystack"
    git = Command("git").in_dir(DIR.project)
    version_file = DIR.project.joinpath("VERSION")
    old_version = version_file.bytes().decode('utf8')
    if version_file.bytes().decode("utf8") != version:
        DIR.project.joinpath("VERSION").write_text(version)
        git("add", "VERSION").run()
        git("commit", "-m", "RELEASE: Version {0} -> {1}".format(
            old_version,
            version
        )).run()
        git("push").run()
        git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
        git("push", "origin", version).run()
    else:
        git("push").run()

    # Set __version__ variable in __init__.py, build sdist and put it back
    initpy = DIR.project.joinpath(NAME, "__init__.py")
    original_initpy_contents = initpy.bytes().decode('utf8')
    initpy.write_text(
        original_initpy_contents.replace("DEVELOPMENT_VERSION", version)
    )
    python("setup.py", "sdist").in_dir(DIR.project).run()
    initpy.write_text(original_initpy_contents)

    # Upload to pypi
    python(
        "-m", "twine", "upload", "dist/{0}-{1}.tar.gz".format(NAME, version)
    ).in_dir(DIR.project).run()


def docgen():
    """
    Generate documentation.
    """
    docpath = DIR.project.joinpath("docs")

    if not docpath.exists():
        docpath.mkdir()

    documentation = hitchdoc.Documentation(
        DIR.gen.joinpath('storydb.sqlite'),
        'doctemplates.yml'
    )

    for story in documentation.stories:
        story.write(
            "rst",
            docpath.joinpath("{0}.rst".format(story.slug))
        )


@ignore_ctrlc
def ipy():
    """
    Run IPython in environment."
    """
    Command(DIR.gen.joinpath("py3.5.0", "bin", "ipython")).run()


def hvenvup(package, directory):
    """
    Install a new version of a package in the hitch venv.
    """
    pip = Command(DIR.gen.joinpath("hvenv", "bin", "pip"))
    pip("uninstall", package, "-y").run()
    pip("install", DIR.project.joinpath(directory).abspath()).run()
