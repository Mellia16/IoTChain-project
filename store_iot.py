import socket
from web3 import Web3
import threading

# Konfigurasi Web3 dan Blockchain
w3 = Web3(Web3.HTTPProvider('http://10.6.6.11:6102'))
abi=[{'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'name': 'dataList', 'outputs': [{'internalType': 'uint256', 'name': 'timestamp', 'type': 'uint256'}, {'internalType': 'string', 'name': 'data', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getDataCount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_index', 'type': 'uint256'}], 'name': 'retrieveData', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'string', 'name': '_data', 'type': 'string'}], 'name': 'storeData', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]

contract_address = '0xb52dCdf7DF184074087189897EcF8FdfCC830390'
account = '0xE0F473c185230cCD37C39e7A6CD858B2ec3a7EFc'
private_key = '0x5da5b08520cac83f6f52a8359ef5c073e94022354f1883cd4d9e14785dda6f4a'

contract = w3.eth.contract(address=contract_address, abi=abi)

# Fungsi untuk menyimpan data ke blockchain
def store_to_blockchain(data):
    try:
        nonce = w3.eth.get_transaction_count(account)

        transaction = contract.functions.storeData(data).build_transaction({
            'from': account,
            'gas': 10000000,
            'gasPrice': w3.to_wei('2', 'gwei'),
            'nonce': nonce
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"\n[Blockchain] Data berhasil disimpan!")
        print(f"Transaction hash: {tx_hash.hex()}")
        print(f"Block number: {tx_receipt['blockNumber']}\n")
        return True
    except Exception as e:
        print(f"\n[Blockchain Error] Gagal menyimpan data: {str(e)}\n")
        return False

# Fungsi untuk menjalankan server TCP
def run_tcp_server():
    # Buat socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind socket ke port
    server_address = ('0.0.0.0', 61003)  # Gunakan IP PC Anda jika perlu
    print(f"Starting TCP server on {server_address[0]} port {server_address[1]}")
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Tunggu koneksi
        print("\n[TCP Server] Menunggu koneksi dari ESP32...")
        connection, client_address = sock.accept()

        try:
            print(f"[TCP Server] Terhubung dengan: {client_address}")

            while True:
                data = connection.recv(1024)
                if data:
                    message = data.decode('utf-8').strip()
                    print(f"[TCP Server] Menerima pesan: {message}")

                    # Simpan ke blockchain dalam thread terpisah
                    thread = threading.Thread(target=store_to_blockchain, args=(message,))
                    thread.start()

                    # Beri respon ke ESP32
                    response = "Pesan diterima dan sedang diproses ke blockchain"
                    connection.sendall(response.encode('utf-8'))
                else:
                    break

        except Exception as e:
            print(f"[TCP Server Error] {str(e)}")
        finally:
            # Bersihkan koneksi
            connection.close()
            print(f"[TCP Server] Koneksi dengan {client_address} ditutup")

if __name__ == '__main__':
    # Jalankan server TCP dalam thread utama
    run_tcp_server()