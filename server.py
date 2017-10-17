import sys
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain

# Main
app = Flask(__name__)
host = "0.0.0.0"
port = len(sys.argv) > 1 and sys.argv[1] or 5000

# Globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # Do work
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Give me a coin!
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    block = blockchain.new_block(proof)

    response = {
        'message': "New block forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    print("request.get_json()")
    print(request.get_json())

    required = ['sender', 'recipient', 'amount']
    print("values")
    print(values)
    print("required")
    print(required)
    if not all(k in values for k in required):
        return 'Error: Missing values', 400

    # Create new transaction
    index = blockchain.new_transaction(values['sender'],
                                       values['recipient'],
                                       values['amount'])

    response = {'message': f'Transaction added to block{index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Invalid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)
        # Register self with other node
        # this_node = f'{host}:{port}'
        # new_nodes = nodes[:]
        # new_nodes.remove(node)
        # new_nodes.append(this_node)
        # requests.post(
        #     f'http://{node}/nodes/register/sync',
        #     data = {'nodes':new_nodes},
        # )
        #
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201


@app.route('/nodes/register/sync', methods=['POST'])
def register_ping():
    print("register_ping")
    values = request.get_json()
    print("values")
    print(values)
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Invalid list of nodes", 400
    print("nodes")
    print(nodes)
    for node in nodes:
        blockchain.register_node(node)
    print("Registered")
    return jsonify("OK"), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    was_replaced = blockchain.resolve_conflicts()

    if was_replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain,
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain,
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host=host, port=port)
