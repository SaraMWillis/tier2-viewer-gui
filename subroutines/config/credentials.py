#!/usr/bin/env python3

import os, subprocess


def mask_string(s):
    if len(s) > 4:
        return '*' * (len(s) - 4) + s[-4:]
    else:
        return s

def find_credentials():
    home_dir = os.path.expanduser("~")

    aws_config_file = os.path.join(home_dir,".aws/credentials")
    bucket_config_file= os.path.join(home_dir,".config/aws-tier-check/bucket")
    if os.path.exists(aws_config_file) == False or os.path.exists(aws_config_file) == False:
        return False
    else:
        return True

def pull_credentials():
    home_dir = os.path.expanduser("~")
    aws_config_file = os.path.join(home_dir,".aws/credentials")
    bucket_config_file= os.path.join(home_dir,".config/aws-tier-check/bucket")

    if os.path.exists(aws_config_file) == True:
        with open(aws_config_file,"r") as file:
            lines = file.readlines()
            try:
                public_key = lines[1].strip().split("=")[-1].strip()
                private_key = lines[2].strip().split("=")[-1].strip()
                public_key = mask_string(public_key)
                private_key = mask_string(private_key)
                with open(bucket_config_file,"r") as file:
                    bucket = file.read()
                    return [bucket,private_key,public_key]
            except IndexError:
                return None
            
def save_and_check_credentials(netid,private_key,public_key):
    region_name = "us-west-2"
    output_format = "json"
    bucket="ua-rt-t2-{}".format(netid)

    env = os.environ.copy()
    env['AWS_ACCESS_KEY_ID'] = public_key
    env['AWS_SECRET_ACCESS_KEY'] = private_key
    env['AWS_DEFAULT_REGION'] = region_name
    try:
        subprocess.run(['aws', 'sts', 'get-caller-identity'],check=True,capture_output=True,text=True,env=env)
    except:
        return None, "Error: Credentials are invalid. Check your access keys and try again."
    try:
        subprocess.run(['aws', 's3api', 'head-bucket', '--bucket', bucket],check=True,capture_output=True,text=True,env=env)
    except:
        return None,"Error: The public and private keys are valid, but you either lack permission to access the bucket '{}' or it does not exist. Please check your permissions, bucket name, and that you are providing the associated access keys.".format(bucket)


    
    p = subprocess.Popen(['aws configure set aws_access_key_id %s'%public_key],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()
    p = subprocess.Popen(['aws configure set aws_secret_access_key %s'%private_key],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()
    p = subprocess.Popen(['aws configure set region %s'%region_name],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()
    p = subprocess.Popen(['aws configure set output %s'%output_format],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    output, error = p.communicate()

    home_dir = os.path.expanduser("~")
    bucket_path= os.path.join(home_dir,".config/aws-tier-check/")
    bucket_file = "bucket"
    try:
        os.makedirs(bucket_path)
    except FileExistsError:
        pass
    write_path = os.path.join(bucket_path,bucket_file)
    with open(write_path,"w") as file:
        file.write(bucket)
    return True, "Success: Your AWS credentials are valid and have been saved."