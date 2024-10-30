'''
------------------------------------------------------------------------------------------
                                     human readable
Converts bytes into a human-readable format
'''            
def human_readable(size):
    size = int(size)
    size_prefixes = ["B","KB","MB","GB","TB","PB"]
    
    for pfx in size_prefixes:
        if size < 1024:
            return str(size)+" "+pfx
        else:
            size = round(size/1024,1)