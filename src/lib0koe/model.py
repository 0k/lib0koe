# -*- encoding: utf-8 -*-
"""Various OpenERP model utils

Adding values in an existing fields.selection definition
--------------------------------------------------------

We can use ``edit_list`` and ``is_select_id`` in combination with the
overriding selection::

    _columns = {
        'state': fields.selection(edit_list(
            stock_picking._columns["state"].selection,
                [is_select_id('confirmed'), 'before', ('wait_delivery_delay', 'En attente validation fournisseur')]),
            "State",
            required=True),
    }



"""

from functools import wraps

from . import common


def edit_select(column, actions):
    """Returns given list modified with a sequence of specific actions

    Actions can replace, insert before or after a specific element. The target
    element is found thanks to callable predicate.

    Each actions is a tuple (predicate, action_type, element)

        >>> l = [1, 3, 5, 8, 8]
        >>> is_pair = lambda x: x % 2 == 0
        >>> is_nb = lambda nb: (lambda x: x == nb)
        >>> edit_list(l, [(is_pair, 'replace', 9), ])()
        [1, 3, 5, 9, 8]

    Note that only the first matching element will trigger the action.

        >>> edit_list(l, [(is_nb(3), 'before', 'x'), ])
        [1, 'x', 3, 5, 8, 8]
        >>> edit_list(l, [(is_nb(3), 'after', 'x'), ])
        [1, 3, 'x', 5, 8, 8]

    """
    def _selection(model, cr, uid, context):
        l = column.select.reify(cr, uid, model, column, context)
        return edit_list(l, actions)
    return _selection


def edit_list(l, actions):
    """Returns given list modified with a sequence of specific actions

    Actions can replace, insert before or after a specific element. The target
    element is found thanks to callable predicate.

    Each actions is a tuple (predicate, action_type, element)

        >>> l = [1, 3, 5, 8, 8]
        >>> is_pair = lambda x: x % 2 == 0
        >>> is_nb = lambda nb: (lambda x: x == nb)
        >>> edit_list(l, [(is_pair, 'replace', 9), ])()
        [1, 3, 5, 9, 8]

    Note that only the first matching element will trigger the action.

        >>> edit_list(l, [(is_nb(3), 'before', 'x'), ])
        [1, 'x', 3, 5, 8, 8]
        >>> edit_list(l, [(is_nb(3), 'after', 'x'), ])
        [1, 3, 'x', 5, 8, 8]

    """
    for predicate, action_type, element in actions:
        index = common.get_index(l, predicate)
        if action_type == "replace":
            stop = index
            cont = stop + 1
        if action_type == "before":
            stop = index
            cont = stop
        if action_type == "after":
            stop = index + 1
            cont = stop
        l = l[:stop] + [element] + l[cont:]
    return l


def is_select_id(identifier):
    """Returns a predicate matching selection tuples with given identifier

    It is meant to be used to generate a predicate for ``edit_list()``
    function, when used with openerp selection fields.

    """
    return lambda obj: obj[0] == identifier


def functionator(f):
    """Returns a callable adequate to be used as field.function

    Classical v6.0/v6.1/v7 openerp syntax would need heavy prototyped
    function::

        def _my_func(self, cr, uid, ids, field_name, arg, context=None):
            ...

    Often, these function would do the exact same things: get a 'browsable'
    object for each ids, then do some computations with each one, put back
    the value in a dictionary, and return the dictionary.

    Functionator aim to remove all this common part and can be used as a
    decorator.

    Prototype of function decorated with functionator become::

        def _my_func(obj):
            ...

    With ``obj`` one browsable record.

    Here's then a sample model using functionator::

        class Link(osv.osv):
            _name = 'my_name'

            @functionator
            def get_total(obj):
                return sum(line.price for line in obj.line_ids)

            _columns = {
                ...
                'total': fields.function(get_total, store=True,
                                         string='status', method=True,
                                         type=float)
                ...
            }

    """
    @wraps(f)
    def _wrap(self, cr, uid, ids, _field_name, _arg, context=None):
        res = {}
        for id in ids:
            obj = self.browse(cr, uid, id, context=context)
            res[id] = f(obj)
        return res
    return _wrap


def methodator(f):
    """Returns a callable adequate to be used as a method of OpenERP model

    Classical v6.0/v6.1/v7 openerp syntax would need heavy prototyped
    method::

        def my_method(self, cr, uid, ids, context=None):
            ...

    Often, these function would do the exact same things: refuse to act when
    more than 1 id in 'ids' parameter, get a 'browsable' for the given id,
    then do some computations with it and then return something.

    Methodator aim to remove all this common part and can be used as a
    decorator.

    Prototype of function decorated with methodator become::

        def my_method(obj):
            ...

    With ``obj`` one browsable record.

    Here's then a sample model using methodator::

        class Link(osv.osv):
            _name = 'my_name'

            @methodator
            def get_total(obj):
                return sum(line.price for line in obj.line_ids)

    """
    @wraps(f)
    def _wrap(self, cr, uid, ids, context):
        assert len(ids) == 1, "Only support one id"
        obj = self.browse(cr, uid, ids[0], context=context)
        return f(obj)
    return _wrap
