def parse_tsv(file_reader, row_handler=None):

    def readline(reader):
        """读取一行，但不包括末尾换行符"""
        content = reader.readline()
        if isinstance(content, bytes):
            return content.decode("utf-8").rstrip("\n")
        return content.rstrip("\n")

    data = []
    headers = readline(file_reader).split("\t")
    while line := readline(file_reader):
        if line and (values := line.split("\t")):
            row = {k: v for k, v in zip(headers, values)}
            if row_handler:
                row = row_handler(row, headers=headers)
            data.append(row)
    return data
