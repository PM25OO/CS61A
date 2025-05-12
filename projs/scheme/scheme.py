"""A Scheme interpreter and its read-eval-print loop."""
"""一个 Scheme 解释器及其读取-求值-打印 循环（REPL）。"""

import sys
import os

sys.path.append("scheme_reader")

from scheme_classes import *
from scheme_forms import *
from scheme_eval_apply import *
from scheme_builtins import *
from scheme_reader import *
from ucb import main, trace



################
# Input/Output #
################
# 输入 / 输出

def read_eval_print_loop(next_line, env, interactive=False, quiet=False,
                         startup=False, load_files=(), report_errors=False):
    """Read and evaluate input until an end of file or keyboard interrupt."""
    """读取并求值输入，直到遇到文件结束符或键盘中断。"""
    if startup:
        for filename in load_files:
            scheme_load(filename, True, env)
    while True:
        try:
            src = next_line()
            while src.more_on_line():
                expression = scheme_read(src)
                result = scheme_eval(expression, env)
                if not quiet and result is not None:
                    print(repl_str(result))
        except (SchemeError, SyntaxError, ValueError, RuntimeError) as err:
            if report_errors:
                if isinstance(err, SyntaxError):
                    err = SchemeError(err)
                    raise err
            if (isinstance(err, RuntimeError) and
                'maximum recursion depth exceeded' not in getattr(err, 'args')[0]):
                raise
            elif isinstance(err, RuntimeError):
                print('Error: maximum recursion depth exceeded')
            else:
                print('Error:', err)
        except KeyboardInterrupt:  # <Control>-C
            # 键盘中断（如按下 Ctrl-C）
            if not startup:
                raise
            print()
            print('KeyboardInterrupt')
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            # 文件结束符（如按下 Ctrl-D 等）
            print()
            return

def add_builtins(frame, funcs_and_names):
    """Enter bindings in FUNCS_AND_NAMES into FRAME, an environment frame,
    as built-in procedures. Each item in FUNCS_AND_NAMES has the form
    (NAME, PYTHON-FUNCTION, INTERNAL-NAME)."""
    """将 FUNCS_AND_NAMES 中的绑定添加到 FRAME（环境帧）中，作为内建过程。
    每个 FUNCS_AND_NAMES 的项的格式为 (NAME, PYTHON 函数, 内部名称)。"""
    for name, py_func, proc_name, need_env in funcs_and_names:
        frame.define(name, BuiltinProcedure(py_func, name=proc_name, need_env=need_env))

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    """初始化并返回一个带有内建名称的单帧环境。"""
    env = Frame(None)
    env.define('eval',
               BuiltinProcedure(scheme_eval, True, 'eval'))
    env.define('apply',
               BuiltinProcedure(complete_apply, True, 'apply'))
    env.define('undefined', None)
    add_builtins(env, BUILTINS)
    return env

@main
def run(*argv):
    import argparse
    parser = argparse.ArgumentParser(description='CS 61A Scheme Interpreter')
    parser.add_argument('--pillow-turtle', action='store_true',
                        help='run with pillow-based turtle. This is much faster for rendering but there is no GUI')
    # 使用基于 pillow 的 turtle 渲染方式运行。渲染速度更快，但没有图形界面。
    parser.add_argument('--turtle-save-path', default=None,
                        help='save the image to this location when done')
    # 渲染完成后将图像保存到此位置。
    parser.add_argument('-load', '-i', action='store_true',
                        help='run file interactively')
    # 以交互模式运行文件。
    parser.add_argument('file', nargs='?',
                        type=argparse.FileType('r'), default=None,
                        help='Scheme file to run')
    # 要运行的 Scheme 文件。
    args = parser.parse_args()

    import builtins
    builtins.TK_TURTLE = not args.pillow_turtle
    builtins.TURTLE_SAVE_PATH = args.turtle_save_path
    sys.path.insert(0, '')

    next_line = buffer_input
    interactive = True
    load_files = []

    if args.file is not None:
        if args.load:
            load_files.append(getattr(args.file, 'name'))
        else:
            lines = args.file.readlines()
            def next_line():
                return buffer_lines(lines)
            interactive = False

    read_eval_print_loop(next_line, create_global_frame(), startup=True,
                         interactive=interactive, load_files=load_files)
    tscheme_exitonclick()
