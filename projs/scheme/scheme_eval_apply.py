import sys

from pair import *
from scheme_utils import *
from ucb import main, trace

import scheme_forms

##############
# Eval/Apply #
##############
# 求值/应用

def scheme_eval(expr, env, _=None): # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.
    - 在环境 ENV 中求值 Scheme 表达式 EXPR。

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # Evaluate atoms
    # 对原子表达式求值
    if scheme_symbolp(expr):
        return env.lookup(expr)
    elif self_evaluating(expr):
        return expr

    # All non-atomic expressions are lists (combinations)
    # 所有非原子的表达式都是列表（组合）
    if not scheme_listp(expr):
        raise SchemeError('malformed list: {0}'.format(repl_str(expr)))
    first, rest = expr.first, expr.rest
    if scheme_symbolp(first) and first in scheme_forms.SPECIAL_FORMS:
        return scheme_forms.SPECIAL_FORMS[first](rest, env)
    else:
        # BEGIN PROBLEM 3
        "*** YOUR CODE HERE ***"
        procedure = scheme_eval(first, env)
        args = rest.map((lambda x : scheme_eval(x, env)))
        return scheme_apply(procedure, args, env)
        # END PROBLEM 3

def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment.
    - 在当前环境 Frame ENV 中，将 Scheme 过程 PROCEDURE 应用于参数值 ARGS（一个 Scheme 列表）。
    """
    validate_procedure(procedure)
    if not isinstance(env, Frame):
       assert False, "Not a Frame: {}".format(env)
    if isinstance(procedure, BuiltinProcedure):
        # BEGIN PROBLEM 2
        "*** YOUR CODE HERE ***"
        arg = []
        while (args != nil):
            arg.append(args.first)
            args = args.rest
        if procedure.need_env:
            arg.append(env)
        # END PROBLEM 2
        try:
            # BEGIN PROBLEM 2
            "*** YOUR CODE HERE ***"
            return procedure.py_func(*arg)
            # END PROBLEM 2
        except TypeError as err:
            raise SchemeError('incorrect number of arguments: {0}'.format(procedure))
    elif isinstance(procedure, LambdaProcedure):
        # BEGIN PROBLEM 9
        "*** YOUR CODE HERE ***"
        # END PROBLEM 9
    elif isinstance(procedure, MuProcedure):
        # BEGIN PROBLEM 11
        "*** YOUR CODE HERE ***"
        # END PROBLEM 11
    else:
        assert False, "Unexpected procedure: {}".format(procedure)

def eval_all(expressions, env):
    """Evaluate each expression in the Scheme list EXPRESSIONS in
    Frame ENV (the current environment) and return the value of the last.
    在当前环境 Frame ENV 中，对 Scheme 列表 EXPRESSIONS 中的每个表达式进行求值，并返回最后一个表达式的值。

    >>> eval_all(read_line("(1)"), create_global_frame())
    1
    >>> eval_all(read_line("(1 2)"), create_global_frame())
    2
    >>> x = eval_all(read_line("((print 1) 2)"), create_global_frame())
    1
    >>> x
    2
    >>> eval_all(read_line("((define x 2) x)"), create_global_frame())
    2
    """
    # BEGIN PROBLEM 6
    return scheme_eval(expressions.first, env) # replace this with lines of your own code
    # END PROBLEM 6


################################
# Extra Credit: Tail Recursion #
################################
# 附加加分项：尾递归优化

class Unevaluated:
    """An expression and an environment in which it is to be evaluated.
    一个表达式及其将要被求值的环境。
    """

    def __init__(self, expr, env):
        """Expression EXPR to be evaluated in Frame ENV.
        表达式 EXPR 将在 Frame ENV 中被求值。
        """
        self.expr = expr
        self.env = env

def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not an Unevaluated.
    在 env 环境中将 procedure 应用于 args；确保结果不是一个 Unevaluated 对象。
    """
    validate_procedure(procedure)
    val = scheme_apply(procedure, args, env)
    if isinstance(val, Unevaluated):
        return scheme_eval(val.expr, val.env)
    else:
        return val

def optimize_tail_calls(unoptimized_scheme_eval):
    """Return a properly tail recursive version of an eval function.
    返回一个经过适当尾递归优化的 eval 函数。
    """
    def optimized_eval(expr, env, tail=False):
        """Evaluate Scheme expression EXPR in Frame ENV. If TAIL,
        return an Unevaluated containing an expression for further evaluation.
        在环境 ENV 中求值 Scheme 表达式 EXPR。如果 tail 为 True，则返回一个包含该表达式用于后续求值的 Unevaluated 对象。
        """
        if tail and not scheme_symbolp(expr) and not self_evaluating(expr):
            return Unevaluated(expr, env)

        result = Unevaluated(expr, env)
        # BEGIN OPTIONAL PROBLEM 1
        "*** YOUR CODE HERE ***"
        # END OPTIONAL PROBLEM 1
    return optimized_eval

################################################################
# Uncomment the following line to apply tail call optimization #
################################################################
# 取消以下注释以启用尾调用优化
# scheme_eval = optimize_tail_calls(scheme_eval)
