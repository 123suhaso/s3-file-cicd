from flask import Flask, render_template, request, redirect, url_for
import boto3
import os
app = Flask(__name__)


# Get environment variables from ~/.bashrc
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Initialize the S3 client with environment variables
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)


def list_s3_files():
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    return response.get("Contents", [])


def list_s3_buckets():
    response = s3.list_buckets()
    return response.get("Buckets", [])

#create an s3 bucket
def create_s3_bucket(bucket_name):
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': AWS_DEFAULT_REGION})

#delet an s3 bucket
def delete_s3_bucket(bucket_name):
    s3.delete_bucket(Bucket=bucket_name)

@app.route("/")
def index():
    files = list_s3_files()
    buckets = list_s3_buckets()
    return render_template("index.html", files=files, buckets=buckets)

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            s3.upload_fileobj(file, S3_BUCKET_NAME, file.filename)
            print("File uploaded successfully!", "success")
            return redirect(url_for("index"))
    return render_template("upload.html")

@app.route("/delete/<filename>")
def delete_file(filename):
    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
    print(f"{filename} deleted!", "danger")
    return redirect(url_for("index"))

@app.route("/copy/<filename>")
def copy_file(filename):
    copy_source = {"Bucket": S3_BUCKET_NAME, "Key": filename}
    new_key = f"copy_of_{filename}"
    s3.copy_object(Bucket=S3_BUCKET_NAME, CopySource=copy_source, Key=new_key)
    print(f"Copied {filename} to {new_key}!", "info")
    return redirect(url_for("index"))

@app.route("/move/<filename>/<new>")
def move_file(filename, new):
    copy_source = {"Bucket": S3_BUCKET_NAME, "Key": filename}
    new_key = f"{new}/{filename}"
    s3.copy_object(Bucket=S3_BUCKET_NAME, CopySource=copy_source, Key=new_key)
    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
    print(f"Moved {filename} to {new}!", "warning")
    return redirect(url_for("index"))

@app.route("/create_bucket", methods=["POST"])
def create_bucket():
    bucket_name = request.form["bucket_name"]
    try:
        create_s3_bucket(bucket_name)
        print(f"Bucket {bucket_name} created!", "success")
    except Exception as e:
        print(f"Error creating bucket: {e}", "error")
    return redirect(url_for("index"))

@app.route("/delete_bucket/<bucket_name>")
def delete_bucket(bucket_name):
    try:
        delete_s3_bucket(bucket_name)
        print(f"Bucket {bucket_name} deleted!", "danger")
    except Exception as e:
        print(f"Error deleting bucket: {e}", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
