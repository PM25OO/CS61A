"""This module implements the built-in procedures of the Scheme language."""
"""本模块实现了Scheme语言的内置程序。"""

import math
import numbers
import operator
import sys

from pair import Pair, nil, repl_str
from scheme_reader import *
from scheme_eval_apply import *
from scheme_classes import *
from scheme_utils import *


#######################
# Built-In Procedures # 内置过程
#######################

# A list of triples (NAME, PYTHON-FUNCTION, INTERNAL-NAME).  Added to by
# builtin and used in scheme.create_global_frame.
# 一个三元组列表 (名称, PYTHON函数, 内部名称)。由 builtin 添加并用于 scheme.create_global_frame。
BUILTINS = []

def builtin(*names, need_env=False):
    """An annotation to convert a Python function into a BuiltinProcedure."""
    """一个将Python函数转换为BuiltinProcedure的注解。"""
    def add(py_func):
        for name in names:
            BUILTINS.append((name, py_func, names[0], need_env))
        return py_func
    return add

builtin("procedure?")(scheme_procedurep)
builtin("list?")(scheme_listp)
builtin("atom?")(scheme_atomp)
builtin("boolean?")(scheme_booleanp)
builtin("number?")(scheme_numberp)
builtin("symbol?")(scheme_symbolp)
builtin("string?")(scheme_stringp)
builtin("null?")(scheme_nullp)

@builtin("not")
def scheme_not(x):
    return not is_scheme_true(x)

@builtin("equal?")
def scheme_equalp(x, y):
    if scheme_pairp(x) and scheme_pairp(y):
        return scheme_equalp(x.first, y.first) and scheme_equalp(x.rest, y.rest)
    elif scheme_numberp(x) and scheme_numberp(y):
        return x == y
    else:
        return type(x) == type(y) and x == y


@builtin("eq?")
def scheme_eqp(x, y):
    if scheme_numberp(x) and scheme_numberp(y):
        return x == y
    elif scheme_symbolp(x) and scheme_symbolp(y):
        return x == y
    else:
        return x is y

@builtin("pair?")
def scheme_pairp(x):
    return type(x).__name__ == 'Pair'

@builtin("scheme-valid-cdr?")
def scheme_valid_cdrp(x):
    return scheme_pairp(x) or scheme_nullp(x) or scheme_promisep(x)

# Streams 流
@builtin("promise?")
def scheme_promisep(x):
    return type(x).__name__ == 'Promise'

@builtin("force")
def scheme_force(x):
    validate_type(x, scheme_promisep, 0, 'promise')
    return x.evaluate()

@builtin("cdr-stream")
def scheme_cdr_stream(x):
    validate_type(x, lambda x: scheme_pairp(x) and scheme_promisep(x.rest), 0, 'cdr-stream')
    return scheme_force(x.rest)

@builtin("length")
def scheme_length(x):
    validate_type(x, scheme_listp, 0, 'length')
    if x is nil:
        return 0
    return len(x)

@builtin("cons")
def scheme_cons(x, y):
    return Pair(x, y)

@builtin("car")
def scheme_car(x):
    validate_type(x, scheme_pairp, 0, 'car')
    return x.first

@builtin("cdr")
def scheme_cdr(x):
    validate_type(x, scheme_pairp, 0, 'cdr')
    return x.rest

# Mutation extras 可变操作补充
@builtin("set-car!")
def scheme_set_car(x, y):
    validate_type(x, scheme_pairp, 0, 'set-car!')
    x.first = y

@builtin("set-cdr!")
def scheme_set_cdr(x, y):
    validate_type(x, scheme_pairp, 0, 'set-cdr!')
    validate_type(y, scheme_valid_cdrp, 1, 'set-cdr!')
    x.rest = y

@builtin("list")
def scheme_list(*vals):
    result = nil
    for e in reversed(vals):
        result = Pair(e, result)
    return result

@builtin("append")
def scheme_append(*vals):
    if len(vals) == 0:
        return nil
    result = vals[-1]
    for i in range(len(vals)-2, -1, -1):
        v = vals[i]
        if v is not nil:
            validate_type(v, scheme_pairp, i, 'append')
            r = p = Pair(v.first, result)
            v = v.rest
            while scheme_pairp(v):
                p.rest = Pair(v.first, result)
                p = p.rest
                v = v.rest
            result = r
    return result

@builtin("integer?")
def scheme_integerp(x):
    return scheme_numberp(x) and (isinstance(x, numbers.Integral) or int(x) == x)

def _check_nums(*vals):
    """Check that all arguments in VALS are numbers."""
    """检查VALS中的所有参数是否都是数字。"""
    for i, v in enumerate(vals):
        if not scheme_numberp(v):
            msg = "operand {0} ({1}) is not a number"
            raise SchemeError(msg.format(i, v))

def _arith(fn, init, vals):
    """Perform the FN operation on the number values of VALS, with INIT as
    the value when VALS is empty. Returns the result as a Scheme value."""
    """对VALS的数值执行FN操作，当VALS为空时，INIT作为初始值。以Scheme值的形式返回结果。"""
    _check_nums(*vals)
    s = init
    for val in vals:
        s = fn(s, val)
    s = _ensure_int(s)
    return s

def _ensure_int(x):
    if int(x) == x:
        x = int(x)
    return x

@builtin("+")
def scheme_add(*vals):
    return _arith(operator.add, 0, vals)

@builtin("-")
def scheme_sub(val0, *vals):
    _check_nums(val0, *vals) # fixes off-by-one error 修复了差一错误
    if len(vals) == 0:
        return _ensure_int(-val0)
    return _arith(operator.sub, val0, vals)

@builtin("*")
def scheme_mul(*vals):
    return _arith(operator.mul, 1, vals)

@builtin("/")
def scheme_div(val0, *vals):
    _check_nums(val0, *vals) # fixes off-by-one error 修复了差一错误
    try:
        if len(vals) == 0:
            return _ensure_int(operator.truediv(1, val0))
        return _arith(operator.truediv, val0, vals)
    except ZeroDivisionError as err:
        raise SchemeError(err)

@builtin("expt")
def scheme_expt(val0, val1):
    _check_nums(val0, val1)
    return pow(val0, val1)

@builtin("abs")
def scheme_abs(val0):
    return abs(val0)

@builtin("quotient")
def scheme_quo(val0, val1):
    _check_nums(val0, val1)
    try:
        return -(-val0 // val1) if (val0 < 0) ^ (val1 < 0) else val0 // val1
    except ZeroDivisionError as err:
        raise SchemeError(err)

@builtin("modulo")
def scheme_modulo(val0, val1):
    _check_nums(val0, val1)
    try:
        return val0 % val1
    except ZeroDivisionError as err:
        raise SchemeError(err)

@builtin("remainder")
def scheme_remainder(val0, val1):
    _check_nums(val0, val1)
    try:
        result = val0 % val1
    except ZeroDivisionError as err:
        raise SchemeError(err)
    while result < 0 and val0 > 0 or result > 0 and val0 < 0:
        result -= val1
    return result

def number_fn(module, name, fallback=None):
    """A Scheme built-in procedure that calls the numeric Python function named
    MODULE.FN."""
    """一个Scheme内置过程，调用名为MODULE.FN的数字Python函数。"""
    py_fn = getattr(module, name) if fallback is None else getattr(module, name, fallback)
    def scheme_fn(*vals):
        _check_nums(*vals)
        return py_fn(*vals)
    return scheme_fn

# Add number functions in the math module as built-in procedures in Scheme
# 将math模块中的数字函数添加为Scheme中的内置过程
for _name in ["acos", "acosh", "asin", "asinh", "atan", "atan2", "atanh",
              "ceil", "copysign", "cos", "cosh", "degrees", "floor", "log",
              "log10", "log1p", "radians", "sin", "sinh", "sqrt",
              "tan", "tanh", "trunc"]:
    builtin(_name)(number_fn(math, _name))
builtin("log2")(number_fn(math, "log2", lambda x: math.log(x, 2)))  # Python 2 compatibility Python 2 兼容性

def _numcomp(op, x, y):
    _check_nums(x, y)
    return op(x, y)

@builtin("=")
def scheme_eq(x, y):
    return _numcomp(operator.eq, x, y)

@builtin("<")
def scheme_lt(x, y):
    return _numcomp(operator.lt, x, y)

@builtin(">")
def scheme_gt(x, y):
    return _numcomp(operator.gt, x, y)

@builtin("<=")
def scheme_le(x, y):
    return _numcomp(operator.le, x, y)

@builtin(">=")
def scheme_ge(x, y):
    return _numcomp(operator.ge, x, y)

@builtin("even?")
def scheme_evenp(x):
    _check_nums(x)
    return x % 2 == 0

@builtin("odd?")
def scheme_oddp(x):
    _check_nums(x)
    return x % 2 == 1

@builtin("zero?")
def scheme_zerop(x):
    _check_nums(x)
    return x == 0

##
## Other operations 其他操作
##

@builtin("display")
def scheme_display(*vals):
    vals = [repl_str(val[1:-1] if scheme_stringp(val) else val) for val in vals]
    print(*vals, end="")

@builtin("print")
def scheme_print(*vals):
    vals = [repl_str(val) for val in vals]
    print(*vals)

@builtin("displayln")
def scheme_displayln(*vals):
    scheme_display(*vals)
    scheme_newline()

@builtin("newline")
def scheme_newline():
    print()
    sys.stdout.flush()

@builtin("error")
def scheme_error(msg=None):
    msg = "" if msg is None else repl_str(msg)
    raise SchemeError(msg)

@builtin("exit")
def scheme_exit():
    raise EOFError

@builtin("map", need_env=True)
def scheme_map(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'map')
    validate_type(s, scheme_listp, 1, 'map')
    return s.map(lambda x: complete_apply(fn, Pair(x, nil), env))

@builtin("filter", need_env=True)
def scheme_filter(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'filter')
    validate_type(s, scheme_listp, 1, 'filter')
    head, current = nil, nil
    while s is not nil:
        item, s = s.first, s.rest
        if complete_apply(fn, Pair(item, nil), env):
            if head is nil:
                head = Pair(item, nil)
                current = head
            else:
                current.rest = Pair(item, nil)
                current = current.rest
    return head

@builtin("reduce", need_env=True)
def scheme_reduce(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'reduce')
    validate_type(s, lambda x: x is not nil, 1, 'reduce')
    validate_type(s, scheme_listp, 1, 'reduce')
    value, s = s.first, s.rest
    while s is not nil:
        value = complete_apply(fn, scheme_list(value, s.first), env)
        s = s.rest
    return value

@builtin("load", need_env=True)
def scheme_load(*args):
    """Load a Scheme source file. ARGS should be of the form (SYM, ENV) or
    (SYM, QUIET, ENV). The file named SYM is loaded into Frame ENV,
    with verbosity determined by QUIET (default true)."""
    """加载一个Scheme源文件。ARGS应该是(SYM, ENV)或(SYM, QUIET, ENV)的形式。
    名为SYM的文件被加载到Frame ENV中，详细程度由QUIET确定（默认为true）。"""
    if not (2 <= len(args) <= 3):
        expressions = args[:-1]
        raise SchemeError('"load" given incorrect number of arguments: '
                          '{0}'.format(len(expressions)))
    sym = args[0]
    quiet = args[1] if len(args) > 2 else True
    env = args[-1]
    if (scheme_stringp(sym)):
        sym = eval(sym)
    validate_type(sym, scheme_symbolp, 0, 'load')
    with scheme_open(sym) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines,)
    def next_line():
        return buffer_lines(*args)

    from scheme import read_eval_print_loop
    read_eval_print_loop(next_line, env, quiet=quiet, report_errors=True)

@builtin("load-all", need_env=True)
def scheme_load_all(directory, env):
    """
    Loads all .scm files in the given directory, alphabetically. Used only
        in tests/ code.
    """
    """
    按字母顺序加载给定目录中的所有.scm文件。仅在 tests/ 代码中使用。
    """
    assert scheme_stringp(directory)
    directory = directory[1:-1]
    import os
    for x in sorted(os.listdir(".")):
        if not x.endswith(".scm"):
            continue
        scheme_load(x, env)

def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise an error."""
    """如果FILENAME或FILENAME.scm是有效文件的名称，则返回打开该文件的Python文件对象。否则，引发错误。"""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))


##
## Turtle graphics (non-standard) 海龟绘图 (非标准)
##

turtle = CANVAS = None

def _title():
    import turtle as _nativeturtle
    _nativeturtle.title("Scheme Turtles")

def attempt_install_tk_turtle():
    try:
        from abstract_turtle import turtle
    except ImportError:
        raise SchemeError("Could not find abstract_turtle. This should never happen in student-facing situations. If you are a student, please file a bug on Piazza.")
        # 无法找到 abstract_turtle。这在面向学生的情况下不应该发生。如果您是学生，请在 Piazza 上提交错误报告。
    return turtle

def attempt_create_tk_canvas():
    try:
        import tkinter as _
    except:
        raise SchemeError("\n".join([
            "Could not import tkinter, so the tk-turtle will not work.", # 无法导入 tkinter，因此 tk-turtle 将无法工作。
            "Either install python with tkinter support or run in pillow-turtle mode" # 请安装支持 tkinter 的 python 或以 pillow-turtle 模式运行
        ]))
    from abstract_turtle import TkCanvas
    return TkCanvas(1000, 1000, init_hook=_title)

def attempt_create_pillow_canvas():
    try:
        import PIL as _
        import numpy as _
    except:
        raise SchemeError("\n".join([
            "Could not import abstract_turtle[pillow_canvas]'s dependencies.", # 无法导入 abstract_turtle[pillow_canvas] 的依赖项。
            "To install these packages, run", # 要安装这些包，请运行
            "    python3 -m pip install 'abstract_turtle[pillow_canvas]'",
            "You can also run in tk-turtle mode by removing the flag `--pillow-turtle`" # 您也可以通过删除 `--pillow-turtle` 标志以 tk-turtle 模式运行
        ]))
    from abstract_turtle import PillowCanvas
    return PillowCanvas(1000, 1000)

def _tscheme_prep():
    global turtle, CANVAS
    if turtle is not None:
        return
    _turtle = attempt_install_tk_turtle()
    if builtins.TK_TURTLE:
        try:
            _CANVAS = attempt_create_tk_canvas()
        except SchemeError as e:
            print(e, file=sys.stderr)
            print("Attempting pillow canvas mode", file=sys.stderr) # 尝试 pillow 画布模式
            _CANVAS = attempt_create_pillow_canvas()
    else:
        _CANVAS = attempt_create_pillow_canvas()
    turtle, CANVAS = _turtle, _CANVAS
    turtle.set_canvas(CANVAS)
    turtle.mode("logo")


@builtin("forward", "fd")
def tscheme_forward(n):
    """Move the turtle forward a distance N units on the current heading."""
    """使海龟沿当前方向前进N个单位。"""
    _check_nums(n)
    _tscheme_prep()
    turtle.forward(n)

@builtin("backward", "back", "bk")
def tscheme_backward(n):
    """Move the turtle backward a distance N units on the current heading,
    without changing direction."""
    """使海龟沿当前方向向后移动N个单位，不改变方向。"""
    _check_nums(n)
    _tscheme_prep()
    turtle.backward(n)

@builtin("left", "lt")
def tscheme_left(n):
    """Rotate the turtle's heading N degrees counterclockwise."""
    """将海龟的朝向逆时针旋转N度。"""
    _check_nums(n)
    _tscheme_prep()
    turtle.left(n)

@builtin("right", "rt")
def tscheme_right(n):
    """Rotate the turtle's heading N degrees clockwise."""
    """将海龟的朝向顺时针旋转N度。"""
    _check_nums(n)
    _tscheme_prep()
    turtle.right(n)

@builtin("circle")
def tscheme_circle(r, extent=None):
    """Draw a circle with center R units to the left of the turtle (i.e.,
    right if N is negative.  If EXTENT is not None, then draw EXTENT degrees
    of the circle only.  Draws in the clockwise direction if R is negative,
    and otherwise counterclockwise, leaving the turtle facing along the
    arc at its end."""
    """以海龟左侧R个单位为圆心绘制一个圆（即，如果N为负，则为右侧）。
    如果EXTENT不为None，则仅绘制圆的EXTENT度。
    如果R为负，则按顺时针方向绘制，否则按逆时针方向绘制，最终使海龟朝向圆弧的末端。"""
    if extent is None:
        _check_nums(r)
    else:
        _check_nums(r, extent)
    _tscheme_prep()
    turtle.circle(r, extent and extent)

@builtin("setposition", "setpos", "goto")
def tscheme_setposition(x, y):
    """Set turtle's position to (X,Y), heading unchanged."""
    """将海龟的位置设置为(X,Y)，朝向不变。"""
    _check_nums(x, y)
    _tscheme_prep()
    turtle.setposition(x, y)

@builtin("setheading", "seth")
def tscheme_setheading(h):
    """Set the turtle's heading H degrees clockwise from north (up)."""
    """将海龟的朝向设置为从北方（向上）顺时针旋转H度。"""
    _check_nums(h)
    _tscheme_prep()
    turtle.setheading(h)

@builtin("penup", "pu")
def tscheme_penup():
    """Raise the pen, so that the turtle does not draw."""
    """抬起画笔，使海龟不绘制。"""
    _tscheme_prep()
    turtle.penup()

@builtin("pendown", "pd")
def tscheme_pendown():
    """Lower the pen, so that the turtle starts drawing."""
    """放下画笔，使海龟开始绘制。"""
    _tscheme_prep()
    turtle.pendown()

@builtin("showturtle", "st")
def tscheme_showturtle():
    """Make turtle visible."""
    """使海龟可见。"""
    _tscheme_prep()
    turtle.showturtle()

@builtin("hideturtle", "ht")
def tscheme_hideturtle():
    """Make turtle visible."""
    """使海龟可见。""" # 注释原文有误，应为使海龟不可见
    _tscheme_prep()
    turtle.hideturtle()

@builtin("clear")
def tscheme_clear():
    """Clear the drawing, leaving the turtle unchanged."""
    """清除绘图，海龟状态不变。"""
    _tscheme_prep()
    turtle.clear()

@builtin("color")
def tscheme_color(c):
    """Set the color to C, a string such as '"red"' or '"#ffc0c0"' (representing
    hexadecimal red, green, and blue values."""
    """将颜色设置为C，一个字符串，例如'"red"'或'"#ffc0c0"'（表示十六进制的红、绿、蓝值）。"""
    _tscheme_prep()
    validate_type(c, scheme_stringp, 0, "color")
    turtle.color(eval(c))

@builtin("rgb")
def tscheme_rgb(red, green, blue):
    """Return a color from RED, GREEN, and BLUE values from 0 to 1."""
    """根据0到1之间的RED、GREEN和BLUE值返回一种颜色。"""
    colors = (red, green, blue)
    for x in colors:
        if x < 0 or x > 1:
            raise SchemeError("Illegal color intensity in " + repl_str(colors)) # 非法的颜色强度
    scaled = tuple(int(x*255) for x in colors)
    return '"#%02x%02x%02x"' % scaled

@builtin("begin_fill")
def tscheme_begin_fill():
    """Start a sequence of moves that outline a shape to be filled."""
    """开始一系列勾勒待填充形状的移动。"""
    _tscheme_prep()
    turtle.begin_fill()

@builtin("end_fill")
def tscheme_end_fill():
    """Fill in shape drawn since last begin_fill."""
    """填充自上次begin_fill以来绘制的形状。"""
    _tscheme_prep()
    turtle.end_fill()

@builtin("bgcolor")
def tscheme_bgcolor(c):
    _tscheme_prep()
    validate_type(c, scheme_stringp, 0, "bgcolor")
    turtle.bgcolor(eval(c))

@builtin("exitonclick")
def tscheme_exitonclick():
    global turtle
    """Wait for a click on the turtle window, and then close it."""
    """等待点击海龟窗口，然后关闭它。"""
    if turtle is None:
        return
    _tscheme_prep()
    # BEGIN SOLUTION NO PROMPT ALT="if _turtle_screen_on:"
    # 开始解决方案 无提示 ALT="if _turtle_screen_on:"
    if builtins.TK_TURTLE:
        print("Close or click on turtle window to complete exit") # 关闭或点击海龟窗口以完成退出
    if builtins.TURTLE_SAVE_PATH is not None:
        _save(builtins.TURTLE_SAVE_PATH)
    turtle.exitonclick()
    turtle = None

@builtin("speed")
def tscheme_speed(s):
    """Set the turtle's animation speed as indicated by S (an integer in
    0-10, with 0 indicating no animation (lines draw instantly), and 1-10
    indicating faster and faster movement."""
    """设置海龟的动画速度，由S表示（一个0-10之间的整数，0表示无动画（线条立即绘制），1-10表示越来越快的移动）。"""
    validate_type(s, scheme_integerp, 0, "speed")
    _tscheme_prep()
    turtle.speed(s)

@builtin("pixel")
def tscheme_pixel(x, y, c):
    """Draw a filled box of pixels (default 1 pixel) at (X, Y) in color C."""
    """在(X, Y)处以颜色C绘制一个填充的像素框（默认为1像素）。"""
    validate_type(c, scheme_stringp, 0, "pixel")
    color = c[1:-1]
    _tscheme_prep()
    turtle.pixel(x, y, color)

@builtin("pixelsize")
def tscheme_pixelsize(size):
    """Change pixel size to SIZE."""
    """将像素大小更改为SIZE。"""
    _check_nums(size)
    _tscheme_prep()
    turtle.pixel_size(size)

@builtin("screen_width")
def tscheme_screen_width():
    """Screen width in pixels of the current size (default 1)."""
    """当前尺寸的屏幕宽度（以像素为单位）（默认为1）。"""
    _tscheme_prep()
    return turtle.canvas_width()

@builtin("screen_height")
def tscheme_screen_height():
    """Screen height in pixels of the current size (default 1)."""
    """当前尺寸的屏幕高度（以像素为单位）（默认为1）。"""
    _tscheme_prep()
    return turtle.canvas_height()

def _save(path):
    if not builtins.TK_TURTLE:
        path = path + ".png"
        CANVAS.export().save(path, "png")
    else:
        CANVAS.export(path + ".ps")

@builtin("save-to-file")
def tscheme_write_to_file(path):
    _tscheme_prep()
    validate_type(path, scheme_stringp, 0, "save-to-file")
    path = eval(path)
    _save(path)

@builtin("print-then-return")
def scheme_print_return(val1, val2):
    print(repl_str(val1))
    return val2