import re
import os
class ParsePath:
    vault_prefix = "/Users/quebec/notes/vx_attachments/"
    open_in_os_extensions = {'png', 'pdf', 'jpg', 'jpeg', 'mp3', 'mp4'}
    def __init__(self, current_file):
        self.current_file =  current_file

    @classmethod
    def has_os_extension(cls, path):
        '''如果extensions不为空, 且后缀在extensions中, 返回True'''
        if not cls.open_in_os_extensions:
            return False

        _, ext = os.path.splitext(path)
        if ext:
            ext = ext[1:]
        return ext in cls.open_in_os_extensions
    def anchor_path(self, target):
        if os.path.isabs(target):
            return target

        ret = os.path.join(os.path.dirname(self.current_file), target)
        if(os.path.exists(ret)):
            return ret
        ret = os.path.join(self.vault_prefix, target)
        # if(os.path.exists(ret)):
        #     return ret
        return ret
    # {{{ normalize_path: 将target中出现的path转换为真正存在的path
    def normalize_path(self, path):
        if path and (not '.' in path):
            path = path + ".md"
        path = self.anchor_path(path)
        return path

    # {{{1 parse_path 解析[[]]出现的target, output: ParsedPath, path会处理相对路径
    def parse_path(self, target):
        """Parse a path with optional line number of anchor into its parts.
        有可能没有后缀

        For example::

            parse_path('foo.md:30') == ParsedPath('foo.md', line=30)
            parse_path('foo.md#anchor') == ParsedPath('foo.md', anchor='anchor')
        而且ParsedPath没做什么处理, 只是存起来

        """
        if('|' in target):
            target = target.rsplit('|')[0]
        # {{{2 解析信息存入到ret(ParsedPath)中
        ret = ParsedPath()
        if target.startswith('#^'): # 这是heading inside的情况
            ret.internal = True
            ret.anchor = target[1:]
        elif target.startswith('#'): # 这是heading inside的情况
            ret.internal = True
            ret.anchor = "# " + target[1:]
        else: # 这种情况一定包含文件
            # {{{2 其它文件的3种链接形式
            ret.internal = False # 这句话是多余的, False是默认值
            line_regex = re.compile('^.*:\d+$')
            if('#' in target):
                ret.path, ret.anchor = target.rsplit('#', 1) # 现在line还是字符串
                if not ret.anchor.startswith("^"):
                    ret.anchor = "# "+ret.anchor
            elif(line_regex.match(target)):
                ret.path, ret.line = target.rsplit(':', 1) # 现在line还是字符串
            else:
                ret.path = target
            # {{{2 规则化路径

            ret.path = self.normalize_path(ret.path)
            if(os.path.samefile(ret.path, self.current_file)):
                ret.internal = True
            assert os.path.exists(ret.path), f"{ret.path} not exists"
            ret.os_open = self.has_os_extension(target)
        if(ret.line):
            ret.line = int(ret.line)

        return ret
    # }}}


class ParsedPath(object):
    '''anchor既可以表示'''
    def __init__(self, path=None, line=None, anchor=None):
        self.path = path
        self.line = line
        self.anchor = anchor
        self.os_open = False
        self.internal = False

    def __repr__(self):
        return 'ParsedPath({!r}, line={}, anchor={!r}, os_open={}, internal={})'.format(self.path, self.line, self.anchor, self.os_open, self.internal)
parse_path = ParsePath("/Users/quebec/notes/tmp.md").parse_path
print(parse_path('python#如果没实现`__init__`方法, 类有参数'))
print(parse_path('#^t3thyl'))
print(parse_path('/Users/quebec/box/obsidian/vim/mdnav/ftplugin/markdown/mdnav.py'))
print(parse_path('Table 5.3.png'))

