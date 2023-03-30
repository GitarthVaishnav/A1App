from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import random
import hashlib
import os
import shutil
import base64
import csv
import pytz
from datetime import datetime

app = Flask(__name__)

dir_path = None
zip_path = None
d = False

def save_number_to_csv(number):
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(BASE_DIR,'numbers.csv')

    # Check if the file exists
    if not os.path.isfile(filename):
        # If the file does not exist, create a new one and write the headers
        with open(filename, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["StudentID", "Timestamp"])

    # Open the file in append mode and write the number and timestamp
    with open(filename, "a") as f:
        writer = csv.writer(f)
        writer.writerow([number, datetime.now(pytz.timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S %Z%z')])

    print("ID saved successfully.")



def generate_seed(input_number):
    input_number = str(input_number).encode()
    save_number_to_csv(int(input_number))
    return int(hashlib.sha256(input_number).hexdigest()[:16], 16) % (10 ** 8)

def generate_unique_list(input_number):
    seed = generate_seed(input_number)
    random.seed(seed)
    big_set = ["leq", "geq", "theta", "neq", "[", "]", "pm", "div", "!", "beta", "pi", "alpha", "sum", "times", "sqrt", "=", "(", ")", "+", "-"]
    unique_list = random.sample(big_set, 10)
    return unique_list

def generate_dataset(unique_list, input_number):
    # Set the parent directory path
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.join(BASE_DIR,'extracted_images-1')

    # Get a list of subdirectories in the parent directory
    subdirs = [d for d in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, d))]

    # Print the parent directory path and number of subdirectories
    print("Parent directory:", parent_dir)
    print("Number of subdirectories:", len(subdirs))

    # Set the number of files to copy from each subdirectory
    num_files = 500

    # Set the list of subdirectories to copy
    subdirs_to_copy = unique_list

    pth = ""

    # Iterate through each subdirectory
    for subdir in subdirs_to_copy:
        if subdir in subdirs:
            # Set the source and destination paths
            src_path = os.path.join(parent_dir, subdir)
            student_data_folder = os.path.join(BASE_DIR, "Student_Dataset")
            folder_name = f'dataset_42028assg1_{str(input_number)}'
            pth = os.path.join(student_data_folder, folder_name)
            dst_path = os.path.join(str(pth), subdir)

            # Create the destination directory if it does not exist
            if not os.path.exists(dst_path):
                os.makedirs(dst_path)

            # Get a list of files in the subdirectory
            files = [f for f in os.listdir(src_path) if os.path.isfile(os.path.join(src_path, f))]

            # Select a random set of files to copy
            seed = generate_seed(input_number)
            random.seed(seed)
            selected_files = random.sample(files, num_files)

            # Iterate through the selected files and copy them to the destination
            for file in selected_files:
                src_file = os.path.join(src_path, file)
                dst_file = os.path.join(dst_path, file)
                shutil.copy2(src_file, dst_file)
        else:
            print(f"{subdir} not exist in parent directory {parent_dir}")

    print("Files copied successfully!")
    return pth

def zip_directory(directory_path):
    global dir_path
    dir_path = directory_path
    # create a zip file with the directory
    shutil.make_archive(directory_path, 'zip', directory_path)
    # read the zip file and encode it as base64
    filename = directory_path + '.zip'
    with open(str(filename), 'rb') as f:
        zip_bytes = f.read()
    zip_base64 = base64.b64encode(zip_bytes).decode()
    if os.path.exists(directory_path):
        print("deleting the directory")
        shutil.rmtree(directory_path)
    return zip_base64

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    input_number = request.form['input_number']
    unique_list = generate_unique_list(input_number)
    dataset_path = generate_dataset(unique_list, input_number)
    zip_b64 = zip_directory(dataset_path)
    # print(dataset_path)
    filename = dataset_path.split('/')[-1] + '.zip'
    # print(filename)
    # Create a URL that can be used to download the zip file
    download_url = url_for('download_file', filename=filename)

    response = jsonify({'download_url': download_url})
    print(download_url)
    return response, 200

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    global d
    if d is True:
        if os.path.exists(str(os.path.dirname(dir_path))+'/'+str(dir_path.split('/')[-1] + '.zip')):
            print("Removing zip file.")
            os.remove(str(os.path.dirname(dir_path))+'/'+str(dir_path.split('/')[-1] + '.zip'))
            d = False
    d = False
    return response

@app.route(f'/download/<filename>')
def download_file(filename):
    print("Trying to download file: ", filename)
    print("Directory path: ", str(os.path.dirname(dir_path)))
    # Serve the zip file as a download
    response = send_from_directory(os.path.dirname(dir_path), filename, as_attachment=True)
    global d
    d = True
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
