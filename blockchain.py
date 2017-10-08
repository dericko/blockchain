import hashlib
import json

from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create init block
        self.new_block(previous_hash=1, proof=100)

    """
    Create new block and add it to chain

    :param proof: <int> The proof given by the Proof of Work algorithm
    :param previous_hash: (Optional) <str> Hash of previous Block
    :return: <dict> New Block
    """
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block)
        }

        self.current_transactions = []

        self.chain.append(block)
        return block

    """
    Create new transaction and add it to list of transactions

    :param sender: <str> Address of the Sender
    :param recipient: <str> Address of the Recipient
    :param amount: <int> Amount
    :return: <int> The index of the Block that will hold this transaction
    """
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        print("current_transactions")
        print(self.current_transactions)

        return self.last_block['index'] + 1

    """
    Simple Proof of Work Algorithm:
     - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
     - p is the previous proof, and p' is the new proof

    :param last_proof: <int>
    :return: <int>
    """
    def proof_of_work(self, last_proof):
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    """
    Add a new node to the list of nodes

    :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
    :return: None
    """
    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    """
    Determine if a given blockchain is valid

    :param chain: <list> A blockchain
    :return: <bool> True if valid, False if not
    """
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n--------\n")

            # Check correct hash
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check proof of work
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    """
    This is our Consensus Algorithm, it resolves conflicts
    by replacing our chain with the longest one in the network.
    :return: <bool> True if our chain was replaced, False if not
    """
    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None

        # Only check longer chains
        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace current chain with new/longer/valid chain
        if new_chain:
            self.chain = new_chain
            return True

        return False

    # Return the last block in the chain
    @property
    def last_block(self):
        return self.chain[-1]

    """
    Creates a SHA-256 hash of a Block
    :param block: <dict> Block
    :return: <str>
    """
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode() # sorted
        return hashlib.sha256(block_string).hexdigest()

    """
    Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?

    :param last_proof: <int> Previous Proof
    :param proof: <int> Current Proof
    :return: <bool> True if correct, False if not.
    """
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
