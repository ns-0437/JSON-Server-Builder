# JSON-Server-Builder
Built a script that reads a JSON file representing server nodes and links, then generates a complete server implementation. 

## Overview
This repository contains a Python script that reads a JSON configuration, processes server nodes and links, and generates a fully functional server using Node.js and Express.

## Project Structure
```
.
├── script.py           # Python script to generate server.js
├── config.json         # Example JSON configuration for server generation
├── server.js           # Auto-generated Node.js server
└── README.md           # Project documentation
```

## Requirements
- Python 3.8+
- Node.js 16+
- Express.js
- CORS

## Installation and Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/ns-0437/JSON-Server-Builder
cd JSON-server-builder
```

### Step 2: Install Python Requirements
No additional Python packages are required. Ensure Python 3 is installed.

### Step 3: Install Node.js and Dependencies
```bash
npm install express cors
```

### Step 4: Generate Server
Run the Python script to generate the `server.js` file.
```bash
python script.py
```

### Step 5: Start the Server
```bash
node server.js
```
The server will be accessible at `http://localhost:3000`.


## Configuration File (config.json)
The JSON file defines nodes representing routes, middlewares, and links between them. It supports:
- Entry and exit points
- Authentication and admin middleware
- CORS configuration
- Route definitions (e.g., endpoints, methods)







