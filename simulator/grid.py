import requests
import json
import time
from cryptography.fernet import Fernet

with open('key.key', 'rb') as key_file:
  key = key_file.read()

cipher_suite = Fernet(key)

def encrypt_message(message):
    return cipher_suite.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message):
    return cipher_suite.decrypt(encrypted_message.encode()).decode()

grid_cost = 0.1
smart_controller_url = 'http://127.0.0.1:5005'
step = 0

while step < 24:
    grid_data = {"component_id": "grid", "grid_cost": grid_cost}
    encrypted_data = encrypt_message(json.dumps(grid_data))

    requests.post(f'{smart_controller_url}/update_data', json={'encrypted_data': encrypted_data})
    time.sleep(10)

    response = requests.get(f'{smart_controller_url}/grid_response')
    encrypted_response = response.json().get('encrypted_data', '')

    decrypted_response = decrypt_message(encrypted_response)
    energy_management_data = json.loads(decrypted_response)

    print("Grid Energy Used:", energy_management_data['grid_energy_used'])
    print("Energy received from microgrid", energy_management_data['excess_solar_energy'])

    from web3 import Web3
    import json
    from web3.middleware import geth_poa_middleware

    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.eth.default_account = "<your_default_account_address>"
    abi = json.loads('[{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"battery","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"battery_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"genset","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"genset_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"grid","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"grid_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"load","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"load_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"renewable","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"renewable_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_battery","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_genset","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_grid","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_load","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_renewable","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"}]')
    address = Web3.to_checksum_address("<your_checksum_address")
    contract = w3.eth.contract(address=address,abi=abi)

    tx_hash = contract.functions.grid(str(grid_cost)).transact({'from': w3.eth.default_account})

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("BlockNumber:",tx_receipt['blockNumber'])

    call2=contract.functions.show_grid().call()
    print(len(call2))
    step += 1
    time.sleep(30)
