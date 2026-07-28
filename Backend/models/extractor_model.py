from typing import Optional, Union
from pydantic import BaseModel


# -------------------------
# Aadhaar
# -------------------------

class AadhaarData(BaseModel):
    aadhaar_number: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None


# -------------------------
# PAN
# -------------------------

class PANData(BaseModel):
    pan_number: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None


# -------------------------
# Passport
# -------------------------

class PassportData(BaseModel):
    passport_number: Optional[str] = None
    full_name: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    expiry_date: Optional[str] = None


# -------------------------
# Salary Slip
# -------------------------

class SalarySlipData(BaseModel):
    employee_name: Optional[str] = None
    employer_name: Optional[str] = None
    pay_period: Optional[str] = None
    net_salary: Optional[str] = None


# -------------------------
# Property Proof
# -------------------------

class PropertyProofData(BaseModel):
    owner_name: Optional[str] = None
    property_address: Optional[str] = None
    document_number: Optional[str] = None


# -------------------------
# Gold Purity Certificate
# -------------------------

class GoldPurityCertificateData(BaseModel):
    certificate_number: Optional[str] = None
    purity: Optional[str] = None
    weight: Optional[str] = None


# -------------------------
# Car Invoice
# -------------------------

class CarInvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    registration_number: Optional[str] = None
    invoice_amount: Optional[str] = None


# -------------------------
# ITR
# -------------------------

class ITRData(BaseModel):
    pan_number: Optional[str] = None
    assessment_year: Optional[str] = None
    total_income: Optional[str] = None
    taxable_income: Optional[str] = None


# -------------------------
# Bank Statement
# -------------------------

class BankStatementData(BaseModel):
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    statement_period: Optional[str] = None
    closing_balance: Optional[str] = None


# -------------------------
# Address Proof
# -------------------------

class AddressProofData(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    document_number: Optional[str] = None


# -------------------------
# Generic Response
# -------------------------

class ExtractResponse(BaseModel):
    document_type: Optional[str] = None
    extracted_data: Optional[
        Union[
            AadhaarData,
            PANData,
            PassportData,
            SalarySlipData,
            PropertyProofData,
            GoldPurityCertificateData,
            CarInvoiceData,
            ITRData,
            BankStatementData,
            AddressProofData,
        ]
    ] = None