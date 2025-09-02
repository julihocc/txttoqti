class TxtToQtiError(Exception):
    """Base class for exceptions in the txttoqti package."""
    pass

class ParseError(TxtToQtiError):
    """Exception raised for errors in parsing questions."""
    pass

class ValidationError(TxtToQtiError):
    """Exception raised for validation errors in questions."""
    pass

class ConversionError(TxtToQtiError):
    """Exception raised for errors during conversion to QTI."""
    pass