import google.generativeai as genai
import pandas as pd
import PyPDF2
import io
from datetime import datetime, timedelta

# Configure Gemini API
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Get from https://makersuite.google.com/app/apikey
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def generate_pbc_from_trial_balance(tb_df, audit_type="Statutory Audit", financial_year="2024-25"):
    """
    Generate comprehensive PBC list from Trial Balance using Gemini AI
    """
    
    # Prepare Trial Balance summary
    tb_summary = f"""
Trial Balance Summary for {financial_year}:
- Total Accounts: {len(tb_df)}
- Total Debit: ₹{tb_df['Debit'].sum():,.2f}
- Total Credit: ₹{tb_df['Credit'].sum():,.2f}

Key Account Categories Present:
"""
    
    # Extract key accounts
    if 'Account Name' in tb_df.columns:
        accounts = tb_df['Account Name'].tolist()[:50]  # First 50 accounts
        tb_summary += "\n".join([f"- {acc}" for acc in accounts[:20]])
    
    prompt = f"""
You are an expert Chartered Accountant conducting a {audit_type}. Based on this Trial Balance, generate a comprehensive "Provided By Client" (PBC) list.

{tb_summary}

Generate a PBC list with the following structure for EACH item:
1. Category (e.g., "Cash & Bank", "Revenue", "Fixed Assets", "Statutory Compliance")
2. Item Description (Clear, specific request)
3. Why Needed (Audit assertion and purpose)
4. Priority (High/Medium/Low)

Cover these mandatory areas:
- Bank confirmations and reconciliations
- Revenue supporting documents (invoices, contracts)
- Expense vouchers and supporting
- Fixed asset registers and verification
- Inventory records and stock statements
- Statutory registers and filings
- Related party transaction details
- Loan agreements and repayment schedules
- Tax returns and assessments
- Board minutes and resolutions

Return EXACTLY in this JSON format (no extra text):
{{
  "pbc_items": [
    {{
      "category": "Cash & Bank",
      "description": "Bank statements for all bank accounts",
      "why_needed": "To verify existence and completeness of cash and bank balances",
      "priority": "High"
    }}
  ]
}}

Generate at least 25-30 PBC items covering all material areas.
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        import json
        pbc_data = json.loads(text)
        return pbc_data.get("pbc_items", [])
    
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        # Fallback: Return basic PBC list
        return get_fallback_pbc_list()

def get_fallback_pbc_list():
    """Basic PBC list if AI fails"""
    return [
        {"category": "Cash & Bank", "description": "Bank statements for all accounts (last 12 months)", "why_needed": "Verify cash balances", "priority": "High"},
        {"category": "Revenue", "description": "Sales invoices and supporting documents", "why_needed": "Verify revenue recognition", "priority": "High"},
        {"category": "Fixed Assets", "description": "Fixed asset register with depreciation schedule", "why_needed": "Verify existence and valuation", "priority": "High"},
        {"category": "Inventory", "description": "Stock statements and physical verification reports", "why_needed": "Verify inventory existence", "priority": "High"},
        {"category": "Statutory", "description": "GST returns (GSTR-1, GSTR-3B) for financial year", "why_needed": "Verify tax compliance", "priority": "High"},
        {"category": "Statutory", "description": "Income Tax returns and computation", "why_needed": "Verify tax provisions", "priority": "High"},
        {"category": "Loans", "description": "Loan agreements and sanction letters", "why_needed": "Verify loan obligations", "priority": "Medium"},
        {"category": "Governance", "description": "Board meeting minutes", "why_needed": "Understand key decisions", "priority": "Medium"},
    ]

def analyze_uploaded_document(file_bytes, filename, pbc_description):
    """
    Analyze uploaded PDF/document using Gemini AI
    """
    
    try:
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text_content = ""
        for page in pdf_reader.pages[:5]:  # First 5 pages
            text_content += page.extract_text()
        
        # Limit text length
        text_content = text_content[:3000]
        
        prompt = f"""
You are an audit assistant reviewing documents for a PBC request.

PBC Requirement: {pbc_description}
Document Filename: {filename}

Document Content Preview:
{text_content}

Analyze this document and provide:
1. Document Type (e.g., "Bank Statement", "Invoice", "Agreement")
2. Relevance Score (0-100) - How well does this match the PBC requirement?
3. Key Information Found (bullet points)
4. Missing Information (what's still needed)
5. Recommendation (Accept/Request Clarification/Reject)

Return in JSON format:
{{
  "document_type": "",
  "relevance_score": 0,
  "key_info": ["item1", "item2"],
  "missing_info": ["item1"],
  "recommendation": "",
  "summary": ""
}}
"""
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        import json
        return json.loads(text)
    
    except Exception as e:
        return {
            "document_type": "Unknown",
            "relevance_score": 50,
            "key_info": ["Document uploaded successfully"],
            "missing_info": ["Manual review required"],
            "recommendation": "Request Clarification",
            "summary": f"Document received: {filename}. Manual verification recommended."
        }

def smart_pbc_categorization(account_name, debit, credit):
    """Suggest PBC items based on account analysis"""
    categories = []
    
    keywords = {
        "bank": ["Bank statements", "Bank reconciliation"],
        "cash": ["Cash book", "Petty cash vouchers"],
        "sales": ["Sales invoices", "Sales register"],
        "purchase": ["Purchase invoices", "Purchase register"],
        "salary": ["Salary sheets", "PF/ESI challans"],
        "loan": ["Loan agreements", "Repayment schedule"],
        "asset": ["Asset register", "Depreciation schedule"],
        "gst": ["GST returns", "GST reconciliation"],
    }
    
    account_lower = account_name.lower()
    for keyword, items in keywords.items():
        if keyword in account_lower:
            categories.extend(items)
    
    return list(set(categories))
