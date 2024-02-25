# Deployment Guide for Flask Application on AWS EC2

This guide covers the deployment of a Flask application on a free tier AWS EC2 Ubuntu instance using Poetry for dependency management and Gunicorn as the WSGI HTTP server.

## Setting Up AWS EC2 Instance

1. **Create an AWS Account** and log in to the AWS Management Console.
2. **Launch an EC2 Instance**:
   - Choose an **Ubuntu Server** AMI (e.g., Ubuntu Server 20.04 LTS).
   - Select the `t2.micro` instance type for the AWS Free Tier.
   - Configure instance and storage settings as needed.
   - Add security group rules to allow SSH (port 22) and HTTP (port 8080 or your desired port).
   - Launch the instance and select or create a new key pair for SSH access.

## Preparing the EC2 Environment

SSH into your EC2 instance using the public DNS or IP address and your key pair:

```bash
ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-dns
```

Update the system and install necessary packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.9
sudo apt install python3-pip python3-dev git -y
```

Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Add Poetry to the system's PATH by including it in your `~/.profile` or `~/.bashrc` file:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
source ~/.profile
```

## Setting Up Your Flask Application

Clone your Flask application repository and navigate into the project directory:

```bash
git clone https://github.com/GitarthVaishnav/A1App.git
cd A1App
```

Install the project dependencies using Poetry:

```bash
poetry install
```

## Running the Application as a Module

To run your application as a module, ensure it is structured properly with an `__init__.py` file in your application directory. Adjust your module path as necessary in the command below:

```bash
poetry run python -m dlcnn_a1_dataset_generator
```

## Configuring Gunicorn to Serve Your Flask App

Instead of directly serving your Flask app in production, use Gunicorn for better performance and reliability.

Create a Gunicorn systemd service file for your application:

```bash
sudo nano /etc/systemd/system/yourapp.service
```

Add the following configuration, adjusting paths and names as necessary:

```ini
[Unit]
Description=Gunicorn instance to serve my Flask app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/your-flask-app
Environment="PATH=/home/ubuntu/.local/bin"
# Adjust the ExecStart command to reference the app module and Flask instance
ExecStart=/home/ubuntu/.local/bin/poetry run gunicorn -w 3 -b 0.0.0.0:8080 'app:dlcnn_a1_datagen_app'

[Install]
WantedBy=multi-user.target
```

Note: Replace `'app:dlcnn_a1_datagen_app'` with the appropriate import path to your Flask application factory function if it's named differently.

Enable and start the Gunicorn service:

```bash
sudo systemctl enable yourapp
sudo systemctl start yourapp
```

Check the status to ensure it's running without issues:

```bash
sudo systemctl status yourapp
```

## Finalizing Deployment

- **Adjust EC2 Security Groups**: Make sure your EC2 instance's security group allows traffic on the port Gunicorn is configured to use (e.g., 8080).
- **Access Your Application**: Your Flask application should now be accessible via your EC2 instance's public IP address or DNS name on the configured port.

## Security and Maintenance

- Regularly update your system and Python dependencies for security and performance.
- Consider setting up a domain name, SSL/TLS certificates, and a reverse proxy for additional security and reliability in production environments.
