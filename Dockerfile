# Use lightweight official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into container
COPY engine.py wal.py server.py kvstore.proto ./

# Compile protobuf files inside container build layer
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. kvstore.proto

# Expose gRPC default port
EXPOSE 50051

# Run unbuffered Python server
CMD ["python", "-u", "server.py"]