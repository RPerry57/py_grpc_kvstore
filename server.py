from concurrent import futures
import grpc
from engine import KeyValueEngine
import kvstore_pb2
import kvstore_pb2_grpc
from wal import WriteAheadLog


class KeyValueServicer(kvstore_pb2_grpc.KeyValueServiceServicer):

    def __init__(self, engine: KeyValueEngine, wal: WriteAheadLog):
        self.engine = engine
        self.wal = wal

    def Set(self, request, context):
        # 1. Write to disk first (WAL)
        self.wal.log_action("SET", request.key, request.value)
        # 2. Update in-memory state
        self.engine.set(request.key, request.value, request.ttl_seconds)
        return kvstore_pb2.SetResponse(success=True)

    def Get(self, request, context):
        val = self.engine.get(request.key)
        if val is None:
            return kvstore_pb2.GetResponse(found=False, value="")
        return kvstore_pb2.GetResponse(found=True, value=val)

    def Delete(self, request, context):
        self.wal.log_action("DELETE", request.key)
        success = self.engine.delete(request.key)
        return kvstore_pb2.DeleteResponse(success=success)

def serve():
    # Step 1: Initialize storage engine and WAL
    engine = KeyValueEngine(num_shards=16)
    wal = WriteAheadLog("wal.log")

    # Step 2: Crash recovery — rebuild memory state from WAL
    wal.recover(engine)

    # Step 3: Start multithreaded gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kvstore_pb2_grpc.add_KeyValueServiceServicer_to_server(
        KeyValueServicer(engine, wal), server
    )
    server.add_insecure_port("[::]:50051")
    print("gRPC Key-Value Store running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()