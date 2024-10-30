#!/usr/bin/env python3

import sys, subprocess, time
from tqdm import tqdm

def restore(bucket,searchable_prefix,is_dir,batch):
    #print(bucket, searchable_prefix,is_dir)
    searchable_prefix=searchable_prefix.replace('"','')
    #print("aws s3 ls --recursive 's3://%s/%s' | awk '{print $NF}'"%(bucket,searchable_prefix))
    p = subprocess.Popen(["aws s3 ls --recursive 's3://%s/%s' | awk '{print $NF}'"%(bucket,searchable_prefix)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output,error=p.communicate()
    out = output.decode("utf-8","ignore")
    err = error.decode("utf-8","ignore")
    print(err)
    contents = [i for i in out.split("\n") if i != ""]
    if len(contents) > 100 and batch == False:
        print("Yikes! This directory has %s objects. This restore may take a long time."%len(contents))
        proceed = None
        while proceed not in ["Y","N"]:
            proceed = input("Proceed? (Y/N): ").upper()
            if proceed not in ["Y","N"]:
                print("Option not recognized")
        if proceed == "N":
            sys.exit(0)
    if batch == False:
        t = tqdm(contents, desc="Found %s objects. Restoring"%len(contents), ascii=True)
    else:
        t = contents

    for i in t:
        p = subprocess.Popen(["aws s3api restore-object --bucket %s --key %s --restore-request '{}'"%(bucket,i)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        #print("aws s3api restore-object --bucket %s --key %s --restore-request '{}'"%(bucket,i))
        output,error=p.communicate()
        #out = output.decode("utf-8","ignore")
        err = error.decode("utf-8","ignore")
        # If this error happens, then the object has been uploaded to AWS as a Glacier/Deep Glacier object and isn't subject to intelligent tiering (only can be done using rclone to my knowledge).
        # We'll execute the restore for this object by setting a time limit
        if "The XML you provided was not well-formed or did not validate against our published schema" in err:
            p = subprocess.Popen(["aws s3api restore-object --bucket %s --key %s --restore-request '{\"Days\":30,\"GlacierJobParameters\":{\"Tier\":\"Standard\"}}'"%(bucket,i)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        #print(out)
        #print(err)
        #time.sleep(.01)
    '''
        p = subprocess.Popen(['aws s3 ls'],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()
    out = output.decode("utf-8","ignore")
    err = error.decode("utf-8","ignore")
    print(err)
    out = out.split("\n")
    valid_bucket_names = [i.split(" ")[-1] for i in out if i != ""]
    print(valid_bucket_names)
    sys.exit(0)
    '''
    sys.exit(0)