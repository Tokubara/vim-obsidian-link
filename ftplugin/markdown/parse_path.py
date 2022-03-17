import re
import os
from enum import Enum

class ParseType(Enum):
    id = 1
    suffix = 2
    heading = 3
    line = 4
    page = 5
    os = 6
    empty = 7


class ParsePath:
    vault_prefix = "/Users/quebec/notes/vx_attachments/"
    notes_prefix = "/Users/quebec/notes"
    open_in_os_extensions = {'png', 'jpg', 'jpeg', 'mp3', 'mp4'} # pdf单独处理了

    def __init__(self, current_file_path):
        self.current_file = current_file_path

    # {{{ normalize_path: 将target中出现的path转换为真正存在的path
    @classmethod
    def normalize_path(cls, path):
        if not os.path.isabs(path): # 只会是在notes中
            has_dot = '.' in path
            if(has_dot):
                path = os.path.join(cls.vault_prefix, path)
            else:
                path = os.path.join(cls.notes_prefix, path) + '.md'
        return path

    # {{{1 parse_path 解析[[]]出现的target, output: ParsedPath, path会处理相对路径
    def parse_path(self, target): # anchor就是#之后的内容
        """Parse a path with optional line number of anchor into its parts.
        """
        def set_anchor(ret, anchor):
            if(anchor.startswith(':')):
                ret.anchor = anchor[1:]
                if(ret.path and ret.path.endswith('pdf')):
                    ret.type = ParseType.page
                else:
                    ret.type = ParseType.line
            elif(anchor.startswith('%')):
                ret.anchor = anchor[1:]
                ret.type = ParseType.suffix
            elif(anchor.startswith('^')):
                ret.type = ParseType.id
                ret.anchor = anchor[1:]
            else:
                ret.type = ParseType.heading
                ret.anchor = anchor


        if('|' in target):
            target = target.rsplit('|')[0]
        # {{{2 解析信息存入到ret(ParsedPath)中
        ret = ParsedPath()
        if target.startswith('#'):
            # 本来path就默认为None, 表示internal
            set_anchor(ret, target[1:])
        else:
            if '#' in target: # 这种情况一定包含文件
                # import pdb; pdb.set_trace()
                ret.path, anchor = target.split('#', 1)
                set_anchor(ret, anchor)
                ret.path = self.normalize_path(ret.path)
            else:
                ret.path = self.normalize_path(target)
                if('.' in ret.path and ret.path.rsplit('.', 1)[1].lower() in self.open_in_os_extensions):
                    ret.type = ParseType.os
                else:
                    ret.type = ParseType.empty
            # {{{2 规则化路径
            
            assert ret.type
            if(os.path.samefile(ret.path, self.current_file)):
                ret.path = None
            else:
                assert os.path.exists(ret.path), f"{ret.path} not exists"

        return ret
    # }}}


class ParsedPath(object):
    '''anchor既可以表示'''
    def __init__(self):
        self.path = None # 如果为None, 表示是internal
        self.type = None
        self.anchor = None

    def __repr__(self):
        return 'ParsedPath({!r}, type={}, anchor={!r})'.format(self.path, self.type, self.anchor)
    # {{{1 testcase
if __name__ == '__main__':
    parse_path = ParsePath("/Users/quebec/notes/yolo.md").parse_path
    print(parse_path('python#如果没实现`__init__`方法, 类有参数'))
    print(parse_path('python'))
    print(parse_path('#^t3thyl'))
    print(parse_path('/Users/quebec/box/毕设/Soccer-Ball-Detection-YOLOv2/cfg/yolo_custom.cfg#%classes=2'))
    print(parse_path('/Users/quebec/Documents/Book/The_Linux_Command_Linex.pdf#:224'))
    print(parse_path('Table 5.3.png'))
    print(parse_path('perl#scalar context'))
    print(parse_path('tmp#^3lPZjZ'))

