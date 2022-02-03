from __future__ import print_function

import collections
import json
import os.path
import re
import sys
import subprocess
from parse_path import ParsePath, ParsedPath

# {{{1 全局变量
import vim
current_file = vim.eval("expand('%:p')")
# }}}



class FakeLogger(object):
    def __init__(self, active=False):
        self.active = active

    def info(self, fmt, *args):
        if not self.active:
            return

        print(fmt % args)


_logger = FakeLogger()


def plugin_entry_point():
    import vim

    if int(vim.eval("exists('g:mdnav#Extensions')")):
        extensions = vim.eval('g:mdnav#Extensions')

    else:
        extensions = []

    if int(vim.eval("exists('g:mdnav#DebugMode')")):
        _logger.active = vim.eval('g:mdnav#DebugMode') == 'true'

    row, col = vim.current.window.cursor
    cursor = (row - 1, col) # -1的原因是, 行号是从1开始, 但是取当前行, 从0开始
    lines = vim.current.buffer

    target = parse_link(cursor, lines) # 返回了[]()中()中的内容
    _logger.info('open %s', target)
    action = open_link(
        target,
        current_file=vim.eval("expand('%:p')"),
    ) # 返回是类的实例, 比如JumpToAnchor
    if(action):
        action() # 跳转动作


# {{{ 入口, target是target
def open_link(target, current_file):
    """
    :returns: a callable that encapsulates the action to perform
    """

    if target is not None:
        target = target.strip()

    if not target:
        _logger.info('no target')
        # return NoOp(target)

        return None
    parsed_path = ParsePath(current_file).parse_path(target)
    if(parsed_path.os_open):
        return OSOpen(parsed_path.path)
    elif(parsed_path.internal):
        return JumpToAnchor(parsed_path)
    else:
        return VimOpen(parsed_path) # 跨文件, 且用vim打开的文件走这里


class Action(object):
    '''仅仅是保存了target, 类型: ParsedPath'''
    def __init__(self, target):
        self.target = target

    def __eq__(self, other):
        return type(self) == type(other) and self.target == other.target

    def __repr__(self):
        return '{}({!r})'.format(type(self).__name__, self.target)



class OSOpen(Action):
    def __call__(self):
        if sys.platform.startswith('linux'):
            call(['xdg-open', self.target])

        elif sys.platform.startswith('darwin'):
            call(['open', self.target])

        else:
            os.startfile(self.target)


# {{{1 VimOpen: input: [[]]的内容, 跨文件, vim处理的情况
class VimOpen(Action):
    '''这个类负责打开文件, 如果有line number, 再跳到指定line number, 文件有可能没有后缀'''
    def __call__(self):
        import vim

        vim.command('e {}'.format(self.target.path.replace(' ', '\\ '))) # highlight 这一步就在vim中打开了文件
        if self.target.line:
            vim.current.window.cursor = (self.target.line, 0) # highlight 控制cursor到指定行

        if self.target.anchor is not None:
            JumpToAnchor(self.target)() #? JumpToAnchor没有__init__方法, 那么如何接受参数?


class JumpToAnchor(Action):
    '''这个类负责跳到anchor, target存的是anchor, 这里的target包括^'''
    # attr_list_pattern = re.compile(r'\^(?P<id>\w+)')

    def __call__(self):
        import vim
        line = self.find_anchor(self.target.anchor, vim.current.buffer)

        if line is None:
            return

        vim.current.window.cursor = (line + 1, 0) #highlight 设置line

    @classmethod
    def find_anchor(cls, target, buffer):
        ''''''
        # 思路就是遍历每一行, 先检查这一行是不是header, 如果是, 把title格式化, 看是不是相等, 对anchor也同样如此
        for (idx, line) in enumerate(buffer):
            if(line.endswith(target)):
                return idx

def call(args):
    """If available use vims shell mechanism to work around display issues
    """
    try:
        import vim

    except ImportError:
        subprocess.call(args)

    else:
        args = ['shellescape(' + json.dumps(arg) + ')' for arg in args]
        vim.command('execute "! " . ' + ' . " " . '.join(args))



def parse_link(cursor, lines):
    '''返回[[]]中的内容'''
    row, column = cursor # row从1开始, column从0开始
    line = lines[row] # 这才获得了当前行
    start_pos = -1
    end_pos = -1
    if(line[column]=='['):
        if(column+1 >= 0 and line[column+1]=='['):
            start_pos = column+2
        elif(column-1 >=0 and line[column-1]=='['):
            start_pos = column+1
        end_pos = line.find(']]', start_pos)
        if start_pos >= 0 and end_pos >= 0:
            return line[start_pos:end_pos]
    elif(line[column]==']'):
        if(column-1 >=0 and line[column-1]==']'):
            end_pos = column - 1
        elif(column+1 >=0 and line[column+1]==']'):
            end_pos = column
        start_pos = line.rfind('[[', 0, end_pos)
        if start_pos >= 0 and end_pos >= 0:
            return line[(start_pos+2):end_pos]
    else:
        start_pos = line.rfind('[[')
        end_pos = line.find(']]')
        if start_pos >= 0 and end_pos >= 0:
            return line[(start_pos+2):end_pos]
    return None
        

    # _logger.info('handle line %s (%s, %s)', line, row, column)
    # m = reference_definition_pattern.match(line) # 这好像没什么关系
    # if m is not None:
    #     return m.group('link').strip()


if __name__ == "__main__":
    plugin_entry_point()

