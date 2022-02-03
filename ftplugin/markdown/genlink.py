import re
import sys
import pathlib
import random
import string

def gen_random_string(length=6):
    return ''.join(random.choices(string.ascii_letters+string.digits, k=length))

def get_path():
    import vim
    cur_filename = vim.eval("expand('%:p')")
    pathobj = pathlib.PosixPath(cur_filename)
    if(pathobj.match("/Users/quebec/notes/*.md")):
        return pathobj.name.replace(".md", "")
    elif(pathobj.match("/Users/quebec/notes/vx_attachments/*")):
        return pathobj.name
    else:
        return cur_filename

def gen_heading_link(cur_line):
    heading_pattern = re.compile("^#{2,}\s(\S.*)$") 
    match_obj = heading_pattern.match(cur_line)
    if(match_obj):
        return "#" + match_obj.group(1)
    else:
        print("not a heading")
        exit(1)

def gen_id_link(cur_line):
    import vim
    rstr = gen_random_string(6)
    vim.current.buffer[vim.current.buffer.cursor[0]] = vim.current.buffer[vim.current.buffer.cursor[0]] + " ^" + rstr
    return "#^" + rstr


if __name__ == "__main__":
    import vim
    cur_line = vim.current.line
    link = None
    if(sys.argv[0] == "heading"):
        link = gen_heading_link(cur_line)
    elif(sys.argv[0] == "id"):
        link = gen_id_link(cur_line)
    elif(sys.argv[0] == "line"):
        link = f":{vim.current.cursor[0]}"
    else:
        link = ""
    full_link = get_path() + link
    vim.command("put *")


