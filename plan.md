# Implementation Plan: Intelligent Invoice Processing & Reconciliation Agent (IPRA)

## Background & Motivation
FinFlow Inc. requires an automated solution to replace its manual accounts-payable process. Currently, extracting invoice data and cross-checking against Purchase Orders (POs) is slow, error-prone, and unscalable. The objective is to build an intelligent, API-driven agent that automates this workflow using a Large Language Model (Gemini), validating extracted data, matching POs, and detecting business anomalies.

## Scope & Impact
The project encompasses building a REST API using Python (FastAPI) that integrates with the Gemini API. 
Key features include:
- Invoice ingestion via file upload (PDF, Image, Text) or raw JSON.
- LLM-powered extraction of structured data (Vendor Name, Invoice Number, Date, Line Items, Total Amount, Currency, PO Reference).
- Business rule validation (dates, non-null fields, valid currency, positive amounts).
- PO matching against a provided mock dataset.
- Anomaly detection (>5% amount variance, missing PO, duplicate invoices).
- Structured JSON reconciliation reporting.

This will significantly reduce manual effort, minimize errors, and accelerate the accounts-payable lifecycle.

## Proposed Solution (Architecture)
The application will be built using Python and **FastAPI**, leveraging its built-in Pydantic validation for robust data modeling.
The architecture will follow a modular design, separating concerns into:
- **Routes (`/api/routes`)**: API endpoint definitions (`/upload`, `/reconcile/{invoice_id}`, `/report/{invoice_id}`).
- **Services (`/services`)**: Core business logic.
  - `llm_service.py`: Integration with Gemini API for data extraction.
  - `validation_service.py`: Field validation against business rules.
  - `po_matcher_service.py`: Matching logic against mock PO data.
  - `anomaly_detector.py`: Detection of variances and duplicates.
- **Models (`/models`)**: Pydantic schemas for request/response validation and internal data representation.
- **Utils (`/utils`)**: Helper functions (e.g., file parsing, JSON handling).
- **Storage (`/storage` or In-Memory)**: A simple mechanism (e.g., in-memory dictionary or SQLite) to store session data for duplicate checking and report retrieval.

## Implementation Steps

### Phase 1: Project Setup & Core Infrastructure
1. Initialize a Python virtual environment.
2. Install dependencies: `fastapi`, `uvicorn`, `pydantic`, `google-generativeai`, `python-multipart` (for file uploads), `pdfplumber` or similar (if direct text extraction is preferred before LLM, though Gemini can handle images/PDFs directly).
3. Set up the modular folder structure.
4. Load mock PO data into a reliable internal structure (e.g., a dictionary in a service module).

### Phase 2: API Endpoints & Models
1. Define Pydantic models for expected LLM output, Validation Status, Anomalies, and the final Reconciliation Report.
2. Implement the `POST /upload` endpoint to accept files/JSON, assign an `invoice_id`, and store the payload temporarily.
3. Implement stub endpoints for `POST /reconcile/{invoice_id}` and `GET /report/{invoice_id}`.

### Phase 3: Gemini Integration & Extraction
1. Configure the `google-generativeai` SDK with the provided API key (via `.env`).
2. Implement `llm_service.py` to send the invoice content (text or file bytes) to Gemini with a strict system prompt demanding structured JSON output adhering to the defined schema.
3. Handle potential parsing errors from the LLM response.

### Phase 4: Business Logic (Validation, Matching, Anomalies)
1. Implement `validation_service.py` to check ISO dates, numeric values > 0, valid currencies, and required fields.
2. Implement `po_matcher_service.py` to lookup the extracted `po_reference` in the mock dataset.
3. Implement `anomaly_detector.py`:
   - Calculate percentage variance between extracted `total_amount` and PO `total_amount`. Flag if > 5%.
   - Flag missing/unmatched POs.
   - Check the storage mechanism for duplicate `invoice_number`s to flag duplicates.

### Phase 5: Orchestration & Reporting
1. Wire the services together in the `POST /reconcile/{invoice_id}` endpoint route handler.
   - Run Extraction -> Validation -> Matching -> Anomaly Detection.
2. Compile the results into the final `ReconciliationReport` model.
3. Determine the final `reconciliation_status` (MATCHED, PARTIAL, FAILED) based on anomalies and validation errors.
4. Store the final report for retrieval via `GET /report/{invoice_id}`.

## Technical Implementation Guide & Usage Instructions

### 1. Environment Setup
- **Python Version**: 3.9+
- **Installation**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  pip install fastapi uvicorn pydantic google-generativeai python-multipart python-dotenv
  ```
- **Configuration**:
  Create a `.env` file in the root directory:
  ```env
  GEMINI_API_KEY=your_gemini_api_key_here
  ```

### 2. Running the Application
```powershell
python main.py
```
The API will be available at `http://localhost:8000`. 
Interactive documentation (Swagger UI) is at `http://localhost:8000/docs`.

### 3. API Usage Workflow

#### Step 1: Upload Invoice
**Endpoint**: `POST /api/v1/upload`
**Payload (JSON)**:
```json
{
  "vendor_name": "TechSupply Co.",
  "invoice_number": "INV-2024-001",
  "invoice_date": "2026-01-20",
  "line_items": [
    {"description": "Laptops", "qty": 5, "unit_price": 2500.0}
  ],
  "total_amount": 12500.0,
  "currency": "USD",
  "po_reference": "PO-1001"
}
```
**Response**:
```json
{
  "invoice_id": "...",
  "message": "Invoice uploaded successfully"
}
```

#### Step 2: Trigger Reconciliation
**Endpoint**: `POST /api/v1/reconcile/{invoice_id}`
**Response**: Returns the complete `ReconciliationReport`.

#### Step 3: Fetch Report
**Endpoint**: `GET /api/v1/report/{invoice_id}`

### 4. Testing Acceptance Criteria
- **Anomaly Detection**: Use `PO-1001` with a `total_amount` of `13500` (>5% variance) to see the `AMOUNT_VARIANCE` anomaly.
- **Duplicate Check**: Upload the same invoice number twice and reconcile both.
- **PO Matching**: Use `PO-9999` to see `UNMATCHED_PO_REFERENCE`.
- **Validation**: Use an invalid date format or negative amount.

## Verification & Testing
- **Unit Tests**: Test individual services (e.g., variance calculation, date validation logic).
- **Integration Tests**: 
  - Send a valid invoice matching a PO exactly. Verify status is `MATCHED`.
  - Send an invoice with a 6% variance. Verify anomaly is flagged and status is `PARTIAL` or `FAILED` (depending on strict business rules).
  - Send an invoice with a missing PO. Verify anomaly is flagged.
  - Send the same invoice twice to verify the duplicate anomaly detection.
- **Performance**: Ensure the `/reconcile` endpoint responds within acceptable limits (targeting < 3s, acknowledging LLM latency variability).
