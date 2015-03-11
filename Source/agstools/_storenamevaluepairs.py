import argparse

from ast import literal_eval

class StoreNameValuePairs(argparse.Action):
    """Simple argparse Action class for taking multiple string values in the form a=b and returning a dictionary.
    Literal values (i.e. booleans, numbers) will be converted to there appropriate Python types.
    On either side of the equals sign, double quotes can be used to contain a string that includes white space."""

    def __call__(self, parser, namespace, values, option_string = None):
        values_dict = {}
        for pair in values:
            k, v = pair.split("=")
            try:
                v = literal_eval(v)
            except SyntaxError:
                pass

            values_dict[k] = v

        setattr(namespace, self.dest, values_dict)