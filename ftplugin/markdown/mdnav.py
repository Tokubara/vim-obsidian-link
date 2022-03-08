from __future__ import print_function
import collections
import json
import os.path
import re
import sys
# sys.path.append("/Users/quebec/box/obsidian/vim/mdnav/ftplugin/markdown/")
from parse_path import ParsePath, ParsedPath, ParseType
from parse_link import parse_link



def plugin_entry_point():
    import vim

    if int(vim.eval("exists('g:mdnav#DebugMode')")):
        _logger.active = vim.eval('g:mdnav#DebugMode') == 'true'

    row, col = vim.current.window.cursor
    cursor = (row - 1, col) # -1的原因是, 行号是从1开始, 但是取当前行, 从0开始

    try:
        target = parse_link(col, vim.current.line) # 返回了[]()中()中的内容
        if(not target):
            raise TypeError("not find link")
        action = open_link(
            target,
            current_file=vim.eval("expand('%:p')"),
        ) # 返回是类的实例, 比如JumpToAnchor
        action() # 跳转动作
    except Exception:
        import traceback
        print(traceback.format_exc())



# {{{ 入口, target是target
def open_link(target, current_file):
    """
    :returns: a callable that encapsulates the action to perform
    """
    assert target,"target is None"
   # if target is not None:
    #     target = target.strip()

    # if not target:
    #     _logger.info('no target')
    #     # return NoOp(target)

    #     return None
    parsed_path = ParsePath(current_file).parse_path(target)
    if(parsed_path.type == ParseType.page):
        return PDFOpen(parsed_path)
    elif(parsed_path.type == ParseType.os):
        return OSOpen(parsed_path)
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
            call(['xdg-open', self.target.path])

        elif sys.platform.startswith('darwin'):
            call(['open', self.target.path])

        else:
            os.startfile(self.target.path)

class PDFOpen(Action):
    def __call__(self):
        # print(f"{self.target.path}: {self.target.line}")
        call(['/Users/quebec/bin/goto_page', self.target.path, self.target.anchor])

# {{{1 VimOpen: input: [[]]的内容, 跨文件, vim处理的情况
class VimOpen(Action):
    '''这个类负责打开文件, 如果有line number, 再跳到指定line number, 文件有可能没有后缀'''
    def __call__(self):
        import vim
    # TODO 这里可以用tabnew, split, 可以用选项
        if(self.target.path):
            vim.command('split {}'.format(self.target.path.replace(' ', '\\ '))) # highlight 这一步就在vim中打开了文件
        if(self.target.type == ParseType.line):
            JumpToLine(self.target)()
        elif(self.target.type == ParseType.heading):
            JumpToHeading(self.target)()
        elif(self.target.type == ParseType.suffix):
            JumpToSuffix(self.target)()
        elif(self.target.type == ParseType.id):
            JumpToId(self.target)()
        elif(self.target.type == ParseType.empty):
            pass
        else:
            raise TypeError(f"unknown type: {self.target.type}")


class JumpToLine(Action):
    def __call__(self):
        import vim
        vim.current.window.cursor = (int(self.target.anchor) + 1, 0) #highlight 设置line


class JumpToHeading(Action):
    def __call__(self):
        import vim
        for (idx, line) in enumerate(vim.current.buffer):
            if(re.match(r'#{2,6}\S '+self.target.anchor, line)):
                vim.current.window.cursor = (idx + 1, 0)
                return
        raise TypeError(f'not find heading {self.target.anchor}')


class JumpToSuffix(Action):
    def __call__(self):
        import vim
        for (idx, line) in enumerate(vim.current.buffer):
            if(line.strip().endswith(self.target.anchor)):
                vim.current.window.cursor = (idx + 1, 0)
                return
        raise TypeError(f'not find suffix {self.target.anchor}')


class JumpToId(Action):
    def __call__(self):
        import vim
        for (idx, line) in enumerate(vim.current.buffer):
            if(line.strip().endswith("^"+self.target.anchor)):
                vim.current.window.cursor = (idx + 1, 0)
                return
        raise TypeError(f'not find id {self.target.anchor}')


def call(args):
    """If available use vims shell mechanism to work around display issues
    """
    # try:
    #     import vim

    # except ImportError:
    #     import subprocess
    #     subprocess.call(args)

    # else:
    #     args = ['shellescape(' + json.dumps(arg) + ')' for arg in args]
    #     vim.command('execute "! " . ' + ' . " " . '.join(args))
    import subprocess
    subprocess.call(args)


if __name__ == "__main__":
    plugin_entry_point()

