import new

class wrap_attributes_in_dict(object):
    """This class decorator wrap each attribute of the decorated class
    in a dictionary in which the key used is the key specified to the
    decorator and the value is the value of the attribute.

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

    *args         -- if others dictionaries are passed as parameters,
                     they are appended to the wrapping dictionaries

    Keywords Arguments:
    depth         -- the depth to which this decorator is also applied
                     to nested classes, by default it is 0 which mean
                     that this decorator is not applied on nested
                     classes, -1 mean infinity
    """

    def __init__(self, key, *args, **kargs):
        self.key = key
        self.depth = kargs.get("depth", 0)
        self.args = args


    def __call__(self, cls):
        key = self.key
        depth = self.depth
        args = self.args
        class_dict = cls.__dict__

        for k, v in class_dict.iteritems():
            if not k.startswith("__"):
                type_of_attribute = type(v)
                # If the attribute is a class (old and new style)
                if (type_of_attribute is type
                        or type_of_attribute is new.classobj):
                    if depth != 0:
                        wrap_attributes_in_dict(key, *args, depth=depth-1)(v)
                else:
                    dt = {key : v}
                    for a in args:
                        dt.update(a)
                    class_dict[k] = dt

        return cls
