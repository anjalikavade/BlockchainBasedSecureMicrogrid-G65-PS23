import requests
import json
import time
from cryptography.fernet import Fernet
from pymgrid.modules import BatteryModule

Battery1=BatteryModule(min_capacity=1,
                              max_capacity=100,
                              max_charge=100,
                              max_discharge=100,
                              efficiency=0.9, 
                              init_soc=0.2)


with open('key.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

def encrypt_message(message):
    return cipher_suite.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message):
    return cipher_suite.decrypt(encrypted_message.encode()).decode()

# battery_soc = 80
battery_soc=Battery1.soc*100
smart_controller_url = 'http://127.0.0.1:5005'
step = 0

while step < 24:
  battery_data = {"component_id": "battery", "battery_soc": battery_soc}
  encrypted_data = encrypt_message(json.dumps(battery_data))

  requests.post(f'{smart_controller_url}/update_data', json={'encrypted_data': encrypted_data})
  time.sleep(10)

  response = requests.get(f'{smart_controller_url}/battery_response')
  encrypted_response = response.json().get('encrypted_data', '')

  decrypted_response = decrypt_message(encrypted_response)
  energy_management_data = json.loads(decrypted_response)

  print("Battery Energy Used:", energy_management_data['battery_energy_used'])
  battery_soc = battery_soc - energy_management_data['battery_energy_used'] + energy_management_data['battery_charging']
  print("current charge of battery ", battery_soc)

  from web3 import Web3
  import json
  from web3.middleware import geth_poa_middleware

  w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
  w3.middleware_onion.inject(geth_poa_middleware, layer=0)
  w3.eth.default_account = "<your_default_account>"
  abi = json.loads('[{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"battery","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"battery_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"genset","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"genset_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"grid","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"grid_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"load","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"load_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"element","type":"string"}],"name":"renewable","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"renewable_data","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_battery","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_genset","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_grid","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_load","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"show_renewable","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"}]')
  address = Web3.to_checksum_address("<your checksum_address>")
  contract = w3.eth.contract(address=address,abi=abi)

  tx_hash = contract.functions.battery(str(battery_soc)).transact({'from': w3.eth.default_account})

  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

  print("BlockNumber:",tx_receipt['blockNumber'])

  call2=contract.functions.show_battery().call()
  # print(len(call2))
  step += 1
  time.sleep(30)
