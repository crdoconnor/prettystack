Only the exception:
  about:
    code: |
      from prettystack import PrettyStackTemplate
      from example1 import exception_raiser

      prettystack_template = PrettyStackTemplate().to_console().only_the_exception()

      try:
          exception_raiser()
      except Exception as exception:
          print(prettystack_template.current_stacktrace())
