import sys
import random
import concurrent.futures
import threading
import time

import grpc

import raft_pb2_grpc as pb2_grpc
import raft_pb2 as pb2

#
# constants
#

# [HEARTBEAT_DURATION, ELECTION_DURATION_FROM, ELECTION_DURATION_TO] = [x*10 for x in [50, 150, 300]]
[HEARTBEAT_DURATION, ELECTION_DURATION_FROM, ELECTION_DURATION_TO] = [x for x in [50, 150, 300]]

#
# global state
#

is_terminating = False
is_suspended = False
state_lock = threading.Lock()
election_timer_fired = threading.Event()
heartbeat_events = {}
state = {
    'election_campaign_timer': None,
    'election_timeout': -1,
    'type': 'follower',
    'nodes': None,
    'term': 0,
    'vote_count': 0,
    'voted_for_id': -1,
    'leader_id': -1,
    'commitIndex': 0,
    'lastApplied': 0
}
log = [{'term':-1,'command':'-1' }]
storage = {}
nextIndex = []
matchIndex = []
# for debugging
START_TIME = time.time()
def log_prefix():
    time_since_start = '{:07.3f}'.format(time.time() - START_TIME)
    return f"{state['term']}\t{time_since_start}\t{state['type']}\t[id={state['id']} leader_id={state['leader_id']} vote_count={state['vote_count']} voted_for={state['voted_for_id']}] "

#
# election timer functions
#

def select_election_timeout():
    return random.randrange(ELECTION_DURATION_FROM, ELECTION_DURATION_TO)*0.001

# def fire_election_timer(id):
#     state['current_timer_id'] = id
#     election_timer_fired.set()

def reset_election_campaign_timer():
    stop_election_campaign_timer()
    state['election_campaign_timer'] = threading.Timer(state['election_timeout'], election_timer_fired.set)
    state['election_campaign_timer'].start()

def select_new_election_timeout_duration():
    state['election_timeout'] = select_election_timeout()

def stop_election_campaign_timer():
    if state['election_campaign_timer']:
        state['election_campaign_timer'].cancel()

#
# elections
#
def split_func(str):
    return str.split('=')

def start_election():
    with state_lock:
        state['type'] = 'candidate'
        state['leader_id'] = -1
        state['term'] += 1
        # vote for ourselves
        state['vote_count'] = 1
        state['voted_for_id'] = state['id']

    print(f"I am a candidate. Term: {state['term']}")
    for id in state['nodes'].keys():
        if id != state['id']:
            t = threading.Thread(target=request_vote_worker_thread, args=(id,))
            t.start()
    # now RequestVote threads have started,
    # lets set a timer for the end of the election
    reset_election_campaign_timer()

def has_enough_votes():
    required_votes = (len(state['nodes'])//2) + 1
    return state['vote_count'] >= required_votes

def finalize_election():
    global nextIndex
    stop_election_campaign_timer()
    with state_lock:
        if state['type'] != 'candidate':
            return

        if has_enough_votes():
            # become a leader
            state['type'] = 'leader'
            state['leader_id'] = state['id']
            state['vote_count'] = 0
            state['voted_for_id'] = -1
            #Reset nextIndex to maxsize of log if I become leader
            nextIndex = [len(log) for _ in nodes]
            start_heartbeats()
            print("Votes received")
            print(f"I am a leader. Term: {state['term']}")
            return
        # if election was unsuccessful
        # then pick new timeout duration
        become_a_follower()
        select_new_election_timeout_duration()
        reset_election_campaign_timer()

def become_a_follower():
    global matchIndex,nextIndex
    if state['type'] != 'follower':
        print(f"I am a follower. Term: {state['term']}")
    state['type'] = 'follower'
    state['voted_for_id'] = -1
    state['vote_count'] = 0
    #Reset value if I become follower
    matchIndex = [0 for _ in nodes]
    nextIndex = [1 for _ in nodes]
    # state['leader_id'] = -1

#
# hearbeats
#

def start_heartbeats():
    for id in heartbeat_events:
        heartbeat_events[id].set()

#
# thread functions
#
        
def request_vote_worker_thread(id_to_request):
    ensure_connected(id_to_request)
    (_, _, stub) = state['nodes'][id_to_request]
    try:
        ind = len(log)-1
        resp = stub.RequestVote(pb2.VoteArgs(term=state['term'], node_id=state['id'],llIndex=ind,llTerm=log[ind]['term']), timeout=0.1)

        with state_lock:
            # if requested node replied for too long,
            # and during this time candidate stopped
            # being a candidate, then do nothing
            if state['type'] != 'candidate' or is_suspended:
                return

            if state['term'] < resp.term:
                state['term'] = resp.term
                become_a_follower()
                reset_election_campaign_timer()
            elif resp.result:
                state['vote_count'] += 1
        
        # got enough votes, no need to wait for the end of the timeout
        if has_enough_votes():
            finalize_election()
    except grpc.RpcError:
        reopen_connection(id_to_request)

def election_timeout_thread():
    while not is_terminating:
        if election_timer_fired.wait(timeout=0.5):
            election_timer_fired.clear()
            if is_suspended:
                continue

            # election timer just fired
            if state['type'] == 'follower':
                # node didn't receive any heartbeats on time
                # that's why it should become a candidate
                print("The leader is dead")
                start_election()
            elif state['type'] == 'candidate':
                # okay, election is over
                # we need to count voutes
                finalize_election()
            # if somehow we got here while being a leader,
            # then do nothing

# Special thread to check changes in commitIndex and apply log[lastApplied] if needed 
def update_index_thread():
    global log
    while not is_terminating:
        if state['type'] == 'leader':
            MI =  max(matchIndex)
            if MI > state['commitIndex'] and matchIndex.count(MI) >= (len(state['nodes'])//2) + 1 and log[MI]['term'] == state['term']:
                state['commitIndex'] = MI

        if state['commitIndex'] > state['lastApplied']:
            state['lastApplied'] += 1
            func = split_func(log[state['lastApplied']]['command'])
            storage[func[0]] = func[1]
            print(storage)

def heartbeat_thread(id_to_request):
    global matchIndex,nextIndex,log
    while not is_terminating:
        try:
            if heartbeat_events[id_to_request].wait(timeout=0.5):
                heartbeat_events[id_to_request].clear()

                if (state['type'] != 'leader') or is_suspended:
                    continue

                ensure_connected(id_to_request)
                (_, _, stub) = state['nodes'][id_to_request]
                # Some changes. Adding parser to new entries
                lInd = nextIndex[id_to_request]-1
                entr = [str(x['term'])+'||'+x['command'] for x in log[nextIndex[id_to_request]:]]
                resp = stub.AppendEntries(pb2.NodeArgs(term=state['term'], node_id=state['id'], plIndex=lInd, plTerm=log[lInd]['term'],entries=entr,leaderCommit=state['commitIndex']), timeout=0.100)

                if (state['type'] != 'leader') or is_suspended:
                    continue

                with state_lock:
                    if state['term'] < resp.term:
                        reset_election_campaign_timer()
                        state['term'] = resp.term
                        become_a_follower()
                    # Additional conditions
                    # If we got False not because of term inequation - decrease nextIndex and matchIndex, as there are log inconsistency
                    elif not resp.result:
                        nextIndex[id_to_request] = 1 if nextIndex[id_to_request] <= 2 else nextIndex[id_to_request] - 1
                        matchIndex[id_to_request] = 0 if matchIndex[id_to_request] <= 1 else matchIndex[id_to_request] - 1
                    # If we got true result, update nextIndex and matchIndex
                    elif len(entr) > 0:
                        nextIndex[id_to_request] += len(entr)
                        matchIndex[id_to_request] += len(entr)
                threading.Timer(HEARTBEAT_DURATION*0.001, heartbeat_events[id_to_request].set).start()
        except grpc.RpcError:
          reopen_connection(id_to_request)

#
# gRPC server handler
#

# helpers that sets timers running again
# when suspend has ended
def wake_up_after_suspend():
    global is_suspended
    is_suspended = False
    if state['type'] == 'leader':
        start_heartbeats()
    else:
        reset_election_campaign_timer()

class Handler(pb2_grpc.RaftNodeServicer):
    def RequestVote(self, request, context):
        global is_suspended
        if is_suspended:
            return
        
        reset_election_campaign_timer()
        with state_lock:
            reply = {'result': False, 'term': state['term']}
            if state['term'] < request.term:
                state['term'] = request.term
                become_a_follower()
            if state['term'] == request.term:
                # Condition checks that only the node with the most complete logs can become the leader.
                ind = len(log)-1
                if state['voted_for_id'] == -1 and request.llIndex >= ind and not (request.llIndex < ind and log[ind]['term'] != request.llTerm):
                    become_a_follower()
                    state['voted_for_id'] = request.node_id
                    reply = {'result': True, 'term': state['term']}
                    print(f"Voted for node {state['voted_for_id']}")
            return pb2.ResultWithTerm(**reply)

    def AppendEntries(self, request, context):
        global is_suspended,log
        if is_suspended:
            return

        reset_election_campaign_timer()

        with state_lock:
            reply = {'result': False, 'term': state['term']}
            if state['term'] < request.term:
                state['term'] = request.term
                become_a_follower()
            if state['term'] == request.term:
                state['leader_id'] = request.node_id
                if len(request.entries) > 0:
                    #Check if plIndex is not in array, return false
                    if request.plIndex != 0 and request.plIndex >= len(log):
                        return reply
                    
                    # Parse
                    entr = [{'term':int(x),'command':y} for x,y in [m.split('||') for m in request.entries]]
                    # If last log entry on these server is prevIndex on leader: append entries
                    if request.plIndex == len(log)-1 or request.plIndex == 0:
                        log += entr
                    # If we get conflict entries, do magic
                    elif log[request.plIndex+1]['term'] != entr[0]['term']:
                        print(log[:request.plIndex+1])
                        log = log[:request.plIndex+1]
                        log += entr
                #upadte commitIndex of server from leaderCommit
                if request.leaderCommit > state['commitIndex']:
                    state['commitIndex'] = min(request.leaderCommit,len(log)-1)   
                reply = {'result': True, 'term': state['term']}
            return pb2.ResultWithTerm(**reply)

    def GetLeader(self, request, context):
        global is_suspended
        if is_suspended:
            return

        (host, port, _) = state['nodes'][state['leader_id']]
        reply = {'leader_id': state['leader_id'], 'leader_addr': f"{host}:{[port]}"}
        return pb2.LeaderResp(**reply)

    def Suspend(self, request, context):
        global is_suspended
        if is_suspended:
            return

        is_suspended = True
        threading.Timer(request.duration, wake_up_after_suspend).start()
        return pb2.NoArgs()

    def GetVal(self, request, context):
        global is_suspended
        if is_suspended:
            return
        reply = {'success': False, 'value': 'None'}
        try:
            val = storage[request.key]
            reply['value'],reply['success'] = val,True
        except:
            pass
        return pb2.GetResp(**reply)
    
    def SetVal(self, request, context):
        global is_suspended
        if is_suspended:
            return
        reply = {'success': True}
        # If leader, append to log new command
        if state['type'] == 'leader':
            log.append({'term':state['term'],'command':f'{request.key}={request.val}'})
        # If follower, raise request to leader
        elif state['type'] == 'follower':
            ensure_connected(state['leader_id'])
            (_, _, stub) = state['nodes'][state['leader_id']]
            resp = stub.SetVal(pb2.SetMsg(key=request.key, val=request.val))
            reply['success'] = resp.success
        return pb2.SetResp(**reply)

#
# other
#

def ensure_connected(id):
    if id == state['id']:
        raise "Shouldn't try to connect to itself"
    (host, port, stub) = state['nodes'][id]
    if not stub:
        channel = grpc.insecure_channel(f"{host}:{port}")
        stub = pb2_grpc.RaftNodeStub(channel)
        state['nodes'][id] = (host, port, stub)

def reopen_connection(id):
    if id == state['id']:
        raise "Shouldn't try to connect to itself"
    (host, port, stub) = state['nodes'][id]
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = pb2_grpc.RaftNodeStub(channel)
    state['nodes'][id] = (host, port, stub)

def start_server(state):
    (ip, port, _) = state['nodes'][state['id']]
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_RaftNodeServicer_to_server(Handler(), server)
    server.add_insecure_port(f"{ip}:{port}")
    server.start()
    return server

def main(id, nodes):
    global nextIndex, matchIndex
    election_th = threading.Thread(target=election_timeout_thread)
    election_th.start()

    index_th = threading.Thread(target=update_index_thread)
    index_th.start()
    hearbeat_threads = []
    for node_id in nodes:
        if id != node_id:
            heartbeat_events[node_id] = threading.Event()
            t = threading.Thread(target=heartbeat_thread, args=(node_id,))
            t.start()
            hearbeat_threads.append(t)

    state['id'] = id
    state['nodes'] = nodes
    state['type'] = 'follower'
    state['term'] = 0

    # Initial values for matchIndex and nextIndex
    matchIndex = [0 for _ in nodes]
    nextIndex = [1 for _ in nodes]

    server = start_server(state)
    (host, port, _) = nodes[id]
    print(f"The server starts at {host}:{port}")
    print(f"I am a follower. Term: 0")
    select_new_election_timeout_duration()
    reset_election_campaign_timer()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        global is_terminating
        is_terminating = True
        server.stop(0)
        print("Shutting down")

        election_th.join()
        index_th.join()
        [t.join() for t in hearbeat_threads]



if __name__ == '__main__':
    [id] = sys.argv[1:]
    nodes = None
    with open("config.conf", 'r') as f:
        line_parts = map(lambda line: line.split(),f.read().strip().split("\n"))
        nodes = dict([(int(p[0]), (p[1], int(p[2]), None)) for p in line_parts])
        print(list(nodes))
    main(int(id), nodes)