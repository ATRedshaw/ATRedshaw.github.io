# Best Practices for MLOps with Docker

Containerization is crucial for reproducible Machine Learning pipelines. Docker allows you to package your code, dependencies, and environment into a single unit that runs consistently across different machines.

## Why Docker for ML?

- **Reproducibility**: No more "it works on my machine" issues.
- **Portability**: deploy anywhere—on-premise, AWS, Azure, or GCP.
- **Scalability**: Easily spin up multiple instances of your model inference service.

## Creating a Dockerfile

Here is a simple `Dockerfile` for a Python-based ML application:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "app.py"]
```

## Best Practices

1. **Keep images small**: Use slim base images (e.g., `python:3.9-slim`) and clean up temporary files.
2. **Use multi-stage builds**: separate build dependencies from runtime dependencies.
3. **Pin versions**: Always pin package versions in `requirements.txt` to ensure consistency.

## Conclusion

Adopting Docker in your MLOps workflow significantly smooths the path from research to production.
