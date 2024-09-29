# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import training_backend_pb2 as training__backend__pb2


class TrainingTrendsStub(object):
    """---------------------------------------------------------------------------------------------------------------------

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UpdateData = channel.unary_unary(
                '/training_analyser.TrainingTrends/UpdateData',
                request_serializer=training__backend__pb2.Empty.SerializeToString,
                response_deserializer=training__backend__pb2.Empty.FromString,
                )
        self.GetFitnessTrend = channel.unary_unary(
                '/training_analyser.TrainingTrends/GetFitnessTrend',
                request_serializer=training__backend__pb2.Name.SerializeToString,
                response_deserializer=training__backend__pb2.FitnessTrend.FromString,
                )
        self.GetRawTrendData = channel.unary_unary(
                '/training_analyser.TrainingTrends/GetRawTrendData',
                request_serializer=training__backend__pb2.Empty.SerializeToString,
                response_deserializer=training__backend__pb2.RawTrendData.FromString,
                )
        self.GetActivities = channel.unary_unary(
                '/training_analyser.TrainingTrends/GetActivities',
                request_serializer=training__backend__pb2.Empty.SerializeToString,
                response_deserializer=training__backend__pb2.Activities.FromString,
                )


class TrainingTrendsServicer(object):
    """---------------------------------------------------------------------------------------------------------------------

    """

    def UpdateData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFitnessTrend(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetRawTrendData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetActivities(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TrainingTrendsServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'UpdateData': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateData,
                    request_deserializer=training__backend__pb2.Empty.FromString,
                    response_serializer=training__backend__pb2.Empty.SerializeToString,
            ),
            'GetFitnessTrend': grpc.unary_unary_rpc_method_handler(
                    servicer.GetFitnessTrend,
                    request_deserializer=training__backend__pb2.Name.FromString,
                    response_serializer=training__backend__pb2.FitnessTrend.SerializeToString,
            ),
            'GetRawTrendData': grpc.unary_unary_rpc_method_handler(
                    servicer.GetRawTrendData,
                    request_deserializer=training__backend__pb2.Empty.FromString,
                    response_serializer=training__backend__pb2.RawTrendData.SerializeToString,
            ),
            'GetActivities': grpc.unary_unary_rpc_method_handler(
                    servicer.GetActivities,
                    request_deserializer=training__backend__pb2.Empty.FromString,
                    response_serializer=training__backend__pb2.Activities.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'training_analyser.TrainingTrends', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TrainingTrends(object):
    """---------------------------------------------------------------------------------------------------------------------

    """

    @staticmethod
    def UpdateData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/training_analyser.TrainingTrends/UpdateData',
            training__backend__pb2.Empty.SerializeToString,
            training__backend__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetFitnessTrend(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/training_analyser.TrainingTrends/GetFitnessTrend',
            training__backend__pb2.Name.SerializeToString,
            training__backend__pb2.FitnessTrend.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetRawTrendData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/training_analyser.TrainingTrends/GetRawTrendData',
            training__backend__pb2.Empty.SerializeToString,
            training__backend__pb2.RawTrendData.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetActivities(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/training_analyser.TrainingTrends/GetActivities',
            training__backend__pb2.Empty.SerializeToString,
            training__backend__pb2.Activities.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)