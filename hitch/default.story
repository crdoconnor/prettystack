Default:
  based on: prettystack
  preconditions:
    example1.py: |
      class CatchThis(Exception):
          """
          Some kind of docstring
          """
          pass

      def exception_raiser():
          raise CatchThis("Some kind of message")

      def something_else():
          pass
    code: |
      from prettystack import PrettyStackTemplate
      from example1 import exception_raiser

      prettystack_template = PrettyStackTemplate().to_console()

      try:
          exception_raiser()
      except Exception as exception:
          print(prettystack_template.current_stacktrace())
  scenario:
  - Run code
  - Output will be:
      reference: (( exception reference ))
      changeable:
      - <ipython-input-((( anything )))>
      - /((( anything )))/example1.py
      - /((( anything )))/examplepythoncode.py
  params:
    exception reference: example exception
