PrettyStack
===========

Pretty stack traces:

.. code-block:: python

        from prettystack import PrettyStacktrace

        try:
            exception_raiser()
        except Exception as exception:
            output(PrettyStacktrace().to_console())

Output::

  <ipython-input-4-2d951494fd2a>

    

  [1]: function 'exception_raiser'
    /path/to/example1.py

      
          5 :
          6 : def exception_raiser():
      --> 7 :     raise CatchThis("Some kind of message")
          8 :
    
    

  example1.CatchThis
  
      Some kind of docstring
    
  Some kind of message
