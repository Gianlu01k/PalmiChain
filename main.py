#imports
from datetime import datetime
import hashlib
import pickle
import random
import string

#init
current_txs = [] #pending transactions
current_supply = 0
current_available = 0
wallets = []

#class Transaction and transaction methods
class Transaction:

    def __init__(self, sender, recipient, amount, description, timestamp):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.description = description
        self.timestamp = timestamp

    def validate(self):
        if self.amount < 0:
            return False
        return True


def create_tx(sender, recipient, amount, description):
    global current_supply
    global current_available
    transaction = Transaction(
        sender, recipient, amount, description, datetime.now())

    if transaction.validate():
        current_txs.append(transaction)
        current_supply = current_supply - amount
        current_available = current_available + amount
        return True
    return False

#class Block and block methods
class Block:

    def __init__(self, index, transaction, nonce, previous_hash):
        self.index = index
        self.transaction = transaction
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    #gets hash block
    def hash_block(self):
        sha = hashlib.sha256()
        return sha.hexdigest()

def add_block(block):
    global current_txs
    last_block = chain[len(chain)-1]
    if validate_block(block, last_block):
        chain.append(block)
        del current_txs
        current_txs = []
        with open('ledger', 'wb') as dl: #write genesis block on ledger file
            pickle.dump(chain, dl)
        return True
    return False

#mining and validation
def mine(reward_address):
    global current_supply
    global current_available
    last_block = chain[len(chain)-1]
    index = last_block.index + 1
    previous_hash = last_block.hash

    nonce = generate_pow(last_block)

    if create_tx('0', reward_address, reward_amount, 'mine reward') == False:
        print('Error rewarding')
    else:
        block = Block(index, current_txs, nonce, previous_hash)
        current_supply = current_supply - reward_amount
        current_available = current_available + reward_amount
        #print(len(block.transaction))
        if add_block(block):
            return chain[len(chain)-1]
        return None

def validate_pow(last_nonce, last_hash, nonce):
    sha = hashlib.sha256(f'{last_nonce}{last_hash}{nonce}'.encode())
    return sha.hexdigest()[:4] == '0000'

def generate_pow(block):
    last_nonce = block.nonce
    last_hash = block.hash
    nonce = 0
    while not validate_pow(last_nonce, last_hash, nonce):
        nonce += 1
    return nonce

def validate_block(current_block, previous_block):
    if current_block.index != previous_block.index + 1:
        return False
    
    if current_block.previous_hash != previous_block.hash:
        return False

    if current_block.hash != current_block.hash_block():
        return False

    if not validate_pow(previous_block.nonce, previous_block.hash, current_block.nonce):
        return False
        
    return True

#wallet management
class Wallet:

    def __init__(self, address, private_key, balance):
        self.address = address
        self.private_key = private_key
        self.balance = balance

def get_random_string():
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(8))
    return result_str

#visualize methods (for test)
def print_pending_tx(index):
    if len(current_txs) != 0:
         print("Sender: %s\n, Recipient: %s\n, Amount: %f\n, Data: %s\n, Date: %s\n" % (current_txs[index].sender, current_txs[index].recipient, current_txs[index].amount, current_txs[index].description, current_txs[index].timestamp))
    else:
        print('Empty list')
        print(len(current_txs))

def print_block(block):
    print("Index :%d, Nonce: %d, Previous Hash: %s" % (block.index, block.nonce, block.previous_hash))
    print("Transactions:")
    for i in range(0, len(block.transaction)):
        print("Sender: %s\n, Recipient: %s\n, Amount: %f\n, Data: %s\n, Date: %s\n" % (block.transaction[i].sender, block.transaction[i].recipient, block.transaction[i].amount, block.transaction[i].description, block.transaction[i].timestamp))

def print_chain():
    print('<---------------------GENESIS_BLOCK--------------------->')
    for x in range(0, len(chain)):
        print_block(chain[x])
        if x != len(chain)-1:
            print('<---------------------NEXT_BLOCK------------------------>')
        else:
            print('<---------------------END_BLOCK------------------------->')

def print_wallets():
    for x in wallets:
        print("Address: %s,\nPrivate Key: %s, \nBalance: %s PLM" % (x.address, x.private_key, x.balance))

#create blockchain (genesis block to call first time)
def create_genesis():
    genesis_block = Block(0, [], 0 , '63N3515')
    chain.append(genesis_block)
    with open('ledger', 'wb') as dl: #write genesis block on ledger file
        pickle.dump(chain, dl)

#read and write methods
def read_chain():
    with open('ledger', 'rb') as dl:
        chain = pickle.load(dl)
    return chain

def read_wallets():
    with open('wallets', 'rb') as wall:
        wallets = pickle.load(wall)
    return wallets   

def save_wallet():
    with open('wallets', 'wb') as wll: #write genesis block on ledger file
        pickle.dump(wallets, wll)

def update_balance():
    f= open("balance.txt","w+")
    f.write("Blockchain name: PalmiChain")
    f.write("\n")
    f.write("Cryptocoin name: palmicoin(PLM)")
    f.write("\n")
    f.write("Max supply:")
    f.write("\n")
    f.write("1000000000.000000")
    f.write("\n")
    f.write("Current supply:")
    f.write("\n")
    f.write("%f" % (current_supply))
    f.write("\n")
    f.write("Available supply:")
    f.write("\n")
    f.write("%f" % (current_available))
    f.write("\n")
    f.write("Reward amount(PLM):")
    f.write("\n")
    f.write("2000.000000") 
    f.close()   

#main (node app)
#create_genesis()
chain = read_chain() #blockchain
wallets =  read_wallets() #wallets, private keys and amounts
f=open("balance.txt", "r")
if f.mode == 'r':
    f1 = f.readlines()
current_supply = float(f1[5])
current_available = float(f1[7])
reward_amount = float(f1[9])
f.close()
choice = '-1'
while choice != '0':
    choice = input('Inserire scelta: \n1-Send, 2-getPendingTx, 3-getAllPendingTx, 4-mineBlock, 5-getChain, 6-getBalance, 7-createWallet, 8-getAllWallets')
    if choice == '1':
        sender = input('Sender address: ')
        recipient = input('Recipient address: ')
        amount = float(input('Insert amount of transaction: '))
        description = input('Insert data: ')
        if create_tx(sender, recipient, amount, description):
            print('Success')
        else:
            print('Failed')
    if choice == '2':
        index = int(input('Which pending transaction do you want to read?'))
        if index > len(current_txs):
            print('Error, out of bound')
        else:
                print_pending_tx(index)    
    if choice == '3':
        if len(current_txs) != 0:
            for index in range(0, len(current_txs)):
               print_pending_tx(index)
        else:
            print('Empty list')
    if choice == '4':
        if len(current_txs) != 0:
            address = input('Insert address where rewards will be send: ')
            block_mined = mine(address)
            if block_mined == None:
                print('Block not mined')
            else:
                print('Block mined, enjoy your reward: %f PLM' % (reward_amount))
                #print_block(block_mined)
        else:
            print('There isn''t any transaction to convalidate and mine')
    if choice == '5':
        print_chain()
    if choice == '6':
        f=open("balance.txt", "r")
        f1 = f.readlines()
        for x in f1:
            print(x)
    if choice == '7':
        pk = input('Insert a private key: ')
        hash_pk = hashlib.sha256(pk.encode('utf-8')).hexdigest()
        print('This is your private key, do not forget it: %s' % (hash_pk))
        address = get_random_string()
        hash_address = hashlib.sha256(address.encode('utf-8')).hexdigest()
        print('Here is your wallet address: %s' % (hash_address))
        new_wallet = Wallet(hash_address, hash_pk, 0)
        wallets.append(new_wallet)
    if choice == '8':
        print_wallets()
save_wallet()
update_balance()
