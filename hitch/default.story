Default:
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
    code: |
      from prettystack import PrettyStackTemplate
      from example1 import exception_raiser

      prettystack_template = PrettyStackTemplate().to_console()

      try:
          exception_raiser()
      except Exception as exception:
          print(prettystack_template.current_stacktrace())
  steps:
  - Run code
  - Output will be:
      will output: |-
        [0]: function 'runcode'                                                                                                                                         
          /gen/state/working/examplepythoncode.py                                                                                                                       
                                                                                                                                                                        
                                                                                                                                                                        
                59 :                                                                                                                                                    
                60 :             try:                                                                                                                                   
            --> 61 :                 exception_raiser()                                                                                                                 
                62 :             except Exception as exception:                                                                                                         
                                                                                                                                                                        
                                                                                                                                                                        
                                                                                                                                                                        
        [1]: function 'exception_raiser'                                                                                                                                
          /gen/state/working/example1.py                                                                                                                                
                                                                                                                                                                        
                                                                                                                                                                        
                5 :                                                                                                                                                     
                6 : def exception_raiser():                                                                                                                             
            --> 7 :     raise CatchThis("Some kind of message")                                                                                                         
                8 :                                                                                                                                                     
                                                                                                                                                                        
                                                                                                                                                                        
                                                                                                                                                                        
        example1.CatchThis                                                                                                                                              
                                                                                                                                                                        
            Some kind of docstring                                                                                                                                      
                                                                                                                                                                        
        Some kind of message
