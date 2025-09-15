# e-dabot-amr-project
My first attempt at connecting IoT devices with blockchain. This project combines ESP32 sensors, a Flask backend, and Solidity smart contracts to securely store real-world data on-chain. A hands-on journey of learning by building.

Secure IoT Data Monitoring with Blockchain Smart Contracts

📌 Project Overview
This project was developed as a final class assignment in the Introduction to Blockchain course (April – June 2024). We built a decentralized IoT monitoring system that records temperature and humidity data into a blockchain using smart contracts. The project combines hardware (ESP32 + BMP180), a Flask backend, and Ethereum-based blockchain (Geth + Solidity).

🔧 Tools & Components
- Hardware
- ESP32
- BMP180 (temperature & humidity sensor)
- OLED display

Software & Frameworks
- Arduino IDE (ESP32 programming)
- Flask (backend server)
- Python
- Solidity (smart contracts)
- Geth (Ethereum client)

⚙️ Workflow
1. Sensor Setup → ESP32 reads temperature & humidity → displays on OLED.
2. Backend Server → Flask processes sensor data.
3. Blockchain Integration → Data is stored via Solidity smart contract (iot.sol).
4. Deployment → Python script (deploy.py) deploys and interacts with contract using ABI & bytecode.

🚀 Outcome
- Successfully deployed a smart contract on a local Ethereum test network.
- IoT sensor data (temperature & humidity) stored securely with timestamps.
- End-to-end demo from hardware → backend → blockchain → retrieval.

🔗 Related Links
https://bit.ly/IoTChain_documentation 
