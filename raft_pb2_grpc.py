# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import raft_pb2 as raft__pb2


class RaftNodeStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RequestVote = channel.unary_unary(
                '/RaftNode/RequestVote',
                request_serializer=raft__pb2.VoteArgs.SerializeToString,
                response_deserializer=raft__pb2.ResultWithTerm.FromString,
                )
        self.AppendEntries = channel.unary_unary(
                '/RaftNode/AppendEntries',
                request_serializer=raft__pb2.NodeArgs.SerializeToString,
                response_deserializer=raft__pb2.ResultWithTerm.FromString,
                )
        self.GetLeader = channel.unary_unary(
                '/RaftNode/GetLeader',
                request_serializer=raft__pb2.NoArgs.SerializeToString,
                response_deserializer=raft__pb2.LeaderResp.FromString,
                )
        self.Suspend = channel.unary_unary(
                '/RaftNode/Suspend',
                request_serializer=raft__pb2.DurationArgs.SerializeToString,
                response_deserializer=raft__pb2.NoArgs.FromString,
                )
        self.GetVal = channel.unary_unary(
                '/RaftNode/GetVal',
                request_serializer=raft__pb2.GetMsg.SerializeToString,
                response_deserializer=raft__pb2.GetResp.FromString,
                )
        self.SetVal = channel.unary_unary(
                '/RaftNode/SetVal',
                request_serializer=raft__pb2.SetMsg.SerializeToString,
                response_deserializer=raft__pb2.SetResp.FromString,
                )


class RaftNodeServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RequestVote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AppendEntries(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLeader(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Suspend(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetVal(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetVal(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RaftNodeServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RequestVote': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestVote,
                    request_deserializer=raft__pb2.VoteArgs.FromString,
                    response_serializer=raft__pb2.ResultWithTerm.SerializeToString,
            ),
            'AppendEntries': grpc.unary_unary_rpc_method_handler(
                    servicer.AppendEntries,
                    request_deserializer=raft__pb2.NodeArgs.FromString,
                    response_serializer=raft__pb2.ResultWithTerm.SerializeToString,
            ),
            'GetLeader': grpc.unary_unary_rpc_method_handler(
                    servicer.GetLeader,
                    request_deserializer=raft__pb2.NoArgs.FromString,
                    response_serializer=raft__pb2.LeaderResp.SerializeToString,
            ),
            'Suspend': grpc.unary_unary_rpc_method_handler(
                    servicer.Suspend,
                    request_deserializer=raft__pb2.DurationArgs.FromString,
                    response_serializer=raft__pb2.NoArgs.SerializeToString,
            ),
            'GetVal': grpc.unary_unary_rpc_method_handler(
                    servicer.GetVal,
                    request_deserializer=raft__pb2.GetMsg.FromString,
                    response_serializer=raft__pb2.GetResp.SerializeToString,
            ),
            'SetVal': grpc.unary_unary_rpc_method_handler(
                    servicer.SetVal,
                    request_deserializer=raft__pb2.SetMsg.FromString,
                    response_serializer=raft__pb2.SetResp.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'RaftNode', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RaftNode(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RequestVote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RaftNode/RequestVote',
            raft__pb2.VoteArgs.SerializeToString,
            raft__pb2.ResultWithTerm.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AppendEntries(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RaftNode/AppendEntries',
            raft__pb2.NodeArgs.SerializeToString,
            raft__pb2.ResultWithTerm.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetLeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RaftNode/GetLeader',
            raft__pb2.NoArgs.SerializeToString,
            raft__pb2.LeaderResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Suspend(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RaftNode/Suspend',
            raft__pb2.DurationArgs.SerializeToString,
            raft__pb2.NoArgs.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetVal(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RaftNode/GetVal',
            raft__pb2.GetMsg.SerializeToString,
            raft__pb2.GetResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetVal(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RaftNode/SetVal',
            raft__pb2.SetMsg.SerializeToString,
            raft__pb2.SetResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
