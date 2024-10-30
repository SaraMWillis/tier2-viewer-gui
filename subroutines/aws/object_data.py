#!/usr/bin/env python3

import subprocess, sys, emoji, re

'''
------------------------------------------------------------------------------------------
                                Check if directory
When a user queries their bucket, we want to know if the object they're looking at is a 
file or "directory". This function figures that out
'''
def check_if_directory(prefix,searchable_prefix,bucket,get_file=False):
    print(prefix,searchable_prefix,bucket)
    regex_pattern = "\d{4}\-\d{2}\-\d{2}\s\d{2}\:\d{2}\:\d{2}\s+\d+\s{1}"
    # If no prefix was provided, then we're querying the bucket which we'll view as the 
    # root directory /
    if prefix == None or prefix == "" or prefix == "/":
        prefix_is_dir = True
    # If the prefix option has been provided, we'll run an aws s3 ls on it.
    else:
        # We need to collect the exact name provided by the user here. This is because, say you have 
        # a file 1 and file 111, if you query --prefix=/path/to/1 with AWS, it will return both files. 
        # We only want the thing that exactly matches the input. 
        if prefix[-1] == "/":
            compare_prefix = prefix[:-1]
        else:
            compare_prefix= prefix
        compareable_names = [compare_prefix.split("/")[-1], compare_prefix.split("/")[-1]+"/"]
        print(compareable_names)
        p = subprocess.Popen(["aws s3 ls %s/%s"%(bucket,searchable_prefix)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        out,err = p.communicate()
        out = out.decode("utf-8","ignore")
        err = err.decode("utf-8","ignore") 
        print(err)   
        
        # If no results are returned, then this path does not exist
        if out == err == "":
            return None
 
            
        # If we get results, we need to check the number of results 
        out = out.strip().split("\n")
        
        # First, if there's only one entry, that makes things easy since we can differentiate directories from files
        # using the presence of the string PRE
        if len(out) == 1:
            
            # These names are in a space-delimited list, so we need a good way to parse them. We do it with regex
            reformatted = re.split(regex_pattern,out[0])
            # Directories don't have date/time/size stamps on them and start with PRE, so we can identify them this way
            if len(reformatted) == 1 and reformatted[0][:3] == "PRE":
                #if user_args.get_file == True:
                #    sys.exit(user_args.WARNINGCOLOR+ "Warning: Found %s in bucket %s, but this object is not a file. Exclude the --file option to see the contents. Exiting."%(user_args.prefix,user_args.bucket) + user_args.ENDCOLOR)
                name = reformatted[0].replace("PRE ","")
                
                # If the object that we've found doesn't exactly match the object the user is querying, we exit
                if name not in compareable_names:
                    return None
                    
                # Otherwise, we continue and return the information that the object being queried is a directory
                else:
                    prefix_is_dir = True
            
            # If our result has length 2, then a date/time/size stamp was found which means the prefix is a file.
            elif len(reformatted) == 2:
                name = reformatted[-1]
                # Before we get too excited, we'll check to see if the object we found actually matches the object
                # that was queried. If not, we exit with a warning.
                if name not in compareable_names:
                    return None
                else:
                    prefix_is_dir = False
                    
        # If there's more than one entry, we check what matches the exact user input.
        

        # Here's an issue I recently thought of: AWS will let you store files/"directories" in the same location
        # with the same name. So a "directory" 1 and an file 1 could both exist in the same search path. 
        # To handle this, I'll make it default to the directory and will add an additional --file flag so 
        # the user can override this behavior.
        else:
            object_found = False
            redundancy_count = 0
            for result in out:
                reformatted = re.split(regex_pattern,result)
                if len(reformatted) == 1 and reformatted[0][:3] == "PRE":
                    name = reformatted[0].replace("PRE ","")
                    if name in compareable_names:
                        prefix_is_dir = True
                        object_found = True
                        redundancy_count += 1
                elif len(reformatted) == 2:
                    name = reformatted[-1]
                    if name in compareable_names:
                        object_found = True
                        redundancy_count += 1
                        # If we've already found this object and the user hasn't specified they want the file,
                        #  then we default to the directory type.
                        if redundancy_count > 1 and get_file == False:
                            prefix_is_dir = True
                        elif get_file == True:
                            prefix_is_dir = False
                        else:
                            prefix_is_dir = False
            if object_found == False:
                return None

    return prefix_is_dir