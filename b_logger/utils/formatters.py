def format_exc(exc):
    exc = str(exc).partition('Stacktrace')[0]
    return exc


def format_tb(tb):
    tb = ('\n' +
          str(tb)
          .partition('Stacktrace')[0]
          + '\n')
    return tb
