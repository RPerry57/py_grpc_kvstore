import grpc
import kvstore_pb2
import kvstore_pb2_grpc


def run_test():
    # Connect to the gRPC server port
    channel = grpc.insecure_channel("localhost:50051")
    stub = kvstore_pb2_grpc.KeyValueServiceStub(channel)

    print("--- 1. Testing SET ---")
    set_resp = stub.Set(
        kvstore_pb2.SetRequest(
            key="user_101", value="Alice Smith", ttl_seconds=10
        )
    )
    print(f"SET Status: {set_resp.success}")

    print("\n--- 2. Testing GET ---")
    get_resp = stub.Get(kvstore_pb2.GetRequest(key="user_101"))
    if get_resp.found:
        print(f"GET Success! Value: {get_resp.value}")
    else:
        print("GET Failed: Key not found")

    print("\n--- 3. Testing DELETE ---")
    del_resp = stub.Delete(kvstore_pb2.DeleteRequest(key="user_101"))
    print(f"DELETE Status: {del_resp.success}")

    print("\n--- 4. Verify DELETE ---")
    get_resp_after = stub.Get(kvstore_pb2.GetRequest(key="user_101"))
    print(f"GET Found: {get_resp_after.found}")


if __name__ == "__main__":
    run_test()