import sys


def current_stack_trace_data():
    """
    Build a list of tracebacks from the last stack trace
    including line numbers and filenames.
    
    All the data needed to build a pretty stacktrace.
    """
    tb_id = 0
    _, exception, tb = sys.exc_info()
    
    if exception is None:
        return None

    # Create list of tracebacks
    tracebacks = []
    while tb is not None:
        filename = tb.tb_frame.f_code.co_filename
        if filename == '<frozen importlib._bootstrap>':
            break

        tracebacks.append({
            "tb_id": tb_id,
            "filename": tb.tb_frame.f_code.co_filename,
            "line": tb.tb_lineno,
            "function": tb.tb_frame.f_code.co_name,
        })
        
        tb_id = tb_id + 1
        tb = tb.tb_next
    
    return {
        "tracebacks": tracebacks,
        "exception_string": str(exception),
        "docstring": exception.__doc__ if exception.__doc__ is not None else None,
        "exception_type": "{}.{}".format(
            type(exception).__module__, type(exception).__name__
        ),
    }
