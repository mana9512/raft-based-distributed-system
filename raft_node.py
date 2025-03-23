from flask import Flask, request, jsonify
import requests
import threading
import time
import random
from flask_cors import CORS

class RaftNode:
    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port
        self.term = 0
        self.state = 'follower'
        self.vote_count = 0
        self.leader_id = None
        self.timeout = random.randint(150, 300) / 1000
        self.last_heartbeat = time.time()
        self.active = False
        self.node_status = {0: False, 1: False, 2: False}
        self.vote_log = {}

        self.app = Flask(__name__)
        CORS(self.app)

        self.app.add_url_rule('/heartbeat', 'heartbeat', self.heartbeat, methods=['POST'])
        self.app.add_url_rule('/request_vote', 'request_vote', self.request_vote, methods=['POST'])
        self.app.add_url_rule('/start_election', 'start_election', self.start_election_ui, methods=['POST'])
        self.app.add_url_rule('/send_heartbeat', 'send_heartbeat', self.send_heartbeat_ui, methods=['POST'])
        self.app.add_url_rule('/get_status', 'get_status', self.get_status, methods=['GET'])

    def start_server(self):
        self.app.run(host="0.0.0.0", port=self.port, threaded=True, use_reloader=False)

    def heartbeat(self):
        data = request.get_json()
        if data and 'term' in data:
            term = data['term']
            if term >= self.term:
                self.term = term
                self.state = 'follower'
                self.last_heartbeat = time.time()
                return jsonify({'success': True})
        return jsonify({'success': False}), 400

    def request_vote(self):
        data = request.get_json()
        if data and 'term' in data and 'candidate_id' in data:
            candidate_id = data['candidate_id']
            if data['term'] > self.term:
                self.term = data['term']
                self.state = 'follower'
                self.vote_log[data['term']] = candidate_id
                return jsonify({'vote_granted': True})
        return jsonify({'vote_granted': False}), 400

    def start_election(self):
        print(f"[Node {self.node_id}] Starting election for term {self.term + 1}")
        self.term += 1
        self.state = 'candidate'
        self.vote_count = 1
        self.leader_id = None
        self.vote_log[self.term] = self.node_id

        for port in range(8000, 8003):
            if port == self.port:
                continue
            try:
                response = requests.post(f"http://127.0.0.1:{port}/request_vote", json={'term': self.term, 'candidate_id': self.node_id}, timeout=1)
                if response.status_code == 200 and response.json().get('vote_granted'):
                    self.vote_count += 1
                    print(f"[Node {self.node_id}] Received vote from Node {port - 8000}")
            except Exception as e:
                print(f"[Node {self.node_id}] Failed to reach Node {port} for vote request: {e}")

        if self.vote_count > 1:
            self.state = 'leader'
            self.leader_id = self.node_id
            print(f"[Node {self.node_id}] Became leader for term {self.term} with {self.vote_count} votes")
            return True
        print(f"[Node {self.node_id}] Election failed. Received {self.vote_count} votes")
        return False

    def send_heartbeat(self):
        self.active = False
        for port in range(8000, 8003):
            if port == self.port:
                continue
            try:
                response = requests.post(f"http://127.0.0.1:{port}/heartbeat", json={'term': self.term}, timeout=1)
                if response.status_code == 200:
                    self.node_status[port - 8000] = True
                    print(f"[Node {self.node_id}] Sent heartbeat to Node {port - 8000}")
                else:
                    self.node_status[port - 8000] = False
            except Exception as e:
                self.node_status[port - 8000] = False
                print(f"[Node {self.node_id}] Heartbeat to Node {port - 8000} failed: {e}")
        self.active = True

    def send_heartbeat_ui(self):
        if self.state == 'leader':
            self.send_heartbeat()
            return jsonify({'status': 'Heartbeat sent', 'active': self.active, 'node_status': self.node_status})
        else:
            return jsonify({'status': 'Not a leader', 'active': False, 'node_status': self.node_status})

    def start_election_ui(self):
        success = self.start_election()
        return jsonify({
            'leader_id': self.leader_id if success else None,
            'status': 'Election completed' if success else 'Election failed',
            'votes': self.vote_count,
            'term': self.term
        })

    def get_status(self):
        return jsonify({
            'node_id': self.node_id,
            'state': self.state,
            'term': self.term,
            'leader_id': self.leader_id,
            'active': self.active,
            'node_status': self.node_status,
            'votes': self.vote_log
        })

    def run(self):
        while True:
            current_time = time.time()
            if self.state == 'follower' and current_time - self.last_heartbeat > self.timeout:
                print(f"[Node {self.node_id}] Timeout occurred. Initiating election.")
                self.start_election()
            elif self.state == 'leader':
                self.send_heartbeat()
                time.sleep(2)
            time.sleep(self.timeout)

def run_node(node_id, port):
    node = RaftNode(node_id, port)
    threading.Thread(target=node.start_server).start()
    node.run()

if __name__ == "__main__":
    import sys
    node_ports = {0: 8000, 1: 8001, 2: 8002}

    if len(sys.argv) == 2:
        try:
            node_id = int(sys.argv[1])
            if node_id not in node_ports:
                print(f"Invalid node ID: {node_id}. Available nodes: {list(node_ports.keys())}")
                sys.exit(1)
            port = node_ports[node_id]
            print(f"Starting Node {node_id} on port {port}...")
            run_node(node_id, port)
        except ValueError:
            print("Please provide a valid integer node ID.")
    else:
        print("No node ID provided. Running all nodes...")
        threads = []
        for node_id, port in node_ports.items():
            thread = threading.Thread(target=run_node, args=(node_id, port))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()