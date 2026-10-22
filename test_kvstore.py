import os
import time
import pytest
import grpc
from concurrent import futures

from engine import KeyValueEngine
from wal import WriteAheadLog
import kvstore_pb2
import kvstore_pb2_grpc
from server import KeyValueServicer


# ==========================================
# Unit Tests: KeyValueEngine
# ==========================================

def test_engine_set_get_delete():
    engine = KeyValueEngine(num_shards=4)
    
    # Test Set & Get
    engine.set("user:1", "Alice")
    assert engine.get("user:1") == "Alice"
    
    # Test Delete
    assert engine.delete("user:1") is True
    assert engine.get("user:1") is None
    assert engine.delete("user:1") is False


def test_engine_ttl_expiration():
    engine = KeyValueEngine(num_shards=4)
    
    # Set key with 1 second TTL
    engine.set("temp_key", "val", ttl_seconds=1)
    assert engine.get("temp_key") == "val"
    
    # Sleep to allow expiration
    time.sleep(1.1)
    assert engine.get("temp_key") == "None" or engine.get("temp_key") is None


# ==========================================
# Unit Tests: Write-Ahead Log & Recovery
# ==========================================

def test_wal_and_recovery(tmp_path):
    log_file = tmp_path / "test_wal.log"
    wal = WriteAheadLog(str(log_file))
    
    # Perform mutations
    wal.log_action("SET", "k1", "v1")
    wal.log_action("SET", "k2", "v2")
    wal.log_action("DELETE", "k1")
    
    # Recover into a fresh engine instance
    new_engine = KeyValueEngine(num_shards=4)
    wal.recover(new_engine)
    
    assert new_engine.get("k1") is None
    assert new_engine.get("k2") == "v2"


# ==========================================
# Integration Tests: gRPC Server
# ==========================================

@pytest.fixture(scope="module")
def grpc_server(tmp_path_factory):
    """Fixture that starts a real gRPC server on a temporary port for testing."""
    test_dir = tmp_path_factory.mktemp("grpc_test")
    wal_path = str(test_dir / "test_wal.log")
    
    engine = KeyValueEngine(num_shards=4)
    wal = WriteAheadLog(wal_path)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    kvstore_pb2_grpc.add_KeyValueServiceServicer_to_server(
        KeyValueServicer(engine, wal), server
    )
    
    # Use ephemeral port 0 to bind to an open port automatically
    port = server.add_insecure_port("localhost:0")
    server.start()
    
    channel = grpc.insecure_channel(f"localhost:{port}")
    stub = kvstore_pb2_grpc.KeyValueServiceStub(channel)
    
    yield stub
    
    server.stop(grace=None)


def test_grpc_end_to_end(grpc_server):
    stub = grpc_server
    
    # SET
    set_res = stub.Set(kvstore_pb2.SetRequest(key="grpc_k1", value="grpc_v1"))
    assert set_res.success is True
    
    # GET
    get_res = stub.Get(kvstore_pb2.GetRequest(key="grpc_k1"))
    assert get_res.found is True
    assert get_res.value == "grpc_v1"
    
    # DELETE
    del_res = stub.Delete(kvstore_pb2.DeleteRequest(key="grpc_k1"))
    assert del_res.success is True