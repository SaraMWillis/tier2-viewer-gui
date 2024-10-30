#!/usr/bin/env python3

import subprocess, json, sys, shlex

def get_tier_class(bucket, true_path):

    
    command = "aws s3api head-object --bucket {} --output json --key '{}'".format(bucket,true_path)
    print(command)
    #print(command_str)
    #sys.exit(0)
    #print(command)
    
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    #p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #p = subprocess.Popen(['aws s3api head-object --bucket %s --output json --key %s'%(bucket,'"'+true_path+'"')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    out,err = p.communicate()
    try:
        out =  json.loads(out.decode('utf-8',"ignore"))
    except json.decoder.JSONDecodeError:

        print("\nError retrieving data %s\nCheck that your input and try again. You can check the contents of your bucket without the --tier flag.\nIf the object you're querying exists, report this bug to sarawillis@arizona.edu. Debug information below."%true_path)
        print("Command executed: aws s3api head-object --bucket %s --output json --key %s"%(bucket,true_path))
        print("stdout: %s"%out.decode("utf-8","ignore"))
        print("stderr: %s"%err.decode("utf-8","ignore"))
        sys.exit(1)
    try:
        storage_class = out["StorageClass"]
    except KeyError:
        storage_class = "STANDARD"
    try: 
        restore_status = out["Restore"]
        if "false" in restore_status:
            restore_status="RESTORED"
        elif "true" in restore_status:
            restore_status="PROCESSING"
    except KeyError:
        restore_status = "-"
    try:
        archive_status = out["ArchiveStatus"]
    except KeyError:
        if storage_class == "INTELLIGENT_TIERING":
            archive_status = "FREQUENT_ACCESS"
        else:
            archive_status = "-"
    return storage_class, archive_status, restore_status

def find_objects(bucket, out,contents,objects):
    depth_1_objects = {}
    max_file_length = 0 

    for k in out["Contents"]:
        full_path = k["Key"]
        print(k)
        
        if full_path in contents.keys():
            obj_size = k["Size"]
            if objects[contents[full_path]]["directory"] == True:
                objects[contents[full_path]]["storage class"] = "-"
                objects[contents[full_path]]["restore status"] = "-"
                objects[contents[full_path]]["archive status"] = "-"
            elif k["StorageClass"] == "STANDARD":
                objects[contents[full_path]]["storage class"] = k["StorageClass"]
                objects[contents[full_path]]["restore status"] = "-"
                objects[contents[full_path]]["archive status"] = "-"
            else:
                storage_class = k['StorageClass']
                storage_class, archive_status, restore_status = get_tier_class(bucket, full_path)
                objects[contents[full_path]]["storage class"] = storage_class
                objects[contents[full_path]]["restore status"] = restore_status
                objects[contents[full_path]]["archive status"] = archive_status

    return objects



