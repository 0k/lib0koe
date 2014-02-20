# -*- encoding: utf-8 -*-


class ElementNotFound(ValueError):
    pass


def get_index(l, predicate):
    """Returns the index of the first element matching predicate in list

    For example, here's how to get the first pair number in a list:

        >>> get_index([1, 3, 8, 7], lambda x: x % 2 == 0)
        2

    Please note that the function returns ``False``, if it doesn't find
    any element satisfying the predicate:

        >>> get_index([1, 3, 9, 7], lambda x: x % 2 == 0)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ElementNotFound: No value matching the predicate in list ...

    """
    for i, elt in enumerate(l):
        if predicate(elt):
            return i
    raise ElementNotFound("No value matching the predicate in list %r" % l)
