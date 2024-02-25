# Dataset Generator for Deep Learning

This project is a Flask-based web application designed for generating custom datasets for deep learning and convolutional neural network assignments. It allows users to input their student ID, upon which it generates a unique dataset for image classification tasks, packages it into a zip file, and provides a download link.

## Features

- **Custom Dataset Generation**: Users can generate datasets by entering their unique student ID.
- **Automatic Dataset Download**: After dataset generation, the user is provided with a link to download their dataset.
- **Secure and Scalable**: Built with Flask, the application is designed to handle multiple requests efficiently.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/GitarthVaishnav/A1App.git
cd A1App
```

2. **Setup Virtual Environment and Install Dependencies**

This project uses Poetry for managing project dependencies. To install Poetry, follow the instructions on the [official website](https://python-poetry.org/docs/#installation).

After installing Poetry, set up the project dependencies by running:

```bash
poetry install
```

This command creates a virtual environment and installs all necessary dependencies.

3. **Configuration**

Before running the application, ensure all configurations are set correctly in `.env` file (you may need to create this file based on `.env.example` if provided).

4. **Running the Application**

Start the Flask application with:

```bash
poetry run flask run
```

The application will be available at `http://localhost:5000`.

## Usage

1. **Access the Web Interface**

Navigate to `http://localhost:5000` in your web browser to access the dataset generator.

2. **Generate Dataset**

Enter your 8-digit student ID in the input form and click the submit button. The application will process your request and provide a download link for your custom dataset.

## Development

To contribute to this project, please create a branch and submit a pull request for review.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask for providing a lightweight and powerful web framework.
- Python community for continuous support and resources.
