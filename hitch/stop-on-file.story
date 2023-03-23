Stop on file:
  about: |
    You can intentionally ignore lines in the traceback which
    occur up or down the stack.
  given:
    files:
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
      example2.py: |
        from example1 import exception_raiser

        def another_exception_raiser():
            exception_raiser()
      example3.py: |
        from example2 import another_exception_raiser

        def yet_another_exception_raiser():
            another_exception_raiser()

        def yet_yet_another_exception_raiser():
            yet_another_exception_raiser()
    code: |
      from prettystack import PrettyStackTemplate
      from example3 import yet_yet_another_exception_raiser

      prettystack_template1 = PrettyStackTemplate().cut_calling_code("example3.py").to_console()

      try:
          yet_yet_another_exception_raiser()
      except Exception as exception:
          print(prettystack_template1.current_stacktrace())
  steps:
  - Run code
  - Output will be:
      will output: |-
        [3]: function 'another_exception_raiser'                                                                                                                        
          /gen/state/working/example2.py                                                                                                                                
                                                                                                                                                                        
                                                                                                                                                                        
                1 :                                                                                                                                                     
                2 : def another_exception_raiser():                                                                                                                     
            --> 3 :     exception_raiser()                                                                                                                              
                4 :                                                                                                                                                     
                                                                                                                                                                        
                                                                                                                                                                        
                                                                                                                                                                        
        [4]: function 'exception_raiser'                                                                                                                                
          /gen/state/working/example1.py                                                                                                                                
                                                                                                                                                                        
                                                                                                                                                                        
                5 :                                                                                                                                                     
                6 : def exception_raiser():                                                                                                                             
            --> 7 :     raise CatchThis("Some kind of message")                                                                                                         
                8 :                                                                                                                                                     
                                                                                                                                                                        
                                                                                                                                                                        
                                                                                                                                                                        
        example1.CatchThis                                                                                                                                              
                                                                                                                                                                        
            Some kind of docstring                                                                                                                                      
                                                                                                                                                                        
        Some kind of message


    #- Run command: |
        #from prettystack import PrettyStackTemplate
        #from example3 import yet_another_exception_raiser

        #prettystack_template2 = PrettyStackTemplate().cut_calling_code_until("example1.py", including=True).to_console()

        #try:
            #yet_another_exception_raiser()
        #except Exception as exception:
            #output(prettystack_template2.current_stacktrace())
    #- Output will be:
        #reference: skip bottom line
        #changeable:
          #- <ipython-input-((( anything )))>
          #- /((( anything )))/example2.py
          #- /((( anything )))/example3.py

    #- Run command: |
        #from prettystack import PrettyStackTemplate
        #from example3 import yet_another_exception_raiser

        #prettystack_template3 = PrettyStackTemplate().cut_bottom_off_including("example3.py").to_console()

        #try:
            #yet_another_exception_raiser()
        #except Exception as exception:
            #output(prettystack_template3.current_stacktrace())
    #- Output will be:
        #reference: cut bottom off including
        #changeable:
          #- /((( anything )))/example1.py
          #- /((( anything )))/example2.py

    #- Run command: |
        #from prettystack import PrettyStackTemplate
        #from example3 import yet_another_exception_raiser

        #prettystack_template4 = PrettyStackTemplate().cut_bottom_off_until("example3.py").to_console()

        #try:
            #yet_another_exception_raiser()
        #except Exception as exception:
            #output(prettystack_template4.current_stacktrace())
    #- Output will be:
        #reference: cut bottom off until
        #changeable:
          #- /((( anything )))/example1.py
          #- /((( anything )))/example2.py
