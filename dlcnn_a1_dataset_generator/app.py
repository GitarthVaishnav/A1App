import base64
import csv
import hashlib
import os
import random
import shutil
from datetime import datetime

import pytz
from flask import (
    Flask,
    after_this_request,
    current_app,
    jsonify,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_cors import CORS
from werkzeug.utils import safe_join, secure_filename

dlcnn_a1_datagen_app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
NUMBERS_CSV = os.path.join(BASE_DIR, "numbers.csv")
STUDENT_DATASET_FOLDER = os.path.join(BASE_DIR, "Student_Dataset")
EXTRACTED_IMAGES_DIR = os.path.join(BASE_DIR, "extracted_images-1")


def save_number_to_csv(number):
    try:
        if not os.path.isfile(NUMBERS_CSV):
            with open(NUMBERS_CSV, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["StudentID", "Timestamp"])
        with open(NUMBERS_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    number,
                    datetime.now(pytz.timezone("Australia/Sydney")).strftime(
                        "%Y-%m-%d %H:%M:%S %Z%z"
                    ),
                ]
            )
    except Exception as e:
        raise IOError(f"Failed to save number to CSV: {e}")


def generate_seed(input_number):
    try:
        input_number_str = str(input_number).encode()
        save_number_to_csv(int(input_number_str))
        return int(hashlib.sha256(input_number_str).hexdigest()[:16], 16) % (10**8)
    except Exception as e:
        raise ValueError(f"Failed to generate seed: {e}")


def generate_unique_list(input_number):
    seed = generate_seed(input_number)
    random.seed(seed)
    big_set = [
        "leq",
        "geq",
        "theta",
        "neq",
        "[",
        "]",
        "pm",
        "div",
        "!",
        "beta",
        "pi",
        "alpha",
        "sum",
        "times",
        "sqrt",
        "=",
        "(",
        ")",
        "+",
        "-",
    ]
    return random.sample(big_set, 10)


def generate_dataset(unique_list, input_number):
    if not os.path.isdir(EXTRACTED_IMAGES_DIR):
        raise FileNotFoundError(f"The directory {EXTRACTED_IMAGES_DIR} does not exist.")

    folder_name = f"dataset_42028assg1_{str(input_number)}"
    dataset_path = os.path.join(STUDENT_DATASET_FOLDER, folder_name)

    if not os.path.exists(STUDENT_DATASET_FOLDER):
        os.makedirs(STUDENT_DATASET_FOLDER, exist_ok=True)

    for subdir in unique_list:
        src_path = os.path.join(EXTRACTED_IMAGES_DIR, subdir)
        if not os.path.isdir(src_path):
            raise FileNotFoundError(
                f"Subdirectory {subdir} does not exist in {EXTRACTED_IMAGES_DIR}"
            )
        dst_path = os.path.join(dataset_path, subdir)
        os.makedirs(dst_path, exist_ok=True)

        files = os.listdir(src_path)
        selected_files = random.sample(files, min(500, len(files)))

        for file in selected_files:
            shutil.copy2(os.path.join(src_path, file), os.path.join(dst_path, file))
    return dataset_path


def zip_directory(directory_path):
    if directory_path is None or not os.path.exists(directory_path):
        raise FileNotFoundError(
            "Invalid or non-existent directory path provided for zipping."
        )

    shutil.make_archive(directory_path, "zip", directory_path)
    filename = f"{directory_path}.zip"
    return filename


@dlcnn_a1_datagen_app.route("/")
def index():
    return render_template("index.html")


@dlcnn_a1_datagen_app.route("/api/generate", methods=["POST"])
def generate():
    try:
        input_number = request.form.get("input_number", type=int)
        unique_list = generate_unique_list(input_number)
        dataset_path = generate_dataset(unique_list, input_number)
        zip_file_path = zip_directory(dataset_path)

        @after_this_request
        def remove_file(response):
            try:
                shutil.rmtree(dataset_path)
            except Exception as e:
                dlcnn_a1_datagen_app.logger.error(
                    "Error removing or cleaning up dataset file or directory."
                )
            return response

        filename = os.path.basename(zip_file_path)
        download_url = url_for("download_file", filename=filename)
        return jsonify({"download_url": download_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dlcnn_a1_datagen_app.route("/download/<filename>")
def download_file(filename):
    try:
        directory = os.path.join(BASE_DIR, "Student_Dataset")
        # Ensure the filename is secure and prevent directory traversal
        filename = secure_filename(filename)
        filepath = safe_join(directory, filename)

        if not os.path.exists(filepath):
            return jsonify({"error": "File not found."}), 404

        @after_this_request
        def cleanup(response):
            try:
                os.remove(filepath)
                # Optionally remove the parent directory if it's safe to do so
                # parent_dir = os.path.dirname(filepath)
                # if os.path.isdir(parent_dir):
                #     shutil.rmtree(parent_dir, ignore_errors=True)
            except Exception as e:
                current_app.logger.error(f"Failed to remove file: {e}")
            return response

        # Use Flask's send_from_directory for secure file delivery
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
