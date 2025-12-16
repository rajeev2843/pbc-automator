
"""
Trial Balance to PBC Mapper - Complete Error-Free Version
Maps trial balance ledgers to PBC categories using keyword and fuzzy matching
"""

import pandas as pd
import numpy as np
import re
from rapidfuzz import fuzz, process
from typing import Dict, List, Tuple, Optional

class TrialBalanceToPBCMapper:
    """
    Maps Trial Balance ledgers to PBC (Prepared By Client) categories
    using keyword matching and fuzzy matching algorithms.
    """
    
    def __init__(self, audit_type: str = "Stat", accounting_standard: str = "Indian GAAP"):
        """
        Initialize the mapper with audit type and accounting standard.
        
        Parameters:
        -----------
        audit_type : str
            'Stat' for Statutory Audit or 'Tax' for Tax Audit
        accounting_standard : str
            'Indian GAAP' or 'Ind AS'
        """
        self.audit_type = audit_type
        self.accounting_standard = accounting_standard
        self.keyword_dictionary = self._build_keyword_dictionary()
        
    def _build_keyword_dictionary(self) -> Dict:
        """
        Build comprehensive keyword dictionary for PBC mapping.
        """
        
        keywords = {
            # ============= ASSETS - NON-CURRENT =============
            "Fixed Assets - Land": {
                "keywords": ["land", "freehold", "leasehold", "plot", "site", "premises"],
                "variations": ["F/H land", "L/H land", "land a/c", "factory land", "office land"]
            },
            "Fixed Assets - Building": {
                "keywords": ["building", "factory", "office", "warehouse", "godown", "shed", "premises", "structure"],
                "variations": ["bldg", "facto bldg", "off bldg", "building a/c"]
            },
            "Fixed Assets - Plant & Machinery": {
                "keywords": ["plant", "machinery", "equipment", "machine", "apparatus", "CNC", "lathe", "boiler", "generator"],
                "variations": ["P&M", "plant & mach", "mach", "equip", "production line"]
            },
            "Fixed Assets - Furniture & Fixtures": {
                "keywords": ["furniture", "fixture", "fitting", "furnishing", "desk", "chair", "cabinet", "workstation"],
                "variations": ["F&F", "furn", "furn & fix", "office furniture"]
            },
            "Fixed Assets - Vehicles": {
                "keywords": ["vehicle", "car", "truck", "van", "transport", "automobile", "motor", "delivery"],
                "variations": ["veh", "motor veh", "auto", "delivery van"]
            },
            "Fixed Assets - Computers & IT Equipment": {
                "keywords": ["computer", "laptop", "printer", "server", "hardware", "IT equipment", "desktop", "scanner"],
                "variations": ["comp", "IT equip", "sys", "laptop", "server"]
            },
            "Fixed Assets - Electrical Installation": {
                "keywords": ["electrical", "installation", "fitting", "wiring", "transformer", "UPS", "power"],
                "variations": ["elec inst", "elec equip", "power", "electrical fitting"]
            },
            "Intangible Assets - Goodwill": {
                "keywords": ["goodwill", "amalgamation", "merger", "acquisition", "business combination"],
                "variations": ["GW", "goodwill a/c", "goodwill on merger"]
            },
            "Intangible Assets - Software": {
                "keywords": ["software", "license", "application", "ERP", "system", "SAP", "tally", "digital"],
                "variations": ["soft", "SW", "lic", "ERP", "software license"]
            },
            "Intangible Assets - Patents & Trademarks": {
                "keywords": ["patent", "trademark", "intellectual property", "IP", "copyright", "brand", "logo"],
                "variations": ["IP", "IPR", "pat", "TM", "brand name"]
            },
            "Capital Work in Progress": {
                "keywords": ["capital work", "WIP", "under construction", "progress", "CWIP", "installation", "development"],
                "variations": ["CWIP", "WIP", "under const", "building under construction"]
            },
            "Investments - Non-Current": {
                "keywords": ["investment", "shares", "equity", "subsidiary", "associate", "long term", "mutual fund", "bond"],
                "variations": ["inv", "equity inv", "LT inv", "share investment"]
            },
            "Loans & Advances - Non-Current": {
                "keywords": ["loan", "advance", "subsidiary", "employee", "security deposit", "intercompany"],
                "variations": ["loan given", "advance to", "deposit paid", "IC loan"]
            },
            "Deferred Tax Assets": {
                "keywords": ["deferred tax", "DTA", "tax asset", "timing difference", "MAT credit", "temporary difference"],
                "variations": ["DTA", "def tax asset", "MAT"]
            },
            
            # ============= ASSETS - CURRENT =============
            "Inventories - Raw Materials": {
                "keywords": ["raw material", "RM", "stock", "inventory", "material"],
                "variations": ["RM", "raw mat", "mat stock", "raw material inventory"]
            },
            "Inventories - Work in Progress": {
                "keywords": ["work in progress", "WIP", "semi finished", "process", "semi-finished", "goods under process"],
                "variations": ["WIP", "semi fin", "process", "WIP stock"]
            },
            "Inventories - Finished Goods": {
                "keywords": ["finished goods", "FG", "final product", "product stock", "finished stock"],
                "variations": ["FG", "fin goods", "product", "finished inventory"]
            },
            "Inventories - Stock in Trade": {
                "keywords": ["trading goods", "stock in trade", "merchandise", "goods for sale", "trading stock"],
                "variations": ["trading stock", "goods", "merchandise"]
            },
            "Inventories - Stores & Spares": {
                "keywords": ["stores", "spares", "consumables", "maintenance", "spare parts"],
                "variations": ["S&S", "spares", "consumables", "stores and spares"]
            },
            "Trade Receivables - Domestic": {
                "keywords": ["debtor", "receivable", "sundry debtor", "trade receivable", "customer", "AR", "account receivable"],
                "variations": ["AR", "debtors", "rec", "sundry debtors", "customer outstanding"]
            },
            "Trade Receivables - Export": {
                "keywords": ["export debtor", "export receivable", "overseas", "foreign debtor", "foreign customer"],
                "variations": ["export AR", "foreign rec", "overseas customer"]
            },
            "Cash on Hand": {
                "keywords": ["cash", "petty cash", "cash in hand", "till", "cash balance"],
                "variations": ["cash", "petty", "till", "cash at office"]
            },
            "Bank - Current Account": {
                "keywords": ["bank", "current account", "CC", "cash credit", "OD", "overdraft"],
                "variations": ["CA", "CC", "OD", "curr a/c", "bank current"]
            },
            "Bank - Savings Account": {
                "keywords": ["bank", "savings", "SB account", "saving bank"],
                "variations": ["SB", "saving a/c", "savings account"]
            },
            "Bank - Fixed Deposit": {
                "keywords": ["fixed deposit", "FD", "term deposit", "deposit", "bank FD"],
                "variations": ["FD", "term dep", "bank deposit"]
            },
            "GST Input Tax Credit": {
                "keywords": ["GST input", "ITC", "input tax credit", "CGST", "SGST", "IGST", "input credit"],
                "variations": ["ITC", "GST ITC", "input", "CGST input", "SGST input"]
            },
            "TDS Receivable": {
                "keywords": ["TDS", "tax deducted", "advance tax", "refund", "TDS credit"],
                "variations": ["TDS rec", "adv tax", "TDS receivable"]
            },
            "Advances to Suppliers": {
                "keywords": ["advance", "supplier advance", "prepayment", "vendor advance", "advance for purchase"],
                "variations": ["supp adv", "prepay", "advance to supplier"]
            },
            "Prepaid Expenses": {
                "keywords": ["prepaid", "advance payment", "deferred expense", "unexpired", "prepaid rent", "prepaid insurance"],
                "variations": ["prepaid exp", "adv exp", "deferred cost"]
            },
            
            # ============= EQUITY =============
            "Equity Share Capital": {
                "keywords": ["equity", "share capital", "authorized", "issued", "subscribed", "paid up"],
                "variations": ["eq cap", "share cap", "equity capital"]
            },
            "Share Premium": {
                "keywords": ["share premium", "securities premium", "capital reserve", "premium account"],
                "variations": ["share prem", "sec prem", "premium"]
            },
            "Reserves & Surplus - General Reserve": {
                "keywords": ["general reserve", "free reserve", "revenue reserve"],
                "variations": ["gen res", "free res", "general reserve"]
            },
            "Reserves & Surplus - Retained Earnings": {
                "keywords": ["retained earnings", "profit and loss", "surplus", "accumulated profit", "P&L", "revenue surplus"],
                "variations": ["RE", "P&L bal", "surplus", "P&L account"]
            },
            
            # ============= LIABILITIES - NON-CURRENT =============
            "Long Term Borrowings - Term Loans": {
                "keywords": ["term loan", "secured loan", "bank loan", "financial institution"],
                "variations": ["TL", "secured loan", "bank term loan"]
            },
            "Long Term Borrowings - Debentures": {
                "keywords": ["debenture", "secured debenture", "bond", "NCD", "debt security"],
                "variations": ["NCD", "secured deb", "bond", "debenture"]
            },
            "Deferred Tax Liability": {
                "keywords": ["deferred tax", "DTL", "tax liability", "timing difference", "temporary difference"],
                "variations": ["DTL", "def tax liab", "tax deferral"]
            },
            "Provision for Gratuity": {
                "keywords": ["gratuity", "employee benefit", "retirement", "terminal benefit"],
                "variations": ["gratuity prov", "terminal", "retirement gratuity"]
            },
            
            # ============= LIABILITIES - CURRENT =============
            "Short Term Borrowings - Cash Credit": {
                "keywords": ["cash credit", "CC", "working capital", "bank OD", "overdraft"],
                "variations": ["CC", "OD", "WC loan", "working capital"]
            },
            "Trade Payables - Domestic": {
                "keywords": ["creditor", "payable", "sundry creditor", "trade payable", "supplier", "AP", "vendor"],
                "variations": ["AP", "creditors", "payable", "vendor outstanding"]
            },
            "Trade Payables - MSME": {
                "keywords": ["MSME", "micro", "small", "medium enterprise", "MSMED"],
                "variations": ["MSME cred", "MSME pay", "micro enterprise"]
            },
            "Advances from Customers": {
                "keywords": ["customer advance", "advance received", "unearned", "advance from customer"],
                "variations": ["cust adv", "adv rec", "customer deposit"]
            },
            "GST Payable": {
                "keywords": ["GST", "CGST", "SGST", "IGST", "output tax", "GST payable", "GST liability"],
                "variations": ["GST pay", "output GST", "CGST payable", "SGST payable"]
            },
            "TDS Payable": {
                "keywords": ["TDS", "tax deducted", "withholding tax", "TDS payable"],
                "variations": ["TDS pay", "WHT", "TDS liability"]
            },
            "PF Payable": {
                "keywords": ["provident fund", "PF", "employee PF", "EPFO"],
                "variations": ["PF pay", "EPFO", "PF liability"]
            },
            "ESI Payable": {
                "keywords": ["ESI", "employee insurance", "ESIC"],
                "variations": ["ESI pay", "ESIC", "employee state insurance"]
            },
            "Salary & Wages Payable": {
                "keywords": ["salary", "wages", "payroll", "remuneration"],
                "variations": ["sal pay", "wages pay", "payroll liability"]
            },
            "Provision for Income Tax": {
                "keywords": ["income tax", "tax provision", "current tax"],
                "variations": ["tax prov", "curr tax", "income tax payable"]
            },
            
            # ============= INCOME - REVENUE =============
            "Sales - Domestic": {
                "keywords": ["sales", "revenue", "domestic sales", "turnover", "sale of goods"],
                "variations": ["sales", "domestic rev", "sale", "turnover"]
            },
            "Sales - Export": {
                "keywords": ["export sales", "export revenue", "foreign sales", "overseas", "export turnover"],
                "variations": ["export sales", "foreign rev", "overseas sales"]
            },
            "Service Income": {
                "keywords": ["service revenue", "service income", "fees", "consulting", "professional fees"],
                "variations": ["service rev", "fees", "consulting income"]
            },
            "Other Operating Revenue": {
                "keywords": ["scrap sales", "export incentive", "duty drawback", "subsidy", "MEIS", "SEIS"],
                "variations": ["scrap", "incentive", "subsidy received"]
            },
            
            # ============= INCOME - OTHER INCOME =============
            "Interest Income": {
                "keywords": ["interest", "FD interest", "bank interest", "loan interest", "interest income"],
                "variations": ["int income", "FD int", "interest received"]
            },
            "Dividend Income": {
                "keywords": ["dividend", "subsidiary dividend", "mutual fund dividend"],
                "variations": ["div income", "dividend received"]
            },
            "Rental Income": {
                "keywords": ["rent", "rental", "property income", "lease rent"],
                "variations": ["rent inc", "lease rent", "rental income"]
            },
            "Profit on Sale of Assets": {
                "keywords": ["profit", "asset sale", "gain on disposal", "sale gain"],
                "variations": ["profit on sale", "disposal gain", "asset sale profit"]
            },
            "Foreign Exchange Gain": {
                "keywords": ["forex gain", "exchange gain", "currency gain", "forex profit"],
                "variations": ["forex gain", "FX gain", "exchange rate gain"]
            },
            "Miscellaneous Income": {
                "keywords": ["miscellaneous", "sundry income", "other income", "general"],
                "variations": ["misc income", "sundry inc", "other non-operating"]
            },
            
            # ============= EXPENSES - DIRECT =============
            "Raw Material Consumed": {
                "keywords": ["raw material", "consumption", "RM consumed", "material cost"],
                "variations": ["RM consumed", "mat consumed", "material used"]
            },
            "Purchase of Raw Materials": {
                "keywords": ["raw material purchase", "RM purchase", "material purchase"],
                "variations": ["RM purchase", "mat purchase", "purchase"]
            },
            "Freight Inward": {
                "keywords": ["freight inward", "inward freight", "transport inward", "carriage"],
                "variations": ["freight in", "transport in", "carriage inward"]
            },
            "Power and Fuel": {
                "keywords": ["power", "fuel", "electricity", "diesel", "coal"],
                "variations": ["power & fuel", "elec cost", "electricity"]
            },
            "Direct Labour": {
                "keywords": ["labour", "wages", "direct labour", "worker cost"],
                "variations": ["labour cost", "wages", "worker wages"]
            },
            
            # ============= EXPENSES - EMPLOYEE BENEFITS =============
            "Salaries and Wages": {
                "keywords": ["salary", "wages", "remuneration", "pay", "basic salary"],
                "variations": ["sal & wages", "remuner", "employee salary"]
            },
            "Contribution to PF": {
                "keywords": ["provident fund", "PF", "EPF", "employer contribution"],
                "variations": ["PF contrib", "EPF", "PF contribution"]
            },
            "Contribution to ESI": {
                "keywords": ["ESI", "employee insurance", "ESIC", "insurance contribution"],
                "variations": ["ESI contrib", "ESIC", "ESI contribution"]
            },
            "Gratuity Expense": {
                "keywords": ["gratuity", "terminal benefit", "retirement benefit"],
                "variations": ["gratuity exp", "terminal", "gratuity provision"]
            },
            "Staff Welfare": {
                "keywords": ["staff welfare", "employee welfare", "welfare expense", "canteen"],
                "variations": ["welfare exp", "emp welfare", "canteen"]
            },
            
            # ============= EXPENSES - FINANCE COSTS =============
            "Interest on Term Loans": {
                "keywords": ["interest", "term loan", "loan interest", "borrowing cost"],
                "variations": ["TL int", "loan int", "interest expense"]
            },
            "Interest on Working Capital": {
                "keywords": ["interest", "working capital", "CC interest", "OD interest"],
                "variations": ["WC int", "CC int", "overdraft interest"]
            },
            "Bank Charges": {
                "keywords": ["bank charges", "bank fees", "processing fees", "service charges"],
                "variations": ["bank charges", "fees", "bank commission"]
            },
            
            # ============= EXPENSES - DEPRECIATION =============
            "Depreciation": {
                "keywords": ["depreciation", "depr", "depreciation on", "amortization"],
                "variations": ["depr", "depreciation", "dep", "amort"]
            },
            
            # ============= EXPENSES - OTHER =============
            "Rent Expense": {
                "keywords": ["rent", "rental", "lease rent", "premises"],
                "variations": ["rent exp", "rental", "office rent"]
            },
            "Rates and Taxes": {
                "keywords": ["rates", "taxes", "property tax", "municipal"],
                "variations": ["rates & tax", "prop tax", "municipal tax"]
            },
            "Insurance Expense": {
                "keywords": ["insurance", "premium", "policy"],
                "variations": ["insurance prem", "policy", "insurance expense"]
            },
            "Repairs and Maintenance": {
                "keywords": ["repairs", "maintenance", "R&M", "upkeep"],
                "variations": ["R&M", "repairs", "maintenance"]
            },
            "Telephone and Internet": {
                "keywords": ["telephone", "internet", "mobile", "communication"],
                "variations": ["phone", "internet exp", "communication"]
            },
            "Printing and Stationery": {
                "keywords": ["printing", "stationery", "office supplies", "paper"],
                "variations": ["print & stat", "stationery", "office supplies"]
            },
            "Legal and Professional Fees": {
                "keywords": ["legal", "professional", "consultant", "advisory"],
                "variations": ["legal & prof", "consultant", "professional fees"]
            },
            "Audit Fees": {
                "keywords": ["audit", "auditor", "statutory audit", "audit charges"],
                "variations": ["audit fees", "auditor", "CA fees"]
            },
            "Travelling and Conveyance": {
                "keywords": ["travelling", "conveyance", "travel", "transport"],
                "variations": ["travel & conv", "travel exp", "conveyance"]
            },
            "Advertisement": {
                "keywords": ["advertisement", "publicity", "marketing", "promotion"],
                "variations": ["adv & pub", "marketing", "advertising"]
            },
            "Bad Debts Written Off": {
                "keywords": ["bad debts", "write off", "irrecoverable", "debt loss"],
                "variations": ["bad debt", "write off", "debt loss"]
            },
            "Foreign Exchange Loss": {
                "keywords": ["forex loss", "exchange loss", "currency loss", "forex"],
                "variations": ["forex loss", "FX loss", "exchange rate loss"]
            },
            "Miscellaneous Expenses": {
                "keywords": ["miscellaneous", "sundry expenses", "general", "other"],
                "variations": ["misc exp", "sundry", "general expenses"]
            },
        }
        
        return keywords
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        if pd.isna(text):
            return ""
        text = str(text).lower().strip()
        # Remove special characters but keep spaces and hyphens
        text = re.sub(r'[^\w\s\-\/]', ' ', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _keyword_match(self, ledger_name: str, pbc_category: str, keywords: Dict) -> int:
        """
        Calculate keyword match score.
        Returns score from 0-100 based on keyword matches.
        """
        ledger_normalized = self._normalize_text(ledger_name)
        score = 0
        
        # Check base keywords
        for keyword in keywords.get("keywords", []):
            keyword_normalized = self._normalize_text(keyword)
            if keyword_normalized in ledger_normalized:
                score += 30
        
        # Check variations
        for variation in keywords.get("variations", []):
            variation_normalized = self._normalize_text(variation)
            if variation_normalized in ledger_normalized:
                score += 20
        
        # Bonus for exact match
        if ledger_normalized in [self._normalize_text(k) for k in keywords.get("keywords", [])]:
            score += 50
        
        return min(score, 100)  # Cap at 100
    
    def _fuzzy_match(self, ledger_name: str, pbc_category: str, keywords: Dict) -> Tuple[int, str]:
        """
        Perform fuzzy matching using RapidFuzz.
        Returns best match score and matched keyword.
        """
        ledger_normalized = self._normalize_text(ledger_name)
        
        all_keywords = keywords.get("keywords", []) + keywords.get("variations", [])
        all_keywords_normalized = [self._normalize_text(k) for k in all_keywords]
        
        if not all_keywords_normalized:
            return 0, ""
        
        # Use token_sort_ratio for better matching with word order variations
        best_match = process.extractOne(
            ledger_normalized,
            all_keywords_normalized,
            scorer=fuzz.token_sort_ratio
        )
        
        if best_match:
            score, matched_keyword_index = best_match[1], best_match[2]
            matched_keyword = all_keywords[matched_keyword_index]
            return score, matched_keyword
        
        return 0, ""
    
    def map_ledger_to_pbc(self, ledger_name: str, threshold: int = 60) -> Dict:
        """
        Map a single ledger to PBC category.
        """
        best_pbc = None
        best_score = 0
        best_method = None
        matched_keyword = ""
        
        for pbc_category, keywords in self.keyword_dictionary.items():
            # Keyword matching
            keyword_score = self._keyword_match(ledger_name, pbc_category, keywords)
            
            # Fuzzy matching
            fuzzy_score, fuzzy_keyword = self._fuzzy_match(ledger_name, pbc_category, keywords)
            
            # Combined score (weighted average)
            combined_score = (keyword_score * 0.6) + (fuzzy_score * 0.4)
            
            if combined_score > best_score:
                best_score = combined_score
                best_pbc = pbc_category
                best_method = "keyword" if keyword_score > fuzzy_score else "fuzzy"
                matched_keyword = fuzzy_keyword if fuzzy_score > keyword_score else ""
        
        confidence = "High" if best_score >= 80 else "Medium" if best_score >= threshold else "Low"
        
        return {
            "Ledger_Name": ledger_name,
            "PBC_Category": best_pbc if best_score >= threshold else "UNMAPPED - Manual Review Required",
            "Confidence_Score": round(best_score, 2),
            "Confidence_Level": confidence,
            "Match_Method": best_method,
            "Matched_Keyword": matched_keyword
        }
    
    def process_trial_balance(self, 
                            df: pd.DataFrame,
                            ledger_column: str = None,
                            debit_column: str = None,
                            credit_column: str = None,
                            threshold: int = 60) -> pd.DataFrame:
        """
        Process trial balance DataFrame and map all ledgers to PBC categories.
        """
        # Auto-detect ledger column if not provided
        if ledger_column is None:
            ledger_column = self._detect_ledger_column(df)
        
        if ledger_column not in df.columns:
            raise ValueError(f"Ledger column '{ledger_column}' not found in file")
        
        # Auto-detect amount columns if not provided
        if debit_column is None:
            debit_column = self._detect_amount_column(df, ["debit", "dr", "debit amount", "dr amount"])
        if credit_column is None:
            credit_column = self._detect_amount_column(df, ["credit", "cr", "credit amount", "cr amount"])
        
        # Process each ledger
        results = []
        
        for idx, row in df.iterrows():
            ledger_name = row[ledger_column]
            
            # Skip empty ledgers
            if pd.isna(ledger_name) or str(ledger_name).strip() == "":
                continue
            
            mapping_result = self.map_ledger_to_pbc(str(ledger_name), threshold)
            
            # Add original amounts
            result_row = {
                "S.No": idx + 1,
                "Original_Ledger_Name": ledger_name,
                "PBC_Category": mapping_result["PBC_Category"],
                "Confidence_Score": mapping_result["Confidence_Score"],
                "Confidence_Level": mapping_result["Confidence_Level"],
                "Match_Method": mapping_result["Match_Method"],
                "Matched_Keyword": mapping_result["Matched_Keyword"]
            }
            
            # Add amount columns if available
            if debit_column and debit_column in df.columns:
                result_row["Debit_Amount"] = row[debit_column]
            if credit_column and credit_column in df.columns:
                result_row["Credit_Amount"] = row[credit_column]
            
            results.append(result_row)
        
        result_df = pd.DataFrame(results)
        
        return result_df
    
    def _detect_ledger_column(self, df: pd.DataFrame) -> str:
        """Auto-detect ledger name column."""
        possible_names = [
            'ledger', 'ledger name', 'account', 'account name', 
            'particulars', 'description', 'ledger_name', 'account_name',
            'name', 'head', 'account head'
        ]
        
        for col in df.columns:
            if any(name in col.lower() for name in possible_names):
                return col
        
        # Default to first column if no match
        return df.columns[0]
    
    def _detect_amount_column(self, df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
        """Auto-detect amount columns."""
        for col in df.columns:
            if any(keyword in col.lower() for keyword in keywords):
                return col
        return None
    
    def generate_pbc_summary(self, result_df: pd.DataFrame) -> Dict:
        """Generate summary statistics from mapping results."""
        if len(result_df) == 0:
            return {
                'total_ledgers': 0,
                'high_confidence': 0,
                'medium_confidence': 0,
                'low_confidence': 0,
                'avg_confidence_score': 0,
                'success_rate': 0
            }
        
        summary = {
            'total_ledgers': len(result_df),
            'high_confidence': len(result_df[result_df['Confidence_Level'] == 'High']),
            'medium_confidence': len(result_df[result_df['Confidence_Level'] == 'Medium']),
            'low_confidence': len(result_df[result_df['Confidence_Level'] == 'Low']),
            'avg_confidence_score': round(result_df['Confidence_Score'].mean(), 2),
            'success_rate': round((len(result_df[result_df['Confidence_Level'] != 'Low']) / len(result_df) * 100), 2)
        }
        
        return summary
