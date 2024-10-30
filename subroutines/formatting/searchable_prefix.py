
def searchable_prefix(prefix):
    if prefix == "":
        searchable_prefix= None
    elif prefix[-1] == "/":
        prefix = prefix[:-1]
    if prefix == "":
        searchable_prefix = None
    if prefix != "":
        if prefix[0] == "/":
            prefix = prefix[1:]
        first_index = len(prefix.split("/"))
        searchable_prefix = '"' + prefix + '"'
    return searchable_prefix


