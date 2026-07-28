Section 1 — Project Introduction
# 🛡️ Aegis AI

> **AI-Powered Document Validation, Verification & Risk Intelligence Platform**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-VertexAI-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)
![Cloud Run](https://img.shields.io/badge/Cloud-Run-success)
![BigQuery](https://img.shields.io/badge/Database-BigQuery-yellow)

---

## 📖 Overview

Aegis AI is an intelligent document verification platform that automates document validation, information extraction, fraud detection, and loan eligibility assessment using Google's Gemini models and a Multi-Agent AI architecture.

Instead of relying on manual verification, Aegis AI analyzes uploaded documents, validates their authenticity, extracts structured information, identifies inconsistencies, evaluates document risk, and generates an AI-assisted loan recommendation.

The entire solution is built on **Google Cloud Platform**, making it scalable, secure, and cloud-native.

---

## 🎯 Problem Statement

Financial institutions spend significant time manually verifying customer documents before approving loans.

Manual verification leads to:

- Slow approval process
- Human errors
- Document fraud
- Inconsistent verification
- High operational cost

Aegis AI automates the complete document verification workflow using AI agents.

---

## 🚀 Solution

Aegis AI provides an end-to-end AI-powered verification pipeline that:

- Classifies uploaded documents
- Extracts important information
- Detects fraudulent or manipulated documents
- Calculates document risk
- Performs cross-document validation
- Generates loan approval recommendations
- Stores application results in BigQuery
- Provides dashboards for both customers and administrators

---

---

# Features

## User Portal

- Secure Login
- Loan Application
- Home Loan
- Car Loan
- Personal Loan
- Gold Loan

- Upload required documents

- AI based document verification

- Automatic risk assessment

- Loan recommendation

- Real-time application status

---

## Admin Portal

- View all applications

- AI generated risk scores

- Verification status

- Application analytics

- BigQuery dashboard

- Search and monitor applicants

- Decision support dashboard

---

# AI Architecture

The backend follows a Multi-Agent Architecture.

```
                User Uploads Documents
                        │
                        ▼
                Master Orchestrator Agent
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
Classifier Agent   Extractor Agent   Risk Agent
        │               │               │
        └───────────────┼───────────────┘
                        ▼
             Loan Decision Agent
                        │
                        ▼
              Final Risk Assessment
                        │
                        ▼
                  Streamlit Frontend
```

---

# AI Agents

## 1. Document Classifier Agent

Automatically identifies uploaded documents such as

- Aadhaar Card
- PAN Card
- Passport
- Salary Slip
- Bank Statement
- Property Documents
- Vehicle Invoice
- Gold Certificate

---

## 2. Document Extractor Agent

Uses Gemini Vision to extract structured information including

- Name
- DOB
- PAN
- Aadhaar Number
- Address
- Income
- Employer
- Bank Details
- Property Details

Returns structured JSON using Pydantic models.

---

## 3. Risk Agent

Performs AI based document validation

Checks include

- Missing information

- Blurry document

- Tampering detection

- Authenticity estimation

- OCR quality

- Document completeness

---

## 4. Loan Decision Agent

Combines outputs from all AI agents and performs cross-document reasoning.

Evaluates

- Document completeness

- Identity consistency

- Authenticity

- Missing mandatory documents

- Overall verification quality

Returns

- Loan Approval Probability

- Overall Score

- Risk Level

- Decision

- Strengths

- Concerns

---

# Frontend

Built using Streamlit.

Features

- Beautiful responsive UI

- User Login

- Admin Login

- Loan selection

- File uploads

- Live document status

- AI verification progress

- Risk visualization

- Approval status

- BigQuery integration

---

# Backend

Python

Google Vertex AI (Gemini)

Cloud Run

Google Cloud Storage

BigQuery

Pydantic

REST APIs

---

# Google Cloud Services

- Vertex AI Gemini
- Cloud Run
- Google Cloud Storage
- BigQuery
- Cloud Logging
- IAM
- Application Default Credentials

---

# Project Workflow

                  Streamlit Frontend
                          │
                          ▼
                  Upload Documents
                          │
                          ▼
                Google Cloud Storage
                          │
                          ▼
                    FastAPI Backend
                          │
                          ▼
                 Master Agent (Orchestrator)
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
Classifier Agent   Extractor Agent     Risk Agent
        │                 │                  │
        └─────────────────┼──────────────────┘
                          ▼
                 Loan Decision Agent
                          │
                          ▼
                Structured JSON Response
                          │
                          ▼
                    Streamlit Dashboard
                          │
                          ▼
                     Google BigQuery

---

# Tech Stack

## Frontend

- Streamlit
- HTML
- CSS
- Python

## Backend

- Python
- FastAPI
- Pydantic

## AI

- Google Gemini
- Vertex AI

## Cloud

- Google Cloud Storage
- BigQuery
- Cloud Run
- Cloud Logging

---

# Supported Loan Types

- Home Loan
- Personal Loan
- Car Loan
- Gold Loan

---

# Supported Documents

- Aadhaar Card
- PAN Card
- Passport
- Salary Slip
- Bank Statement
- Income Tax Return
- Property Documents
- Vehicle Invoice
- Gold Purity Certificate
- Address Proof

---

# Security

- Google Cloud IAM
- Application Default Credentials
- Secure Cloud Storage
- Structured AI Responses
- Server-side Validation

---

# Future Enhancements

- OCR Confidence Scoring

- CIBIL Integration

- Bank Statement Analytics

- Face Matching

- Aadhaar Verification

- PAN Verification

- Digital Signature Verification

- Video KYC

- WhatsApp Notifications

- Email Notifications

- Explainable AI Dashboard

---

# Repository Structure

```text
Aegis-AI/
│
├── Backend/
│   │
│   ├── agents/
│   │   ├── classifier_agents/
│   │   ├── extractor_agents/
│   │   ├── loan_agents/
│   │   ├── master_agents/
│   │   └── risk_agents/
│   │
│   ├── config/
│   │   └── gemini_client.py
│   │
│   ├── models/
│   │
│   ├── prompts/
│   │
│   ├── resources/
│   │   ├── aadhar/
│   │   ├── pan/
│   │   └── passport/
│   │
│   ├── utils/
│   │
│   ├── .env
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── test.py
│   └── README.md
│
├── Frontend/
│   └── streamlit_app.py
│
└── README.md
```

---

# Why Aegis AI?

- Multi-Agent AI Architecture

- Cloud Native

- AI-first Loan Processing

- Automated Document Intelligence

- Fraud Detection

- Intelligent Loan Decisioning

- Scalable on Google Cloud


# 🌐 FastAPI Documentation

The backend exposes REST APIs built using **FastAPI**. These APIs are responsible for receiving uploaded document references from the frontend, invoking the AI agents, and returning structured verification results.

---

# Base URL

### Local Development

```http
http://localhost:8000
```

### Google Cloud Run

```http
https://loan-agent-xxxxxxxxxx.asia-south1.run.app
```

---

# Interactive API Documentation

FastAPI automatically generates interactive API documentation.

| Documentation | URL |
|--------------|-----|
| Swagger UI | `/docs` |
| ReDoc | `/redoc` |

Example:

```
http://localhost:8000/docs
```

or

```
https://loan-agent-xxxxxxxxxx.run.app/docs
```

---

# API Endpoints

## Verify Documents

This endpoint receives uploaded document locations, invokes the Master Agent, and returns the complete AI verification result.

### Endpoint

```http
POST /verify
```

---

### Request Headers

```http
Content-Type: application/json
Accept: application/json
```

---

### Request Body

```json
{
  "documents": {
    "aadhaar": "gs://document-agent-storage/user/john/Home Loan/aadhaar.pdf",
    "pan": "gs://document-agent-storage/user/john/Home Loan/pan.pdf",
    "salary_slip": "gs://document-agent-storage/user/john/Home Loan/salary.pdf",
    "bank_statement": "gs://document-agent-storage/user/john/Home Loan/bank.pdf"
  }
}
```

---

### Request Parameters

| Field | Type | Required | Description |
|---------|------|----------|-------------|
| documents | Object | Yes | Dictionary containing uploaded document locations |
| key | String | Yes | Document name |
| value | String | Yes | Google Cloud Storage path |

---

# Processing Flow

```
Client
   │
   ▼
POST /verify
   │
   ▼
FastAPI Backend
   │
   ▼
Master Agent
   │
   ├────────► Classifier Agent
   │
   ├────────► Extractor Agent
   │
   ├────────► Risk Agent
   │
   └────────► Loan Decision Agent
   │
   ▼
Structured JSON Response
```

---

# Successful Response

```json
{
  "overall_score": 91,
  "loan_approval_probability": 89,
  "decision": "Approve",
  "risk_level": "Low",
  "summary": "Documents are authentic, complete and consistent across all submissions.",
  "strengths": [
    "High document authenticity",
    "Identity information consistent",
    "Required documents available"
  ],
  "concerns": [],
  "missing_documents": []
}
```

---

# Error Response

```json
{
  "detail": "Unable to process uploaded documents."
}
```

---

# HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Documents verified successfully |
| 400 | Invalid request payload |
| 404 | Document not found |
| 422 | Validation error |
| 500 | Internal server error |

---

# Backend Workflow

```
Receive Request
       │
       ▼
Validate JSON
       │
       ▼
Load Documents
       │
       ▼
Master Agent
       │
       ▼
Document Classification
       │
       ▼
Information Extraction
       │
       ▼
Risk Analysis
       │
       ▼
Loan Decision
       │
       ▼
Return JSON Response
```

---

# Example cURL Request

```bash
curl -X POST \
'https://loan-agent-xxxxxxxxxx.asia-south1.run.app/verify' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
  "documents": {
    "aadhaar": "gs://document-agent-storage/user/demo/Home Loan/aadhaar.pdf",
    "pan": "gs://document-agent-storage/user/demo/Home Loan/pan.pdf",
    "salary_slip": "gs://document-agent-storage/user/demo/Home Loan/salary.pdf"
  }
}'
```

---

# API Features

- RESTful API using FastAPI
- Automatic request validation
- Structured JSON responses
- AI-powered document verification
- Multi-Agent orchestration
- Cloud-native deployment on Google Cloud Run
- Swagger & ReDoc documentation
- Easy integration with web and mobile applications

---

# Integration with Frontend

The Streamlit frontend performs the following workflow:

1. User uploads required documents.
2. Documents are uploaded to Google Cloud Storage.
3. GCS URLs are collected.
4. The frontend sends the URLs to the `/verify` endpoint.
5. FastAPI invokes the Master Agent.
6. AI agents process the documents.
7. The backend returns the verification result.
8. The frontend displays the risk score, verification status, and loan recommendation.