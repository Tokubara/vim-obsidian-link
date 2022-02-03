from __future__ import print_function

import collections
import json
import os.path
import re
import sys
import subprocess
import webbrowser

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


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
        open_in_os_extensions=extensions,
    ) # 返回是类的实例, 比如JumpToAnchor
    action() # 跳转动作


def open_link(target, current_file, open_in_os_extensions=set()):
    """
    :returns: a callable that encapsulates the action to perform
    """
    if target is not None:
        target = target.strip()

    if not target:
        _logger.info('no target')
        return NoOp(target)

    if target.startswith('#^'): # 这是heading inside的情况
        return JumpToAnchor(target[1:])

    if target.startswith('#'): # 这是heading inside的情况
        return JumpToAnchor("# " + target[1:])
    
    if has_os_extension(target, open_in_os_extensions): # TODO 我不是不想加.md后缀么
        _logger.info('has no extension for opening in vim')
        return OSOpen(anchor_path(target, current_file))

    return VimOpen(anchor_path(target, current_file)) # 跨文件, 且用vim打开的文件走这里


def anchor_path(target, current_file):
    if os.path.isabs(target):
        return target

    _logger.info('anchor path relative to %s', current_file)
    return os.path.join(os.path.dirname(current_file), target)


def has_os_extension(path, extensions):
    '''如果extensions不为空, 且后缀在extensions中, 返回True'''
    if not extensions:
        return False

    path = parse_path(path)
    _, ext = os.path.splitext(path.path)
    return ext in extensions



class Action(object):
    '''仅仅是保存了target'''
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


class VimOpen(Action):
    '''这个类负责打开文件, 如果有line number, 再跳到指定line number, 文件有可能没有后缀'''
    def __call__(self):
        import vim

        path = parse_path(self.target)

        # TODO: make space handling more robust?
        vim.command('e {}'.format(path.path.replace(' ', '\\ '))) # highlight 这一步就在vim中打开了文件
        if path.line is not None:
            try:
                line = int(path.line)

            except:
                print('invalid line number')
                return

            else:
                vim.current.window.cursor = (line, 0) # highlight 控制cursor到指定行

        if path.anchor is not None:
            JumpToAnchor(path.anchor)() #? JumpToAnchor没有__init__方法, 那么如何接受参数?


class JumpToAnchor(Action):
    '''这个类负责跳到anchor, target存的是anchor, 这里的target包括^'''
    # attr_list_pattern = re.compile(r'\^(?P<id>\w+)')

    def __call__(self):
        import vim
        line = self.find_anchor(self.target, vim.current.buffer)

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

line_regex = re.compile('^.*:\d+$')
def parse_path(target):
    """Parse a path with optional line number of anchor into its parts.
    有可能没有后缀

    For example::

        parse_path('foo.md:30') == ParsedPath('foo.md', line=30)
        parse_path('foo.md#anchor') == ParsedPath('foo.md', anchor='anchor')
    而且ParsedPath没做什么处理, 只是存起来

    """
    ret = ParsedPath()
    if(line_regex.match(target)):
        path, line = target.rsplit(':', 1) # 现在line还是字符串
        ret.line = line
        ret.path = path
    elif('#' in target):
        path, anchor = target.rsplit('#', 1) # 现在line还是字符串
        if not anchor.startswith("^"):
            anchor = "# "+anchor
        ret.anchor = anchor
        ret.path = path
    if ret.path and (not '.' in ret.path):
        ret.path = ret.path + ".md"
    return ret


class ParsedPath(object):
    '''anchor既可以表示'''
    def __init__(self, path=None, line=None, anchor=None):
        self.path = path
        self.line = line
        self.anchor = anchor

    def __repr__(self):
        return 'ParsedPath({!r}, line={}, anchor={!r})'.format(self.path, self.line, self.anchor)


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

