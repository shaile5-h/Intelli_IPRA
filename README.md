# FinFlow Intelligent IPRA
> Intelligent Invoice Processing & Reconciliation Agent

## 🚀 Project Overview
FinFlow Intelligent IPRA is an automated accounts-payable solution designed to streamline invoice processing. It leverages the **Gemini 2.0 Flash Lite LLM** to extract data from invoices, validates the data against business rules, matches it with Purchase Orders (POs), and detects anomalies.

### 🌐 Web Interface
The project now includes a **React-based Web Frontend** for easy interaction. 
- **Access the UI**: Open your browser and go to **`http://localhost:8000/`**
- **Supported File Formats**: PDF, PNG, JPG, JPEG, JSON, and TXT.

## ✨ Key Features
- **Intelligent Extraction**: Uses Gemini AI to parse structured data from both images/PDFs and text-based formats (JSON/TXT).
- **Interactive UI**: Drag-and-drop web interface for instant invoice processing and report viewing.
- **PO Matching**: Automatically reconciles invoices against a mock Purchase Order database.
- **Anomaly Detection**: Flags variances > 5%, missing PO references, and duplicate invoices.
- **RESTful API**: Built with FastAPI for high performance and easy integration.

## 🏗️ Architecture
The project follows a modular service-oriented architecture:
- `api/`: REST API routes and endpoint logic.
- `frontend/`: React-based web interface (`index.html`).
- `models/`: Pydantic schemas for data validation and type safety.
- `services/`: Business logic (LLM integration, Validation, PO Matching, Anomaly Detection).
- `storage/`: Data persistence layer (currently in-memory).
- `utils/`: Common utility functions.

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.13+
- A Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Intelligent_IPRA
```

### 2. Configure Environment
Create a `.env` file in the root directory (or copy `.env.example`):
```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Install Dependencies
It is recommended to use a virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

## 🏃 Running the Project
You can start the server using the provided `server.py` script, which enables hot-reloading for development:

```bash
python server.py
```
The API will be available at: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🧪 Running Tests
The project uses `pytest` for automated testing. To run the test suite:

```bash
# Ensure test dependencies are installed
pip install pytest pytest-asyncio httpx

# Run all tests
python -m pytest tests/
```

## 📡 API Endpoints
- `POST /api/v1/upload`: Upload an invoice (File or JSON).
- `POST /api/v1/reconcile/{invoice_id}`: Trigger the reconciliation pipeline.
- `GET /api/v1/report/{invoice_id}`: Retrieve the full reconciliation report.

## 📈 Version Tracking
| Version | Date | Description |
| :--- | :--- | :--- |
| **1.0.0** | 2026-05-18 | Initial release with LLM extraction, PO matching, and anomaly detection. |

---
*Developed for FinFlow Inc.*
