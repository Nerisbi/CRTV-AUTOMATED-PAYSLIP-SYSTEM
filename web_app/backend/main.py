from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import sys
from pathlib import Path
import asyncio
from typing import List
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import payslip processor service
from services.payslip_processor import get_processor

app = FastAPI(
    title="CRTV Payslip Distribution System",
    description="Web-based payslip distribution and management system",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Create directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CRTV Payslip Distribution System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .gradient-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem 0;
            }
            .upload-zone {
                border: 2px dashed #dee2e6;
                border-radius: 10px;
                padding: 2rem;
                text-align: center;
                transition: all 0.3s ease;
            }
            .upload-zone:hover {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
            .upload-zone.dragover {
                border-color: #28a745;
                background-color: #d4edda;
            }
            .progress-container {
                display: none;
            }
            .status-badge {
                font-size: 0.875rem;
            }
        </style>
    </head>
    <body>
        <div class="gradient-header">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h1 class="mb-0">
                            <i class="fas fa-file-invoice-dollar me-3"></i>
                            CRTV Payslip Distribution System
                        </h1>
                        <p class="lead mb-0">Professional Employee Payslip Management</p>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="status-indicator">
                            <span class="badge bg-success" id="connection-status">
                                <i class="fas fa-circle me-2"></i>Connected
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="container mt-4">
            <!-- Navigation Tabs -->
            <ul class="nav nav-tabs" id="mainTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="bulk-tab" data-bs-toggle="tab" data-bs-target="#bulk" type="button" role="tab">
                        <i class="fas fa-users me-2"></i>Bulk Distribution
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="individual-tab" data-bs-toggle="tab" data-bs-target="#individual" type="button" role="tab">
                        <i class="fas fa-user me-2"></i>Individual Retrieval
                    </button>
                </li>
            </ul>

            <div class="tab-content" id="mainTabContent">
                <!-- Bulk Distribution Tab -->
                <div class="tab-pane fade show active" id="bulk" role="tabpanel">
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">
                                        <i class="fas fa-file-upload me-2"></i>File Upload
                                    </h5>
                                </div>
                                <div class="card-body">
                                    <div class="upload-zone" id="pdf-upload-zone">
                                        <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                                        <h5>Upload Payslip PDF</h5>
                                        <p class="text-muted">Drag and drop or click to select</p>
                                        <input type="file" id="pdf-input" accept=".pdf" style="display: none;">
                                        <button class="btn btn-outline-primary" onclick="document.getElementById('pdf-input').click()">
                                            Choose File
                                        </button>
                                    </div>
                                    <div class="mt-3" id="pdf-file-info"></div>
                                    
                                    <div class="upload-zone mt-3" id="excel-upload-zone">
                                        <i class="fas fa-file-excel fa-3x text-muted mb-3"></i>
                                        <h5>Upload Employee Excel</h5>
                                        <p class="text-muted">Drag and drop or click to select</p>
                                        <input type="file" id="excel-input" accept=".xlsx,.xls" style="display: none;">
                                        <button class="btn btn-outline-success" onclick="document.getElementById('excel-input').click()">
                                            Choose File
                                        </button>
                                    </div>
                                    <div class="mt-3" id="excel-file-info"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">
                                        <i class="fas fa-cogs me-2"></i>Control Panel
                                    </h5>
                                </div>
                                <div class="card-body">
                                    <div class="form-check mb-3">
                                        <input class="form-check-input" type="checkbox" id="simulation-mode">
                                        <label class="form-check-label" for="simulation-mode">
                                            <i class="fas fa-flask me-2"></i>Simulation Mode (No real emails)
                                        </label>
                                    </div>
                                    
                                    <div class="d-grid gap-2">
                                        <button class="btn btn-warning" onclick="validateFiles()">
                                            <i class="fas fa-check-circle me-2"></i>Validate Files
                                        </button>
                                        <button class="btn btn-success" onclick="processData()">
                                            <i class="fas fa-play me-2"></i>Process Data
                                        </button>
                                        <button class="btn btn-primary" onclick="sendPayslips()">
                                            <i class="fas fa-paper-plane me-2"></i>Send Payslips
                                        </button>
                                    </div>
                                    
                                    <div class="progress-container mt-3">
                                        <div class="progress">
                                            <div class="progress-bar" id="progress-bar" role="progressbar" style="width: 0%"></div>
                                        </div>
                                        <small class="text-muted" id="progress-text">Processing...</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Dashboard -->
                    <div class="row mt-4">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">
                                        <i class="fas fa-chart-bar me-2"></i>Dashboard
                                    </h5>
                                </div>
                                <div class="card-body">
                                    <div class="row" id="dashboard-stats">
                                        <div class="col-md-3">
                                            <div class="card bg-info text-white">
                                                <div class="card-body">
                                                    <h5 class="card-title">Total Employees</h5>
                                                    <h2 id="total-employees">0</h2>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="card bg-warning text-white">
                                                <div class="card-body">
                                                    <h5 class="card-title">Processed</h5>
                                                    <h2 id="processed-count">0</h2>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="card bg-success text-white">
                                                <div class="card-body">
                                                    <h5 class="card-title">Sent</h5>
                                                    <h2 id="sent-count">0</h2>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="card bg-danger text-white">
                                                <div class="card-body">
                                                    <h5 class="card-title">Failed</h5>
                                                    <h2 id="failed-count">0</h2>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Individual Retrieval Tab -->
                <div class="tab-pane fade" id="individual" role="tabpanel">
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">
                                        <i class="fas fa-user-edit me-2"></i>Employee Information
                                    </h5>
                                </div>
                                <div class="card-body">
                                    <form id="individual-form">
                                        <div class="mb-3">
                                            <label for="matricule" class="form-label">Matricule</label>
                                            <input type="text" class="form-control" id="matricule" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="email" class="form-label">Email</label>
                                            <input type="email" class="form-control" id="email" required>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Payslip Files</label>
                                            <div class="upload-zone" id="individual-pdf-zone">
                                                <i class="fas fa-file-pdf fa-3x text-muted mb-3"></i>
                                                <h6>Upload PDF Files</h6>
                                                <p class="text-muted small">Multiple files supported</p>
                                                <input type="file" id="individual-pdf-input" accept=".pdf" multiple style="display: none;">
                                                <button type="button" class="btn btn-outline-primary btn-sm" onclick="document.getElementById('individual-pdf-input').click()">
                                                    Choose Files
                                                </button>
                                            </div>
                                            <div class="mt-2" id="individual-pdf-list"></div>
                                        </div>
                                        <div class="d-grid gap-2">
                                            <button type="button" class="btn btn-warning" onclick="validateEmployee()">
                                                <i class="fas fa-check me-2"></i>Validate Employee
                                            </button>
                                            <button type="button" class="btn btn-success" onclick="retrievePayslip()">
                                                <i class="fas fa-download me-2"></i>Retrieve & Send Payslip
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">
                                        <i class="fas fa-history me-2"></i>Processing Log
                                    </h5>
                                </div>
                                <div class="card-body">
                                    <div id="individual-log" style="height: 300px; overflow-y: auto; background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 0.875rem;">
                                        <div class="text-muted">Waiting for actions...</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let ws = null;
            let uploadedFiles = {
                pdf: null,
                excel: null,
                individualPdfs: []
            };

            // WebSocket connection
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
                
                ws.onopen = function() {
                    document.getElementById('connection-status').className = 'badge bg-success';
                    document.getElementById('connection-status').innerHTML = '<i class="fas fa-circle me-2"></i>Connected';
                };
                
                ws.onclose = function() {
                    document.getElementById('connection-status').className = 'badge bg-danger';
                    document.getElementById('connection-status').innerHTML = '<i class="fas fa-circle me-2"></i>Disconnected';
                    setTimeout(connectWebSocket, 5000);
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
            }

            function handleWebSocketMessage(data) {
                switch(data.type) {
                    case 'progress':
                        updateProgress(data.value, data.message);
                        break;
                    case 'status':
                        updateDashboard(data.stats);
                        break;
                    case 'log':
                        addLog(data.message, data.level);
                        break;
                }
            }

            function updateProgress(value, message) {
                document.querySelector('.progress-container').style.display = 'block';
                document.getElementById('progress-bar').style.width = value + '%';
                document.getElementById('progress-text').textContent = message;
                
                if (value >= 100) {
                    setTimeout(() => {
                        document.querySelector('.progress-container').style.display = 'none';
                    }, 2000);
                }
            }

            function updateDashboard(stats) {
                document.getElementById('total-employees').textContent = stats.total || 0;
                document.getElementById('processed-count').textContent = stats.processed || 0;
                document.getElementById('sent-count').textContent = stats.sent || 0;
                document.getElementById('failed-count').textContent = stats.failed || 0;
            }

            function addLog(message, level = 'info') {
                const logContainer = document.getElementById('individual-log');
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = `text-${level === 'error' ? 'danger' : level === 'success' ? 'success' : 'info'}`;
                logEntry.innerHTML = `<small>[${timestamp}]</small> ${message}`;
                logContainer.appendChild(logEntry);
                logContainer.scrollTop = logContainer.scrollHeight;
            }

            // File upload handlers
            function setupFileUpload(zoneId, inputId, fileType) {
                const zone = document.getElementById(zoneId);
                const input = document.getElementById(inputId);
                
                zone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    zone.classList.add('dragover');
                });
                
                zone.addEventListener('dragleave', () => {
                    zone.classList.remove('dragover');
                });
                
                zone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    zone.classList.remove('dragover');
                    handleFileSelect(e.dataTransfer.files, fileType);
                });
                
                input.addEventListener('change', (e) => {
                    handleFileSelect(e.target.files, fileType);
                });
            }

            async function handleFileSelect(files, fileType) {
                if (files.length === 0) return;
                
                const file = files[0];
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch(`/upload/${fileType}`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        uploadedFiles[fileType] = result.filename;
                        
                        if (fileType === 'pdf') {
                            document.getElementById('pdf-file-info').innerHTML = 
                                `<div class="alert alert-success"><i class="fas fa-check me-2"></i>${file.name}</div>`;
                        } else if (fileType === 'excel') {
                            document.getElementById('excel-file-info').innerHTML = 
                                `<div class="alert alert-success"><i class="fas fa-check me-2"></i>${file.name}</div>`;
                        } else if (fileType === 'individualPdfs') {
                            updateIndividualPdfList(files);
                        }
                    }
                } catch (error) {
                    console.error('Upload error:', error);
                }
            }

            function updateIndividualPdfList(files) {
                const listContainer = document.getElementById('individual-pdf-list');
                listContainer.innerHTML = '';
                
                Array.from(files).forEach(file => {
                    const item = document.createElement('div');
                    item.className = 'alert alert-info py-2';
                    item.innerHTML = `<i class="fas fa-file-pdf me-2"></i>${file.name}`;
                    listContainer.appendChild(item);
                });
                
                uploadedFiles.individualPdfs = Array.from(files).map(f => f.name);
            }

            // API functions
            async function validateFiles() {
                if (!uploadedFiles.pdf || !uploadedFiles.excel) {
                    alert('Please upload both PDF and Excel files');
                    return;
                }
                
                try {
                    const response = await fetch('/api/validate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            pdf: uploadedFiles.pdf,
                            excel: uploadedFiles.excel
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        alert('Files validated successfully!');
                    } else {
                        alert('Validation failed: ' + result.message);
                    }
                } catch (error) {
                    console.error('Validation error:', error);
                }
            }

            async function processData() {
                if (!uploadedFiles.pdf || !uploadedFiles.excel) {
                    alert('Please upload and validate files first');
                    return;
                }
                
                try {
                    const response = await fetch('/api/process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            pdf: uploadedFiles.pdf,
                            excel: uploadedFiles.excel,
                            simulation: document.getElementById('simulation-mode').checked
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        alert('Processing started!');
                    } else {
                        alert('Processing failed: ' + result.message);
                    }
                } catch (error) {
                    console.error('Processing error:', error);
                }
            }

            async function sendPayslips() {
                try {
                    const response = await fetch('/api/send', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            simulation: document.getElementById('simulation-mode').checked
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        alert('Payslips sent successfully!');
                    } else {
                        alert('Sending failed: ' + result.message);
                    }
                } catch (error) {
                    console.error('Sending error:', error);
                }
            }

            async function validateEmployee() {
                const matricule = document.getElementById('matricule').value;
                const email = document.getElementById('email').value;
                
                if (!matricule || !email) {
                    alert('Please enter matricule and email');
                    return;
                }
                
                addLog('Validating employee...', 'info');
                
                try {
                    const response = await fetch('/api/individual/validate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ matricule, email })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        addLog('Employee validated successfully', 'success');
                    } else {
                        addLog('Validation failed: ' + result.message, 'error');
                    }
                } catch (error) {
                    addLog('Error: ' + error.message, 'error');
                }
            }

            async function retrievePayslip() {
                const matricule = document.getElementById('matricule').value;
                const email = document.getElementById('email').value;
                
                if (!matricule || !email || uploadedFiles.individualPdfs.length === 0) {
                    alert('Please enter employee details and upload PDF files');
                    return;
                }
                
                addLog('Retrieving payslip...', 'info');
                
                try {
                    const response = await fetch('/api/individual/retrieve', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            matricule,
                            email,
                            pdfs: uploadedFiles.individualPdfs
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        addLog('Payslip retrieved and sent successfully', 'success');
                    } else {
                        addLog('Retrieval failed: ' + result.message, 'error');
                    }
                } catch (error) {
                    addLog('Error: ' + error.message, 'error');
                }
            }

            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                connectWebSocket();
                setupFileUpload('pdf-upload-zone', 'pdf-input', 'pdf');
                setupFileUpload('excel-upload-zone', 'excel-input', 'excel');
                setupFileUpload('individual-pdf-zone', 'individual-pdf-input', 'individualPdfs');
            });
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now, can handle different message types
            await manager.send_personal_message(f"Received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/upload/{file_type}")
async def upload_file(file_type: str, file: UploadFile = File(...)):
    """Handle file uploads"""
    if file_type not in ['pdf', 'excel', 'individual']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"filename": filename, "original_name": file.filename, "size": len(content)}

@app.post("/api/validate")
async def validate_files(request: dict):
    """Validate uploaded files"""
    try:
        pdf_path = request.get('pdf')
        excel_path = request.get('excel')
        
        if not pdf_path or not excel_path:
            return {"success": False, "message": "Files not provided"}
        
        # Get processor and validate files
        processor = get_processor()
        success, message, data = processor.validate_files(pdf_path, excel_path)
        
        # Broadcast validation result
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": f"Validation: {message}",
            "level": "success" if success else "error"
        }))
        
        return {"success": success, "message": message, "data": data}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/process")
async def process_data(request: dict):
    """Process payslip data"""
    try:
        pdf_path = request.get('pdf')
        excel_path = request.get('excel')
        simulation = request.get('simulation', True)
        
        if not pdf_path or not excel_path:
            return {"success": False, "message": "Files not provided"}
        
        # Get processor with simulation mode
        processor = get_processor(simulation)
        
        # Broadcast processing start
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": "Starting payslip processing...",
            "level": "info"
        }))
        
        # Process bulk payslips
        success, message, results = processor.process_bulk_payslips(pdf_path, excel_path)
        
        # Broadcast results
        await manager.broadcast(json.dumps({
            "type": "status",
            "stats": results
        }))
        
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": f"Processing complete: {message}",
            "level": "success" if success else "error"
        }))
        
        return {"success": success, "message": message, "results": results}
    except Exception as e:
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": f"Processing error: {str(e)}",
            "level": "error"
        }))
        return {"success": False, "message": str(e)}

@app.post("/api/send")
async def send_payslips(request: dict):
    """Send payslips via email (combined process and send)"""
    try:
        pdf_path = request.get('pdf')
        excel_path = request.get('excel')
        simulation = request.get('simulation', True)
        
        if not pdf_path or not excel_path:
            return {"success": False, "message": "Files not provided"}
        
        # Get processor with simulation mode
        processor = get_processor(simulation)
        
        # Broadcast sending start
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": "Starting bulk payslip distribution...",
            "level": "info"
        }))
        
        # Process and send in one step
        success, message, results = processor.process_bulk_payslips(pdf_path, excel_path)
        
        # Broadcast final results
        await manager.broadcast(json.dumps({
            "type": "status",
            "stats": results
        }))
        
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": f"Distribution complete: {message}",
            "level": "success" if success else "error"
        }))
        
        return {"success": success, "message": message, "results": results}
    except Exception as e:
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": f"Distribution error: {str(e)}",
            "level": "error"
        }))
        return {"success": False, "message": str(e)}

@app.post("/api/individual/validate")
async def validate_individual_employee(request: dict):
    """Validate individual employee"""
    try:
        matricule = request.get('matricule')
        email = request.get('email')
        
        if not matricule or not email:
            return {"success": False, "message": "Matricule and email required"}
        
        # Basic validation (more complex validation would require Excel file)
        if len(matricule) < 3:
            return {"success": False, "message": "Invalid matricule format"}
        
        if "@" not in email:
            return {"success": False, "message": "Invalid email format"}
        
        return {"success": True, "message": "Employee details validated"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/individual/retrieve")
async def retrieve_individual_payslip_web(request: dict):
    """Retrieve individual payslip"""
    try:
        matricule = request.get('matricule')
        email = request.get('email')
        pdfs = request.get('pdfs', [])
        simulation = request.get('simulation', True)
        
        if not matricule or not email or not pdfs:
            return {"success": False, "message": "Matricule, email, and PDF files required"}
        
        # Get processor with simulation mode
        processor = get_processor(simulation)
        
        # Broadcast retrieval start
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": f"Starting individual retrieval for matricule {matricule}...",
            "level": "info"
        }))
        
        # Process individual retrieval
        success, message, output_file = processor.process_individual_retrieval(
            matricule, email, pdfs
        )
        
        # Broadcast result
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": f"Individual retrieval: {message}",
            "level": "success" if success else "error"
        }))
        
        return {"success": success, "message": message, "output_file": output_file}
    except Exception as e:
        await manager.broadcast(json.dumps({
            "type": "log",
            "message": f"Individual retrieval error: {str(e)}",
            "level": "error"
        }))
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
