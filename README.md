# 📦 RFID-Based Inventory Management System

Inventory management is a critical aspect of businesses that deal with stock control. Conventional systems, often relying on manual processes or barcodes, face challenges such as human errors, inefficiencies, and lack of real-time data availability. Radio Frequency Identification (RFID) technology offers a superior alternative by enabling automated, accurate, and real-time inventory tracking.

Our project aims to develop an RFID-based inventory management system that addresses these challenges. Using an RC522 RFID module for reading inventory tags and a Raspberry Pi 4 as the processing unit, the system will automatically update inventory records. These records will be securely stored on a cloud platform, ensuring data accessibility and reliability.

## 🚀 Features
- Real-time inventory tracking with instant updates on stock changes
- Automated stock management using RFID technology
- Offline functionality with data synchronization when online
- User interaction via OLED display, buzzer alerts, and navigation buttons
- Real-time data exchange through WebSockets

## 🛠️ System Components
### Software Components
- Web Application (Frontend)
- Cloud Database
- Backend Server
- User Interface (UI) Components

### Hardware Components
- RFID Reader/Writer
- OLED Display
- Buzzer
- Buttons
- SD Card Storage

## 📊 System Diagrams
### Block Diagram
![Block Diagram](https://github.com/IoTians-UoM/Inventory-Management-IoT/blob/main/assets/BlockDiagram.png)

### Circuit Diagram
![Circuit Diagram](https://github.com/IoTians-UoM/Inventory-Management-IoT/blob/main/assets/circuit%20Diagram.jpg)

## 🔄 Process Flow
### Inventory Operations
**Stock In Process:**
1. Select Stock In mode from the web UI or IoT device
2. Scan the RFID tag
3. Adjust stock quantity
4. Update records (local and cloud)

**Stock Out Process:**
1. Select Stock Out mode
2. Scan the RFID tag
3. Confirm quantity to deduct
4. Prevent negative stock levels and update records

**Write Mode (Tag Initialization):**
1. Enter Write Mode
2. Select untagged product from the web app
3. Write product ID to RFID tag
4. Confirmation via buzzer and OLED display

### Real-Time Synchronization
- Web UI and IoT module communicate with the server
- Instant cloud database updates
- Offline transactions stored locally and synced when online

## ⚠️ Challenges and Risk Mitigation
- **Real-time Synchronization:** Ensure smooth sync between web, hardware, and cloud
- **Offline Functionality:** Store data locally and sync later
- **Hardware Integration:** Accurate inventory updates via RFID reader
- **Scalability:** Handle large datasets
- **User Experience:** Develop a responsive and intuitive UI
- **Security:** Protect sensitive data and ensure secure communication

## 🏃‍♀️ How to Use
- Use the web application to select Stock In, Stock Out, or Write Mode
- Scan RFID tags to update inventory
- Check the OLED display and buzzer for feedback
- Data syncs to the cloud automatically when online

## 👥 Contributors
- **Hitihamu H.M.C.N.B** (204076V)
- **Gunasekara M.G.M.S** (204062B)
- **Herath H.M.T.D.** (204073J)
- **Pemasiri M.P.T.B.S.** (204152C)
