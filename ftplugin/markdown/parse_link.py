def parse_link(column, line):
    '''返回[[]]中的内容'''
    line_bytes = bytes(line, encoding='utf8')
    sub_bytes = None # 返回对象(返回需要转换)
    column = column - 1
    start_pos = -1
    end_pos = -1
    left_ord = ord('[')
    right_ord = ord(']')
    if(line_bytes[column]==left_ord):
        if(column+1 >= 0 and line_bytes[column+1]==left_ord):
            start_pos = column+2
        elif(column-1 >=0 and line_bytes[column-1]==left_ord):
            start_pos = column+1
        end_pos = line_bytes.find(b']]', start_pos) #? 这样可以么?
        if start_pos >= 0 and end_pos >= 0:
            sub_bytes = line_bytes[start_pos:end_pos]
    elif(line_bytes[column]==right_ord):
        if(column-1 >=0 and line_bytes[column-1]==right_ord):
            end_pos = column - 1
        elif(column+1 >=0 and line_bytes[column+1]==right_ord):
            end_pos = column
        start_pos = line_bytes.rfind(b'[[', 0, end_pos)
        if start_pos >= 0 and end_pos >= 0:
            sub_bytes = line_bytes[(start_pos+2):end_pos]
    else:
        start_pos = line_bytes.rfind(b'[[')
        end_pos = line_bytes.find(b']]')
        if start_pos >= 0 and end_pos >= 0:
            sub_bytes = line_bytes[(start_pos+2):end_pos]
    if(sub_bytes):
        return sub_bytes.decode('utf8')
    else:
        print("cannot find link")
        exit(1)
if(__name__=="__main__"):
    line = "大概说起来, args表示要执行的命令, 既可以是字符串, 也可以是字符串列表. 如果是字符串列表, 并且复杂(比如有重定向), 那么shell参数必须表示True, 这与[[perl#system]]逻辑相似."
    print(parse_link(203, line))
