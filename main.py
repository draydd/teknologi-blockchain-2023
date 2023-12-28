# import libraries

import datetime
import hashlib
import json
from flask import Flask, jsonify, request

# 1. Blockchain (Server)
class Blockchain:

    def __init__(self):
        self.chain = []
        # genesis block
        self.create_block(proof = 1, prev_hash = None, proof_of_work = None, hash= None, data = None)

    def create_block(self, proof, prev_hash, proof_of_work, hash, data):
        
        block = {
            'id_block': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_hash,
            'proof_of_work': proof_of_work,
            'hash': hash,
            'data': data
        }
        
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof, hash_operation
    
    def get_hash(self, block):
        hash_operation = hashlib.sha256(json.dumps(block).encode()).hexdigest()
        return hash_operation
    
    def is_chain_valid(self):
        prev_block = self.chain[0]
        now_index = 1
        while now_index < len(self.chain):
            now_block = self.chain[now_index]

            # 1. cek apakah hash now block = prev hash 
            prev_hash = prev_block['hash']
            if prev_hash != now_block['prev_hash']:
                return False

            # 2. cek apakah proof of worknya true
            now_proof = now_block['proof']
            prev_proof = prev_block['proof']
            hash_operation = hashlib.sha256(str(now_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False

            prev_block = now_block
            now_index += 1
        return True


# 2. Web Aplikasi untuk Testing
app = Flask(__name__)

blockchain = Blockchain()

# buat endpoint 
@app.route("/get_chain", methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route("/mining", methods=['GET'])
def mining():
    prev_block = blockchain.get_last_block()
    # get prev proof 
    prev_proof = prev_block['proof']
    proof, proof_of_work = blockchain.proof_of_work(prev_proof) 
    # get prev hash 
    prev_hash = prev_block['hash']
    hash = None
    
    data = "mined block"
    # create block 
    created_block = blockchain.create_block(proof, prev_hash, proof_of_work, hash, data=data)
    block = blockchain.get_last_block()
    hash = blockchain.get_hash(block)
    block['hash'] = hash
    response = {
        'message': "Blockchain is successfully created",
        'created block': created_block
    }
    return jsonify(response), 200

@app.route("/create", methods=['POST'])
def create_block():
    data = request.form

    prev_block = blockchain.get_last_block()
    # get prev proof 
    prev_proof = prev_block['proof']
    proof, proof_of_work = blockchain.proof_of_work(prev_proof) 
    # get prev hash 
    prev_hash = prev_block['hash']
    hash = None
    # create block 
    created_block = blockchain.create_block(proof, prev_hash, proof_of_work, hash, data['data'])
    block = blockchain.get_last_block()
    hash = blockchain.get_hash(block)
    block['hash'] = hash
    response = {
        'message': "Blockchain is successfully created",
        'created block': created_block
    }
    return jsonify(response), 200

@app.route("/validity", methods=['GET'])
def validity():
    valid = blockchain.is_chain_valid()
    if valid:
        response = {'message': 'Blockchain anda valid'}
    else:
        response = {'message': 'Blockchain anda tidak valid'}
    return jsonify(response), 200

@app.route("/modify_block", methods=["PUT"])
def modify_block():
    block = blockchain.get_last_block()
    block['prev_hash'] = block['hash']
    response = {
        'message': "Blockchain anda telah dimodifikasi!"
    }
    return jsonify(response), 200

app.run()