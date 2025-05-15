import numbers

from scheme_classes import *

#################
# Type Checking #
# 类型检查部分  #
#################

def scheme_procedurep(x):
    return isinstance(x, Procedure)

def scheme_listp(x):
    """Return whether x is a well-formed list. Assumes no cycles.
    - 判断 x 是否是一个格式正确的列表。假设无循环结构。
    """
    while x is not nil:
        if not isinstance(x, Pair):
            return False
        x = x.rest
    return True

def scheme_booleanp(x):
    return x is True or x is False

def scheme_numberp(x):
    return isinstance(x, numbers.Real) and not scheme_booleanp(x)

def is_scheme_true(val):
    """All values in Scheme are true except False.
    - 在 Scheme 中，除了 False，所有值都为真。
    """
    return val is not False

def is_scheme_false(val):
    """Only False is false in scheme_reader.
    - 在 scheme_reader 中，只有 False 为假。
    """
    return val is False

def scheme_stringp(x):
    return isinstance(x, str) and x.startswith('"')

def scheme_symbolp(x):
    return isinstance(x, str) and not scheme_stringp(x)

def scheme_nullp(x):
    return type(x).__name__ == 'nil'

def scheme_atomp(x):
    return (scheme_booleanp(x) or scheme_numberp(x) or scheme_symbolp(x) or
            scheme_nullp(x) or scheme_stringp(x))

def self_evaluating(expr):
    """Return whether EXPR evaluates to itself.
    - 判断 EXPR 是否是自求值的表达式。
    """
    return (scheme_atomp(expr) and not scheme_symbolp(expr)) or expr is None


#######################
# Argument Validation #
# 参数合法性验证部分  #
#######################

def validate_type(val, predicate, k, name):
    """Returns VAL.  Raises a SchemeError if not PREDICATE(VAL)
    using "argument K of NAME" to describe the offending value.
    - 返回 VAL。如果 PREDICATE(VAL) 为假，则抛出 SchemeError，
    并使用“NAME 的第 K 个参数”来描述出错的值。
    """
    if not predicate(val):
        msg = "argument {0} of {1} has wrong type ({2})"
        type_name = type(val).__name__
        if scheme_symbolp(val):
            type_name = "symbol"
        raise SchemeError(msg.format(k, name, type_name))
    return val

def validate_procedure(procedure):
    """Check that PROCEDURE is a valid Scheme procedure.
    - 检查 PROCEDURE 是否是一个合法的 Scheme 过程。
    """
    if not scheme_procedurep(procedure):
        raise SchemeError('{0} is not callable: {1}'.format(
            type(procedure).__name__.lower(), repl_str(procedure)))

def validate_form(expr, min, max=float('inf')):
    """Check EXPR is a proper list whose length is at least MIN and no more
    than MAX (default: no maximum). Raises a SchemeError if this is not the
    case.
    - 检查 EXPR 是否是一个格式正确的列表，其长度不少于 MIN，
    且不超过 MAX（默认无限）。如果不符合条件，则抛出 SchemeError。
    
    >>> validate_form(read_line('(a b)'), 2)
    """
    if not scheme_listp(expr):
        raise SchemeError('badly formed expression: ' + repl_str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError('too few operands in form')
    elif length > max:
        raise SchemeError('too many operands in form')

def validate_formals(formals):
    """Check that FORMALS is a valid parameter list, a Scheme list of symbols
    in which each symbol is distinct. Raise a SchemeError if the list of
    formals is not a list of symbols or if any symbol is repeated.
    - 检查 FORMALS 是否是一个合法的参数列表，即一个由符号组成的 Scheme 列表，
    - 且每个符号都不重复。如果不是符号列表或有重复符号，则抛出 SchemeError。
    
    >>> validate_formals(read_line('(a b c)'))
    """
    symbols = set()
    def validate_and_add(symbol, is_last):
        if not scheme_symbolp(symbol):
            raise SchemeError('non-symbol: {0}'.format(symbol))
        if symbol in symbols:
            raise SchemeError('duplicate symbol: {0}'.format(symbol))
        symbols.add(symbol)

    while isinstance(formals, Pair):
        validate_and_add(formals.first, formals.rest is nil)
        formals = formals.rest
