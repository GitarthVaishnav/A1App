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

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
NUMBERS_CSV = os.path.join(BASE_DIR, "numbers.csv")
STUDENT_DATASET_FOLDER = os.path.join(BASE_DIR, "Student_Dataset")
EXTRACTED_IMAGES_DIR = os.path.join(BASE_DIR, "extracted_images-1")


def save_number_to_csv(number):
    try:
        # Ensure the existence of the header
        if not os.path.isfile(NUMBERS_CSV):
            with open(NUMBERS_CSV, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["StudentID", "Timestamp"])

        # Append the new entry
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
        print("ID saved successfully.")
    except Exception as e:
        print(f"Error saving number to CSV: {e}")


def generate_seed(input_number):
    try:
        input_number_str = str(input_number).encode()
        save_number_to_csv(int(input_number_str))
        return int(hashlib.sha256(input_number_str).hexdigest()[:16], 16) % (10**8)
    except Exception as e:
        print(f"Error generating seed: {e}")
        return None


def generate_unique_list(input_number):
    seed = generate_seed(input_number)
    if seed is not None:
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
    else:
        return []


def generate_dataset(unique_list, input_number):
    try:
        if not unique_list:
            print("Empty unique list provided.")
            return None

        folder_name = f"dataset_42028assg1_{str(input_number)}"
        dataset_path = os.path.join(STUDENT_DATASET_FOLDER, folder_name)

        for subdir in unique_list:
            src_path = os.path.join(EXTRACTED_IMAGES_DIR, subdir)
            if os.path.isdir(src_path):
                dst_path = os.path.join(dataset_path, subdir)
                os.makedirs(dst_path, exist_ok=True)

                seed = generate_seed(input_number)
                random.seed(seed)
                files = os.listdir(src_path)
                selected_files = random.sample(files, min(500, len(files)))

                for file in selected_files:
                    shutil.copy2(
                        os.path.join(src_path, file), os.path.join(dst_path, file)
                    )
            else:
                print(f"{subdir} does not exist in {EXTRACTED_IMAGES_DIR}")

        print("Files copied successfully!")
        return dataset_path
    except Exception as e:
        print(f"Error generating dataset: {e}")
        return None


def zip_directory(directory_path):
    try:
        if directory_path is None:
            print("Invalid directory path provided for zipping.")
            return None

        shutil.make_archive(directory_path, "zip", directory_path)
        filename = f"{directory_path}.zip"

        with open(filename, "rb") as f:
            zip_bytes = f.read()

        zip_base64 = base64.b64encode(zip_bytes).decode()
        shutil.rmtree(directory_path)
        return zip_base64
    except Exception as e:
        print(f"Error zipping directory: {e}")
        return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        input_number = request.form.get("input_number", type=int)
        unique_list = generate_unique_list(input_number)
        dataset_path = generate_dataset(unique_list, input_number)

        if dataset_path:
            zip_b64 = zip_directory(dataset_path)
            filename = os.path.basename(dataset_path) + ".zip"
            download_url = url_for("download_file", filename=filename)
            return jsonify({"download_url": download_url}), 200
        else:
            return jsonify({"error": "Failed to generate dataset"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/download/<filename>")
def download_file(filename):
    try:
        return send_from_directory(STUDENT_DATASET_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
