import re
import sys
import pathlib
import random
import string


def gen_random_string(length=6):
    return ''.join(random.choices(string.ascii_letters+string.digits, k=length))

def get_path(cur_filename):
    pathobj = pathlib.PosixPath(cur_filename)
    if(pathobj.match("/Users/quebec/notes/*.md")):
        return pathobj.name.replace(".md", "")
    elif(pathobj.match("/Users/quebec/notes/vx_attachments/*")):
        return pathobj.name
    else:
        return cur_filename

heading_pattern = re.compile(r"^#{2,}\s(\S.*)$") 
heading_content_pattern = re.compile("(\(.*\))|(:\s.*)")
def gen_heading_link(cur_line):
    match_obj = heading_pattern.match(cur_line)
    if(match_obj):
        heading = match_obj.group(1)
        heading_content = heading_content_pattern.sub("", heading)
        return "#" + heading_content
    else:
        raise Exception("not a heading")

id_pattern = re.compile(r"\^(\w+)$")
def gen_id_link(cur_line):
    # import pdb; pdb.set_trace()
    match_obj = id_pattern.search(cur_line)
    if match_obj:
        rstr = match_obj.group(1)
    else:
        import vim
        rstr = gen_random_string(6)
        cur_line_index = vim.current.window.cursor[0]-1
        vim.current.buffer[cur_line_index] = vim.current.buffer[cur_line_index] + "^" + rstr
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
        link = f"#:{vim.current.window.cursor[0]}"
    elif(sys.argv[0] == "suffix"):
        link = "#" + vim.current.line.strip()
    elif(sys.argv[0] == "empty"):
        link = ""
    cur_filename = vim.eval("expand('%:p')")
    path = get_path(cur_filename)
    full_link = f"[[{path +link}]]"
    full_link = full_link.replace("'", "''")
    vim.command(f"let @* = '{full_link}'")

# if __name__ == "__main__":
#     cur_line = ' ^cKuByc'
#     link = gen_id_link(cur_line)
#     print(link)
