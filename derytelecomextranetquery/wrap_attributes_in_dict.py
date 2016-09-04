class wrap_attributes_in_dict(object):
    """This class decorator wrap each attribute of the decorated class in
    a dictionary in which the key used is the key specified to the decorator and
    the value is the value of the attribute.

    For example, the following two class definition are equivalent:
        @wrap_attributes_in_dict("lang")
        class LANG:
            FRA = "fra"
            ENG = "eng"

        class LANG:
            FRA = {"lang" : "fra"}
            ENG = {"lang" : "eng"}


    Arguments:
    key           -- the key to use in the wrapping dictionaries

    *args         -- if others dictionaries are passed as parameters, they are
                     appended to the wrapping dictionaries

    **kargs       -- dictionaries to append can also be passed as keywords
                     arguments
    """

    def __init__(self, key, *args, **kargs):
        self.key = key
        self.args = args
        self.kargs = kargs

    def __call__(self, cls):
        class_dict = cls.__dict__

        for k, v in class_dict.iteritems():
            if not k.startswith("__"):
                dt = {self.key : v}
                for a in self.args:
                    dt.update(a)
                dt.update(self.kargs)
                class_dict[k] = dt

        return cls
