# Use an official Python runtime as the base image
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

ENV AzureWebJobsScriptRoot=/home/site/wwwroot AzureFunctionsJobHost__Logging__Console__IsEnabled=true

RUN apt-get update \
    && apt-get install -y iputils-ping \
    && apt-get clean
# Set the working directory in the container
COPY . /home/site/wwwroot

WORKDIR /home/site/wwwroot

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org

# Compile the python files
RUN python -m compileall .
