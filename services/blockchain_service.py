import os
from web3 import Web3
import logging
from eth_account import Account
import json

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL')))
        self.account = Account.from_key(os.getenv('PRIVATE_KEY'))

    async def execute_transaction(self, params: dict):
        try:
            required_fields = ['to', 'value']
            for field in required_fields:
                if field not in params:
                    raise ValueError(f"Missing required field: {field}")

            if isinstance(params['value'], str) and params['value'].endswith('eth'):
                value_eth = float(params['value'].replace('eth', ''))
                value_wei = self.w3.to_wei(value_eth, 'ether')
            else:
                value_wei = int(params['value'])

            transaction = {
                'to': Web3.to_checksum_address(params['to']),
                'value': value_wei,
                'gas': params.get('gas', 21000),
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': self.w3.eth.chain_id
            }

            if 'data' in params:
                transaction['data'] = params['data']

            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber'],
                'status': 'success' if tx_receipt['status'] == 1 else 'failed'
            }
        except Exception as e:
            logger.error(f"Error executing transaction: {str(e)}")
            raise