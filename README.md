# training_analyser
## Generate protos
### Python
python -m grpc_tools.protoc -I../proto --python_out=. --grpc_python_out=. ../proto/training_backend.proto
### Swift
protoc -I ../proto --grpc-swift_out=. ../proto/training_backend.proto
protoc -I ../proto --grpc-swift_out=. ../proto/training_backend.proto
