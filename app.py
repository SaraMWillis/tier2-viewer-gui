from flask import Flask, render_template, request, redirect, url_for, flash
import pwinput, os, socket
from subroutines.config import credentials
from subroutines.aws.lists import valid_buckets, aws_ls, aws_list_objects
from subroutines.aws.storage_class import find_objects, get_tier_class
from subroutines.aws.object_data import check_if_directory
from subroutines.aws.merge import merge_bucket_dictionaries
from subroutines.aws.get_size import du
from subroutines.aws.restore import restore
from subroutines.formatting.searchable_prefix import searchable_prefix

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set your secret key here
#logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check-credentials', methods=['GET', 'POST'])
def check_credentials():
    credentials_exist = credentials.find_credentials()
    if credentials_exist == False:
        status_message = "Credentials not found. To configure them, use the form below."
        alert_type = "alert-warning"
        return render_template("configure_credentials.html", status_message=status_message,alert_type=alert_type)
    else:
        credential_values = credentials.pull_credentials()
        if credential_values == None:
            status_message = "Credentials in an invalid format. To reconfigure, use the form below."
            alert_type = "alert-warning"
            return render_template("configure_credentials.html", status_message=status_message,alert_type=alert_type)
        else:
            bucket_name,private_key,public_key = credential_values
            alert_type = "alert-ok"
            return render_template("configure_credentials.html", bucket_name=bucket_name,private_key=private_key,public_key=public_key)
        



@app.route('/configure-credentials', methods=['GET', 'POST'])
def configure_credentials():
    if request.method == 'POST':
        bucket = request.form.get('bucket_name')
        public_key = request.form.get('public_key')
        private_key = request.form.get('private_key')

        # You can use the variables as needed here, for example:
        #flash(f"Received: Bucket: {bucket}, Access Key: {public_key}, Secret Key: {private_key}")
        
        status, message = credentials.save_and_check_credentials(bucket,private_key,public_key)
        if status == None:
            return render_template("configure_credentials.html", credentials_message=message,alert_type="alert-danger")
        else:
            return render_template("configure_credentials.html", credentials_message=message,alert_type="alert-success")

    return render_template('configure_credentials.html')


@app.route('/bucket_size', methods=["GET","POST"])
def bucket_size():
    credential_values = credentials.pull_credentials()
    return render_template('list_objects.html')






@app.route('/list-objects', methods=["GET","POST"])
def list_objects():
    if request.method == 'POST':
        credential_values = credentials.pull_credentials()
        if credential_values == None:
            status_message="Error: No AWS credentials found. Please configure your credentials to view your bucket. This can be done in the Credentials tab."
            return render_template('list_objects.html',status_message=status_message,alert_type="alert-danger")

        bucket_name,private_key,public_key = credential_values
        path = request.form.get('path')
        request_object_tier = request.form.get('request_object_tier') == 'on'  # Checkbox returns 'on' if checked

        searchable_path = searchable_prefix(path.replace('"',""))
        is_dir = check_if_directory(path,searchable_path,bucket_name)

        if is_dir == None:
            status_message="Error: Path not found."
            return render_template('list_objects.html',status_message=status_message,alert_type="alert-danger")
        
        objects = aws_ls(bucket_name, searchable_path,is_dir,False)
        if objects == None:
            status_message = "Error: Problem connecting to bucket. Check that you are connected to the internet."
            return render_template("list_objects.html",status_message=status_message,alert_type="alert-danger")
        contents = [i for i in objects.keys()]
        print(objects)
        paths = {objects[p]["true path"]: p for p in objects.keys()}


        if request_object_tier == False:     
            return render_template('list_objects.html', contents=contents, objects=objects,tier=False)
        else:
            file_count = sum(value["directory"] == False for value in objects.values())
            s3_json = aws_list_objects(10000,objects,bucket_name,searchable_path)
            objects = find_objects(bucket_name,s3_json,paths,objects)
            return render_template("list_objects.html",objects=objects,contents=contents,tier=True, request_object_tier=request_object_tier)
            flash(objects)

    #contents = ["i","j","k"]
    return render_template('list_objects.html')






@app.route('/restore-objects', methods=['GET', 'POST'])
def restore_objects():
    if request.method == 'POST':
        # Here you would handle restoring the object
        object_name = request.form.get('object_name')
        flash(f'Object {object_name} restored successfully!')
        return redirect(url_for('index'))
    return render_template('restore_objects.html')

if __name__ == '__main__':
    app.run(debug=True)
