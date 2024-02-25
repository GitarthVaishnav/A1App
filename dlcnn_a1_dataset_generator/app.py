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
from werkzeug.exceptions import InternalServerError
from werkzeug.utils import safe_join, secure_filename

dlcnn_a1_datagen_app = Flask(__name__)
CORS(dlcnn_a1_datagen_app)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
NUMBERS_CSV = os.path.join(BASE_DIR, "numbers.csv")
STUDENT_DATASET_FOLDER = os.path.join(BASE_DIR, "Student_Dataset")
EXTRACTED_IMAGES_DIR = os.path.join(BASE_DIR, "extracted_images-1")


def save_number_to_csv(number):
    try:
        if not os.path.isfile(NUMBERS_CSV):
            with open(NUMBERS_CSV, "w", newline="") as f:
                csv.writer(f).writerow(["StudentID", "Timestamp"])
        with open(NUMBERS_CSV, "a", newline="") as f:
            csv.writer(f).writerow(
                [
                    number,
                    datetime.now(pytz.timezone("Australia/Sydney")).strftime(
                        "%Y-%m-%d %H:%M:%S %Z%z"
                    ),
                ]
            )
    except Exception as e:
        current_app.logger.error(f"Failed to save number to CSV: {e}")
        raise InternalServerError("Failed to log the student ID.")


def generate_seed(input_number):
    try:
        input_number_str = str(input_number).encode()
        save_number_to_csv(int(input_number_str))
        return int(hashlib.sha256(input_number_str).hexdigest()[:16], 16) % (10**8)
    except Exception as e:
        current_app.logger.error(f"Failed to generate seed: {e}")
        raise InternalServerError("Seed generation failed.")


def generate_unique_list(input_number):
    try:
        seed = generate_seed(input_number)
        random.seed(seed)
        # set having folder names with all folders having 500+ images
        big_set_2 = [
            "beta",
            "pm",
            "infty",
            "rightarrow",
            "div",
            "leq",
            "times",
            "sin",
            "R",
            "u",
            "9",
            "0",
            "7",
            "i",
            "N",
            "G",
            "+",
            ",",
            "6",
            "z",
            "1",
            "8",
            "T",
            "S",
            "cos",
            "A",
            "-",
            "f",
            "H",
            "sqrt",
            "pi",
            "int",
            "sum",
            "lim",
            "neq",
            "log",
            "ldots",
            "theta",
            "ascii_124",
            "M",
            "!",
            "alpha",
            "j",
            "C",
            "]",
            "(",
            "d",
            "v",
            "q",
            "=",
            "4",
            "X",
            "3",
            "tan",
            "e",
            ")",
            "[",
            "b",
            "k",
            "l",
            "geq",
            "2",
            "y",
            "5",
            "p",
            "w",
        ]
        # selected folders for A23
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
    except Exception as e:
        current_app.logger.error(f"Failed to generate unique list: {e}")
        raise InternalServerError("Unique list generation failed.")


def generate_dataset(unique_list, input_number):
    try:
        if not os.path.isdir(EXTRACTED_IMAGES_DIR):
            raise FileNotFoundError(
                f"The directory {EXTRACTED_IMAGES_DIR} does not exist."
            )

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
    except FileNotFoundError as e:
        current_app.logger.error(f"{e}")
        raise
    except Exception as e:
        current_app.logger.error(f"Failed to generate dataset: {e}")
        raise InternalServerError("Dataset generation failed.")


def zip_directory(directory_path):
    try:
        if directory_path is None or not os.path.exists(directory_path):
            raise FileNotFoundError(
                "Invalid or non-existent directory path provided for zipping."
            )

        zip_file_path = shutil.make_archive(directory_path, "zip", directory_path)
        shutil.rmtree(directory_path)
        return zip_file_path
    except FileNotFoundError as e:
        current_app.logger.error(f"{e}")
        raise
    except Exception as e:
        current_app.logger.error(f"Error zipping directory: {e}")
        raise InternalServerError("Failed to create zip archive.")


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

        filename = os.path.basename(zip_file_path)
        download_url = url_for("download_file", filename=filename)

        return jsonify({"download_url": download_url}), 200
    except InternalServerError as e:
        return jsonify({"error": e.description}), 500
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Unhandled exception: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@dlcnn_a1_datagen_app.route("/download/<filename>")
def download_file(filename):
    try:
        directory = STUDENT_DATASET_FOLDER
        filename = secure_filename(filename)
        filepath = safe_join(directory, filename)

        if not os.path.exists(filepath):
            return jsonify({"error": "File not found."}), 404

        @after_this_request
        def cleanup(response):
            try:
                os.remove(filepath)
            except Exception as e:
                current_app.logger.error(f"Failed to remove file: {e}")
            return response

        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Error downloading file: {e}")
        return jsonify({"error": "Failed to download file."}), 500
