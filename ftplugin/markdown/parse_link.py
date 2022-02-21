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
        # import pdb; pdb.set_trace()
        start_pos = line_bytes.rfind(b'[[', 0, column) #  ^9Fy79w
        end_pos = line_bytes.find(b']]', column)
        if start_pos >= 0 and end_pos >= 0:
            sub_bytes = line_bytes[(start_pos+2):end_pos]
    if(sub_bytes):
        return sub_bytes.decode('utf8')
    else:
        print("cannot find link")
        return None
if(__name__=="__main__"):
    line = "##### pynav, `[[#annotation: yolo格式]]`都解析不了?, `[[/Users/quebec/box/毕设/Soccer-Ball-Detection-YOLOv2/]]`识别有错误"
    print(parse_link(18, line))
