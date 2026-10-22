# High-Throughput Distributed Key-Value Store

A high-performance, thread-safe, in-memory key-value database built in Python using **gRPC** and **Protocol Buffers**. Designed with low-latency concurrent operations, lock-sharding, Write-Ahead Logging (WAL) for durability, and Docker containerization.

---

## Key Technical Features

* **High-Throughput Concurrency:** Uses lock-sharding (16 distinct mutex shards) to eliminate single-lock contention and maximize parallel read/write performance.
* **Crash Recovery & Durability:** Implements an append-only Write-Ahead Log (WAL) with line-buffering to ensure O(1) mutation persistence and instant crash recovery on startup.
* **gRPC & Protocol Buffers API:** Replaces standard JSON/REST interfaces with binary Protocol Buffer serialization over HTTP/2 for sub-millisecond network request latencies.
* **TTL Expiration Engine:** Supports key-level Time-To-Live (TTL) with non-blocking lazy eviction on retrieval paths.
* **Production-Grade Infrastructure:** Fully containerized with Docker, featuring automated .proto compilation within Docker build stages and end-to-end integration tests in pytest.

---

## Project Structure

* `engine.py` — Core storage engine featuring lock-sharding & TTL
* `wal.py` — Write-Ahead Log implementation for durability & replay
* `kvstore.proto` — Protocol Buffer API schema definitions
* `server.py` — gRPC server implementation with thread pool executor
* `client.py` — Sample gRPC client script for CRUD testing
* `test_kvstore.py` — Unit and integration test suite (pytest)
* `Dockerfile` — Multi-stage production Docker build definition
* `requirements.txt` — Project dependencies

---

## Getting Started

### Prerequisites

* Python 3.11+
* Docker Desktop (optional)

### Local Setup

1. Clone the repository and navigate to the project directory:
   git clone https://github.com/your-username/grpc-kvstore.git
   cd grpc-kvstore

2. Set up a virtual environment and install dependencies:
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt

3. Compile Protocol Buffers:
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. kvstore.proto

4. Launch the Server:
   python server.py

5. Run the Client Test Suite (in a separate terminal):
   python client.py

---

## Running with Docker

You can build and launch the application in a single command using Docker:

1. Build the Docker image:
   docker build -t grpc-kvstore .

2. Run the container exposing port 50051:
   docker run -p 50051:50051 --name kvstore-app grpc-kvstore

---

## Automated Testing

Run the test suite covering lock-sharding, TTL expiration, log recovery, and gRPC endpoints:

pytest -v
