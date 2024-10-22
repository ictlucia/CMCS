import acm


def pprint(obj):
    """
    Pretty print FObject.
    """
    if obj is None:
        print(obj)
    else:
        for attrib in obj.Class().Attributes():
            getter = attrib.GetMethod()
            val = getter(obj)
            print(f'{attrib.Name()} = {val}')
