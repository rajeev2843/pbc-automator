"""
Trial Balance to PBC Mapper - Integrated Module
Maps trial balance ledgers to PBC categories using keyword and fuzzy matching
"""

import pandas as pd
import numpy as np
import re
from rapidfuzz import fuzz, process
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import io

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
        Based on complete master dictionary from all tables.
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
            "Fixed Assets - Tools & Dies": {
                "keywords": ["tool", "die", "jig", "fixture", "mould", "pattern", "cutting"],
                "variations": ["T&E", "jigs & fix", "moulds", "dies"]
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
            "Investments - Non-Current - Equity": {
                "keywords": ["investment", "shares", "equity", "subsidiary", "associate", "long term"],
                "variations": ["inv", "equity inv", "LT inv", "share investment"]
            },
            "Investments - Non-Current - Mutual Funds": {
                "keywords": ["mutual fund", "SIP", "debt fund", "equity fund", "MF units"],
                "variations": ["MF", "MF inv", "SIP", "mutual fund"]
            },
            "Investments - Non-Current - Bonds & Debentures": {
                "keywords": ["bond", "debenture", "govt securities", "fixed income", "g-sec"],
                "variations": ["bond inv", "govt sec", "deb", "debenture"]
            },
            "Loans & Advances - Loans to Subsidiaries": {
                "keywords": ["loan", "advance", "subsidiary", "intercompany", "group company"],
                "variations": ["IC loan", "group loan", "sub loan"]
            },
            "Loans & Advances - Loans to Employees": {
                "keywords": ["employee loan", "staff advance", "salary advance", "staff loan"],
                "variations": ["emp loan", "staff adv", "employee advance"]
            },
            "Loans & Advances - Security Deposits": {
                "keywords": ["deposit", "security", "rental deposit", "lease deposit", "refundable"],
                "variations": ["sec dep", "ref dep", "security deposit"]
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
            "Inventories - Packing Materials": {
                "keywords": ["packing", "packaging", "carton", "box", "wrapper", "packaging material"],
                "variations": ["pack mat", "pkg", "packing material"]
            },
            "Inventories - Goods in Transit": {
                "keywords": ["goods in transit", "GIT", "transit inventory", "in-transit", "material in transit"],
                "variations": ["GIT", "transit stock", "goods transit"]
            },
            "Trade Receivables - Domestic": {
                "keywords": ["debtor", "receivable", "sundry debtor", "trade receivable", "customer", "AR", "account receivable"],
                "variations": ["AR", "debtors", "rec", "sundry debtors", "customer outstanding"]
            },
            "Trade Receivables - Export": {
                "keywords": ["export debtor", "export receivable", "overseas", "foreign debtor", "foreign customer"],
                "variations": ["export AR", "foreign rec", "overseas customer"]
            },
            "Trade Receivables - Bills Receivable": {
                "keywords": ["bills receivable", "BR", "promissory note", "bill of exchange", "bills under collection"],
                "variations": ["BR", "bills rec", "promissory note"]
            },
            "Trade Receivables - Related Party": {
                "keywords": ["related party", "group company", "subsidiary", "associate", "director", "RP receivable"],
                "variations": ["RP rec", "group rec", "related party"]
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
            "Bank - Deposits in Transit": {
                "keywords": ["deposit in transit", "cheque in transit", "clearing", "uncleared", "cheque for collection"],
                "variations": ["cheque transit", "clearing", "uncleared"]
            },
            "Short Term Loans - To Employees": {
                "keywords": ["employee loan", "staff loan", "advance to staff", "short term loan"],
                "variations": ["emp loan", "staff adv", "ST loan"]
            },
            "Short Term Loans - To Subsidiaries": {
                "keywords": ["subsidiary loan", "group loan", "intercompany loan", "IC loan"],
                "variations": ["IC loan", "sub loan", "group loan"]
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
            "Other Current Assets - MAT Credit": {
                "keywords": ["MAT credit", "minimum alternate tax", "tax credit"],
                "variations": ["MAT", "MAT credit", "MAT entitlement"]
            },
            "Other Current Assets - Accrued Interest": {
                "keywords": ["accrued interest", "interest receivable", "interest due", "FD interest"],
                "variations": ["int rec", "acc int", "interest accrued"]
            },
            "Other Current Assets - Balance with Authorities": {
                "keywords": ["statutory balance", "govt dues receivable", "excise", "customs", "service tax"],
                "variations": ["stat bal", "excise rec", "customs refund"]
            },
            
            # ============= EQUITY & LIABILITIES - EQUITY =============
            "Equity Share Capital": {
                "keywords": ["equity", "share capital", "authorized", "issued", "subscribed", "paid up"],
                "variations": ["eq cap", "share cap", "equity capital"]
            },
            "Preference Share Capital": {
                "keywords": ["preference", "pref share", "cumulative", "redeemable"],
                "variations": ["pref cap", "pref share", "preference capital"]
            },
            "Share Application Money": {
                "keywords": ["share application", "application money", "pending allotment"],
                "variations": ["app money", "pending", "share application"]
            },
            "Share Premium / Securities Premium": {
                "keywords": ["share premium", "securities premium", "capital reserve", "premium account"],
                "variations": ["share prem", "sec prem", "premium"]
            },
            "Reserves & Surplus - General Reserve": {
                "keywords": ["general reserve", "free reserve", "revenue reserve"],
                "variations": ["gen res", "free res", "general reserve"]
            },
            "Reserves & Surplus - Capital Reserve": {
                "keywords": ["capital reserve", "capital profit", "amalgamation reserve", "capital redemption"],
                "variations": ["cap res", "CRR", "capital reserve"]
            },
            "Reserves & Surplus - Revaluation Reserve": {
                "keywords": ["revaluation", "revaluation reserve", "asset revaluation", "surplus on revaluation"],
                "variations": ["reval res", "reval", "revaluation surplus"]
            },
            "Reserves & Surplus - Retained Earnings": {
                "keywords": ["retained earnings", "profit and loss", "surplus", "accumulated profit", "P&L", "revenue surplus"],
                "variations": ["RE", "P&L bal", "surplus", "P&L account"]
            },
            "Reserves & Surplus - FCTR": {
                "keywords": ["FCTR", "foreign currency", "translation reserve", "exchange difference"],
                "variations": ["FCTR", "forex res", "translation reserve"]
            },
            "Reserves & Surplus - Debenture Redemption Reserve": {
                "keywords": ["DRR", "debenture reserve", "redemption reserve"],
                "variations": ["DRR", "deb res", "debenture redemption"]
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
            "Long Term Borrowings - Unsecured Loans from Directors": {
                "keywords": ["unsecured loan", "director loan", "promoter loan", "director advance"],
                "variations": ["dir loan", "promoter loan", "director unsecured"]
            },
            "Long Term Borrowings - Unsecured Loans from Related Parties": {
                "keywords": ["related party loan", "group company loan", "intercompany", "RP loan"],
                "variations": ["RP loan", "IC loan", "group loan"]
            },
            "Long Term Borrowings - Foreign Currency Loans": {
                "keywords": ["foreign loan", "ECB", "external borrowing", "forex loan", "overseas loan"],
                "variations": ["ECB", "forex loan", "external commercial"]
            },
            "Deferred Tax Liability": {
                "keywords": ["deferred tax", "DTL", "tax liability", "timing difference", "temporary difference"],
                "variations": ["DTL", "def tax liab", "tax deferral"]
            },
            "Provision for Gratuity": {
                "keywords": ["gratuity", "employee benefit", "retirement", "terminal benefit"],
                "variations": ["gratuity prov", "terminal", "retirement gratuity"]
            },
            "Provision for Leave Encashment": {
                "keywords": ["leave", "leave encashment", "earned leave", "compensated absence"],
                "variations": ["leave prov", "EL prov", "leave liability"]
            },
            "Provision for Pension": {
                "keywords": ["pension", "superannuation", "retirement benefit"],
                "variations": ["pension prov", "superann", "pension liability"]
            },
            "Other Long Term Liabilities - Trade Deposits": {
                "keywords": ["deposit", "security deposit", "customer deposit", "refundable deposit"],
                "variations": ["trade dep", "sec dep rec", "customer deposit"]
            },
            "Other Long Term Liabilities - Deferred Revenue": {
                "keywords": ["deferred revenue", "unearned revenue", "advance billing", "deferred income"],
                "variations": ["def rev", "unearned", "advance billing"]
            },
            
            # ============= LIABILITIES - CURRENT =============
            "Short Term Borrowings - Cash Credit": {
                "keywords": ["cash credit", "CC", "working capital", "bank OD", "overdraft"],
                "variations": ["CC", "OD", "WC loan", "working capital"]
            },
            "Short Term Borrowings - Working Capital Loan": {
                "keywords": ["working capital", "WCDL", "demand loan", "short term loan"],
                "variations": ["WCDL", "demand loan", "WC facility"]
            },
            "Short Term Borrowings - Packing Credit": {
                "keywords": ["packing credit", "export finance", "pre-shipment", "LC", "export credit"],
                "variations": ["PC", "export fin", "pre-shipment"]
            },
            "Short Term Borrowings - Bill Discounting": {
                "keywords": ["bill discounting", "invoice discounting", "trade finance"],
                "variations": ["bill disc", "inv disc", "trade bill"]
            },
            "Short Term Borrowings - Inter-Corporate Deposits": {
                "keywords": ["ICD", "corporate deposit", "short term deposit", "inter-corporate"],
                "variations": ["ICD", "corp deposit", "ICD payable"]
            },
            "Trade Payables - Domestic": {
                "keywords": ["creditor", "payable", "sundry creditor", "trade payable", "supplier", "AP", "vendor"],
                "variations": ["AP", "creditors", "payable", "vendor outstanding"]
            },
            "Trade Payables - Import": {
                "keywords": ["import creditor", "import payable", "foreign supplier", "forex creditor"],
                "variations": ["import AP", "foreign cred", "overseas creditor"]
            },
            "Trade Payables - Bills Payable": {
                "keywords": ["bills payable", "BP", "promissory note payable", "bill of exchange"],
                "variations": ["BP", "bills pay", "promissory note"]
            },
            "Trade Payables - Related Party": {
                "keywords": ["related party", "group company payable", "subsidiary payable", "RP payable"],
                "variations": ["RP payable", "group pay", "related party creditor"]
            },
            "Trade Payables - MSME": {
                "keywords": ["MSME", "micro", "small", "medium enterprise", "MSMED"],
                "variations": ["MSME cred", "MSME pay", "micro enterprise"]
            },
            "Trade Payables - LC Acceptances": {
                "keywords": ["acceptance", "LC acceptance", "bank acceptance", "trade acceptance"],
                "variations": ["LC accept", "bank accept", "acceptance payable"]
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
            "TCS Payable": {
                "keywords": ["TCS", "tax collected", "collection at source"],
                "variations": ["TCS pay", "collection tax", "TCS liability"]
            },
            "PF Payable": {
                "keywords": ["provident fund", "PF", "employee PF", "EPFO"],
                "variations": ["PF pay", "EPFO", "PF liability"]
            },
            "ESI Payable": {
                "keywords": ["ESI", "employee insurance", "ESIC"],
                "variations": ["ESI pay", "ESIC", "employee state insurance"]
            },
            "Professional Tax Payable": {
                "keywords": ["professional tax", "PT", "state tax"],
                "variations": ["PT pay", "prof tax", "professional tax"]
            },
            "Labour Welfare Fund": {
                "keywords": ["LWF", "welfare fund", "labour welfare"],
                "variations": ["LWF pay", "welfare", "labour welfare"]
            },
            "Salary & Wages Payable": {
                "keywords": ["salary", "wages", "payroll", "remuneration"],
                "variations": ["sal pay", "wages pay", "payroll liability"]
            },
            "Bonus Payable": {
                "keywords": ["bonus", "incentive", "performance pay"],
                "variations": ["bonus pay", "incentive", "performance bonus"]
            },
            "Dividend Payable": {
                "keywords": ["dividend", "distribution", "shareholder payment", "unclaimed dividend"],
                "variations": ["div pay", "unclaimed div", "dividend distribution"]
            },
            "Interest Accrued but Not Due": {
                "keywords": ["interest accrued", "accrued interest", "interest payable"],
                "variations": ["int accrued", "acc int", "interest not due"]
            },
            "Expenses Payable": {
                "keywords": ["expense payable", "accrued expense", "outstanding expense"],
                "variations": ["exp pay", "acc exp", "outstanding expenses"]
            },
            "Income Received in Advance": {
                "keywords": ["income advance", "deferred income", "unearned revenue", "advance billing"],
                "variations": ["adv income", "def income", "unearned"]
            },
            "Security Deposits from Customers": {
                "keywords": ["customer deposit", "security", "refundable deposit"],
                "variations": ["cust sec dep", "refund dep", "customer security"]
            },
            "Provision for Expenses": {
                "keywords": ["provision", "accrual", "estimated expense", "accrued"],
                "variations": ["prov exp", "acc prov", "provision for"]
            },
            "Provision for Income Tax": {
                "keywords": ["income tax", "tax provision", "current tax"],
                "variations": ["tax prov", "curr tax", "income tax payable"]
            },
            "Provision for Warranty": {
                "keywords": ["warranty", "guarantee", "service obligation", "product warranty"],
                "variations": ["warranty prov", "guarantee", "warranty liability"]
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
            "Service Income - Domestic": {
                "keywords": ["service revenue", "service income", "fees", "consulting", "professional fees"],
                "variations": ["service rev", "fees", "consulting income"]
            },
            "Service Income - Export": {
                "keywords": ["export service", "foreign service", "overseas service", "service export"],
                "variations": ["export service", "foreign fees", "service export"]
            },
            "Job Work Income": {
                "keywords": ["job work", "conversion charges", "processing charges", "manufacturing service"],
                "variations": ["job work rev", "conversion", "processing fees"]
            },
            "Sale of Scrap": {
                "keywords": ["scrap sales", "scrap revenue", "waste sales", "by-product"],
                "variations": ["scrap", "waste rev", "by-product sales"]
            },
            "Commission Income": {
                "keywords": ["commission", "brokerage", "agency income", "intermediary"],
                "variations": ["comm income", "brokerage", "agency commission"]
            },
            "Royalty Income": {
                "keywords": ["royalty", "licensing", "IP income", "franchise"],
                "variations": ["royalty", "lic fees", "franchise fees"]
            },
            "Other Operating Revenue - Subsidy": {
                "keywords": ["subsidy", "grant", "government grant", "incentive"],
                "variations": ["subsidy", "grant", "govt grant"]
            },
            "Other Operating Revenue - Export Incentives": {
                "keywords": ["export incentive", "MEIS", "SEIS", "duty drawback", "RoDTEP"],
                "variations": ["MEIS", "duty drawback", "RoDTEP", "SEIS"]
            },
            "Other Operating Revenue - Insurance Claims": {
                "keywords": ["insurance claim", "claim received", "damage recovery"],
                "variations": ["claim rec", "insurance rec", "insurance proceeds"]
            },
            
            # ============= INCOME - OTHER INCOME =============
            "Interest Income - Fixed Deposits": {
                "keywords": ["interest", "fixed deposit", "FD", "bank interest", "deposit interest"],
                "variations": ["FD int", "bank int", "interest income"]
            },
            "Interest Income - Loans Given": {
                "keywords": ["interest", "loan interest", "lending income", "interest on loans"],
                "variations": ["loan int", "lending inc", "interest on advance"]
            },
            "Interest Income - Tax Refund": {
                "keywords": ["interest", "tax refund", "refund interest", "IT refund"],
                "variations": ["IT refund int", "tax int", "refund interest"]
            },
            "Interest Income - Delayed Payments": {
                "keywords": ["interest", "delayed payment", "customer interest", "late payment"],
                "variations": ["delay int", "late pay int", "overdue interest"]
            },
            "Dividend Income - Subsidiaries": {
                "keywords": ["dividend", "subsidiary dividend", "intercompany dividend"],
                "variations": ["sub div", "IC div", "dividend from subsidiary"]
            },
            "Dividend Income - Mutual Funds": {
                "keywords": ["dividend", "mutual fund", "MF dividend", "fund income"],
                "variations": ["MF div", "fund div", "mutual fund dividend"]
            },
            "Dividend Income - Equity Shares": {
                "keywords": ["dividend", "equity dividend", "share dividend"],
                "variations": ["equity div", "share div", "equity investment dividend"]
            },
            "Rental Income - Property": {
                "keywords": ["rent", "rental", "property income", "lease rent"],
                "variations": ["rent inc", "lease rent", "rental income"]
            },
            "Rental Income - Plant & Machinery": {
                "keywords": ["rent", "equipment rent", "machinery rent", "asset rent"],
                "variations": ["P&M rent", "equip rent", "machinery hire"]
            },
            "Capital Gains - Short Term": {
                "keywords": ["STCG", "short term", "capital gain", "sale of asset"],
                "variations": ["STCG", "ST cap gain", "short term gain"]
            },
            "Capital Gains - Long Term": {
                "keywords": ["LTCG", "long term", "capital gain", "asset sale"],
                "variations": ["LTCG", "LT cap gain", "long term gain"]
            },
            "Foreign Exchange Gain": {
                "keywords": ["forex gain", "exchange gain", "currency gain", "forex profit"],
                "variations": ["forex gain", "FX gain", "exchange rate gain"]
            },
            "Profit on Sale of Assets": {
                "keywords": ["profit", "asset sale", "gain on disposal", "sale gain"],
                "variations": ["profit on sale", "disposal gain", "asset sale profit"]
            },
            "Bad Debts Recovered": {
                "keywords": ["bad debt recovery", "debt recovered", "written off recovered"],
                "variations": ["debt recovered", "recovery", "bad debt collection"]
            },
            "Sundry Balances Written Back": {
                "keywords": ["written back", "liability write back", "reversal", "credit balance"],
                "variations": ["write back", "reversal", "creditor write back"]
            },
            "Discount Received": {
                "keywords": ["discount", "cash discount", "trade discount", "vendor discount"],
                "variations": ["disc rec", "cash disc", "supplier discount"]
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
            "Purchase of Trading Goods": {
                "keywords": ["trading goods", "purchase", "stock purchase", "merchandise"],
                "variations": ["trading purchase", "stock buy", "goods purchase"]
            },
            "Purchase of Packing Materials": {
                "keywords": ["packing purchase", "packaging", "carton", "wrapper"],
                "variations": ["pack purchase", "pkg buy", "packaging procurement"]
            },
            "Freight Inward": {
                "keywords": ["freight inward", "inward freight", "transport inward", "carriage"],
                "variations": ["freight in", "transport in", "carriage inward"]
            },
            "Import Duty": {
                "keywords": ["import duty", "customs duty", "import tax", "duty on RM"],
                "variations": ["import duty", "customs", "duty on imported"]
            },
            "Octroi and Local Taxes": {
                "keywords": ["octroi", "local tax", "entry tax", "municipal tax"],
                "variations": ["octroi", "entry tax", "local levy"]
            },
            "Power and Fuel": {
                "keywords": ["power", "fuel", "electricity", "diesel", "coal"],
                "variations": ["power & fuel", "elec cost", "electricity"]
            },
            "Stores and Spares Consumed": {
                "keywords": ["stores consumed", "spares", "consumables", "maintenance material"],
                "variations": ["S&S consumed", "consumables", "stores expense"]
            },
            "Direct Labour": {
                "keywords": ["labour", "wages", "direct labour", "worker cost"],
                "variations": ["labour cost", "wages", "worker wages"]
            },
            "Job Work Charges": {
                "keywords": ["job work", "outsource", "subcontracting", "processing charges"],
                "variations": ["job work exp", "outsource", "subcontract"]
            },
            "Manufacturing Expenses": {
                "keywords": ["manufacturing", "production expense", "factory cost"],
                "variations": ["mfg exp", "prod cost", "factory expense"]
            },
            
            # ============= EXPENSES - EMPLOYEE BENEFITS =============
            "Salaries and Wages": {
                "keywords": ["salary", "wages", "remuneration", "pay", "basic salary"],
                "variations": ["sal & wages", "remuner", "employee salary"]
            },
            "Bonus to Employees": {
                "keywords": ["bonus", "incentive", "performance bonus", "annual bonus"],
                "variations": ["bonus", "incentive", "performance pay"]
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
            "Leave Encashment Expense": {
                "keywords": ["leave", "leave encashment", "earned leave", "compensated absence"],
                "variations": ["leave exp", "EL cost", "leave provision"]
            },
            "Staff Welfare": {
                "keywords": ["staff welfare", "employee welfare", "welfare expense", "canteen"],
                "variations": ["welfare exp", "emp welfare", "canteen"]
            },
            "Recruitment Expenses": {
                "keywords": ["recruitment", "hiring cost", "placement fees"],
                "variations": ["recruit exp", "hiring cost", "placement"]
            },
            "Training and Development": {
                "keywords": ["training", "development", "employee training", "skill development"],
                "variations": ["training exp", "dev cost", "skill development"]
            },
            "Workmen Compensation": {
                "keywords": ["workmen compensation", "labour insurance", "worker insurance"],
                "variations": ["WC insurance", "labour ins", "worker compensation"]
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
            "Interest on Debentures": {
                "keywords": ["interest", "debenture", "bond interest", "debt interest"],
                "variations": ["deb int", "bond int", "NCD interest"]
            },
            "Bank Charges": {
                "keywords": ["bank charges", "bank fees", "processing fees", "service charges"],
                "variations": ["bank charges", "fees", "bank commission"]
            },
            "LC Charges": {
                "keywords": ["LC charges", "letter of credit", "LC commission"],
                "variations": ["LC charges", "LC comm", "documentary credit"]
            },
            "Bank Guarantee Charges": {
                "keywords": ["BG charges", "guarantee commission", "bank guarantee"],
                "variations": ["BG charges", "guarantee", "BG commission"]
            },
            "Discount on Bill Discounting": {
                "keywords": ["discount", "bill discount", "discounting charges"],
                "variations": ["bill disc", "disc charges", "invoice discount"]
            },
            "Interest to Related Parties": {
                "keywords": ["related party interest", "group interest", "director interest"],
                "variations": ["RP int", "group int", "director loan interest"]
            },
            "Other Borrowing Costs": {
                "keywords": ["borrowing cost", "other interest", "finance expense"],
                "variations": ["other borrow", "misc int", "finance cost"]
            },
            
            # ============= EXPENSES - DEPRECIATION =============
            "Depreciation - Building": {
                "keywords": ["depreciation", "building", "structure", "depr"],
                "variations": ["depr bldg", "building depr", "depreciation on building"]
            },
            "Depreciation - Plant & Machinery": {
                "keywords": ["depreciation", "plant", "machinery", "equipment"],
                "variations": ["depr P&M", "mach depr", "equipment depreciation"]
            },
            "Depreciation - Furniture": {
                "keywords": ["depreciation", "furniture", "fixture", "fitting"],
                "variations": ["depr F&F", "furn depr", "furniture depreciation"]
            },
            "Depreciation - Vehicles": {
                "keywords": ["depreciation", "vehicle", "car", "automobile"],
                "variations": ["depr veh", "vehicle depr", "car depreciation"]
            },
            "Depreciation - Computers": {
                "keywords": ["depreciation", "computer", "office equipment", "IT"],
                "variations": ["depr comp", "IT depr", "computer depreciation"]
            },
            "Amortization - Intangible Assets": {
                "keywords": ["amortization", "intangible", "goodwill", "software"],
                "variations": ["amort", "intang amort", "software amortization"]
            },
            "Impairment Loss": {
                "keywords": ["impairment", "loss", "asset impairment", "write down"],
                "variations": ["impair loss", "write down", "impairment charge"]
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
            "Repairs and Maintenance - Building": {
                "keywords": ["repairs", "maintenance", "building", "upkeep"],
                "variations": ["R&M bldg", "building repair", "building maintenance"]
            },
            "Repairs and Maintenance - Machinery": {
                "keywords": ["repairs", "maintenance", "machinery", "equipment"],
                "variations": ["R&M mach", "equip repair", "machinery maintenance"]
            },
            "Repairs and Maintenance - Others": {
                "keywords": ["repairs", "maintenance", "general", "other"],
                "variations": ["R&M other", "gen repair", "general maintenance"]
            },
            "Telephone and Internet": {
                "keywords": ["telephone", "internet", "mobile", "communication"],
                "variations": ["phone", "internet exp", "communication"]
            },
            "Postage and Courier": {
                "keywords": ["postage", "courier", "shipping", "delivery"],
                "variations": ["postage", "courier", "shipping costs"]
            },
            "Printing and Stationery": {
                "keywords": ["printing", "stationery", "office supplies", "paper"],
                "variations": ["print & stat", "stationery", "office supplies"]
            },
            "Electricity and Water": {
                "keywords": ["electricity", "water", "utility", "power"],
                "variations": ["elec & water", "utility", "power charges"]
            },
            "Legal and Professional Fees": {
                "keywords": ["legal", "professional", "consultant", "advisory"],
                "variations": ["legal & prof", "consultant", "professional fees"]
            },
            "Audit Fees": {
                "keywords": ["audit", "auditor", "statutory audit", "audit charges"],
                "variations": ["audit fees", "auditor", "CA fees"]
            },
            "ROC Filing Fees": {
                "keywords": ["ROC", "MCA", "filing fees", "compliance"],
                "variations": ["ROC fees", "MCA", "company filing"]
            },
            "Travelling and Conveyance": {
                "keywords": ["travelling", "conveyance", "travel", "transport"],
                "variations": ["travel & conv", "travel exp", "conveyance"]
            },
            "Vehicle Running and Maintenance": {
                "keywords": ["vehicle", "running", "maintenance", "fuel"],
                "variations": ["vehicle R&M", "car exp", "vehicle fuel"]
            },
            "Advertisement and Publicity": {
                "keywords": ["advertisement", "publicity", "marketing", "promotion"],
                "variations": ["adv & pub", "marketing", "advertising"]
            },
            "Sales Promotion": {
                "keywords": ["sales promotion", "promotion", "incentive", "marketing"],
                "variations": ["sales promo", "promo", "promotional"]
            },
            "Commission to Agents": {
                "keywords": ["commission", "agent", "brokerage", "intermediary"],
                "variations": ["comm paid", "agent comm", "brokerage expense"]
            },
            "Discount Allowed": {
                "keywords": ["discount", "sales discount", "trade discount", "cash discount"],
                "variations": ["disc allowed", "sales disc", "trade discount"]
            },
            "Bad Debts Written Off": {
                "keywords": ["bad debts", "write off", "irrecoverable", "debt loss"],
                "variations": ["bad debt", "write off", "debt loss"]
            },
            "Provision for Bad Debts": {
                "keywords": ["provision", "doubtful debts", "bad debt provision"],
                "variations": ["prov bad debt", "doubtful", "provision for doubtful"]
            },
            "Directors' Sitting Fees": {
                "keywords": ["director", "sitting fees", "meeting fees", "board fees"],
                "variations": ["dir sitting", "board fees", "director meeting"]
            },
            "Directors' Commission": {
                "keywords": ["director", "commission", "managerial remuneration"],
                "variations": ["dir comm", "managerial rem", "director profit"]
            },
            "Donations and Contributions": {
                "keywords": ["donation", "contribution", "charity", "CSR"],
                "variations": ["donation", "CSR", "charitable"]
            },
            "CSR Expenditure": {
                "keywords": ["CSR", "corporate social responsibility", "CSR spend"],
                "variations": ["CSR exp", "CSR spend", "CSR activities"]
            },
            "Loss on Sale of Assets": {
                "keywords": ["loss", "asset sale", "disposal loss", "loss on disposal"],
                "variations": ["loss on sale", "disposal loss", "asset sale loss"]
            },
            "Foreign Exchange Loss": {
                "keywords": ["forex loss", "exchange loss", "currency loss", "forex"],
                "variations": ["forex loss", "FX loss", "exchange rate loss"]
            },
            "Miscellaneous Expenses": {
                "keywords": ["miscellaneous", "sundry expenses", "general", "other"],
                "variations": ["misc exp", "sundry", "general expenses"]
            },
            
            # ============= GST SPECIFIC =============
            "CGST Input": {
                "keywords": ["CGST", "input", "input tax credit", "central GST"],
                "variations": ["CGST ITC", "CGST input", "central GST input"]
            },
            "SGST Input": {
                "keywords": ["SGST", "input", "input tax credit", "state GST"],
                "variations": ["SGST ITC", "SGST input", "state GST input"]
            },
            "IGST Input": {
                "keywords": ["IGST", "input", "input tax credit", "integrated GST"],
                "variations": ["IGST ITC", "IGST input", "integrated GST input"]
            },
            "GST RCM Input": {
                "keywords": ["RCM", "reverse charge", "input", "ITC"],
                "variations": ["RCM ITC", "RCM input", "reverse charge input"]
            },
            "CGST Output": {
                "keywords": ["CGST", "output", "output tax", "liability"],
                "variations": ["CGST output", "CGST liab", "central GST output"]
            },
            "SGST Output": {
                "keywords": ["SGST", "output", "output tax", "liability"],
                "variations": ["SGST output", "SGST liab", "state GST output"]
            },
            "IGST Output": {
                "keywords": ["IGST", "output", "output tax", "liability"],
                "variations": ["IGST output", "IGST liab", "integrated GST output"]
            },
            "GST RCM Output": {
                "keywords": ["RCM", "reverse charge", "output", "liability"],
                "variations": ["RCM output", "RCM liab", "reverse charge payable"]
            },
            
            # ============= TAX AUDIT SPECIFIC =============
            "Deemed Dividend u/s 2(22)(e)": {
                "keywords": ["deemed dividend", "2(22)e", "shareholder loan", "advance"],
                "variations": ["deemed div", "2(22)e", "section 2(22)(e)"]
            },
            "Disallowance u/s 40(a)(ia)": {
                "keywords": ["40(a)(ia)", "TDS default", "non-payment", "disallowance"],
                "variations": ["40a(ia)", "TDS default", "section 40"]
            },
            "Disallowance u/s 40A(3)": {
                "keywords": ["40A(3)", "cash payment", "exceeding limit", "disallowance"],
                "variations": ["40A3", "cash pay", "section 40A"]
            },
            "Disallowance u/s 43B": {
                "keywords": ["43B", "statutory payment", "actual payment", "unpaid"],
                "variations": ["43B", "stat unpaid", "section 43B"]
            },
            "Depreciation as per IT Act": {
                "keywords": ["depreciation", "IT Act", "tax depreciation", "block"],
                "variations": ["tax depr", "IT depr", "block depreciation"]
            },
            "Additional Depreciation u/s 32": {
                "keywords": ["additional depreciation", "section 32", "20% additional"],
                "variations": ["addl depr", "32 addl", "additional depr"]
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
        matches = []
        
        # Check base keywords
        for keyword in keywords.get("keywords", []):
            keyword_normalized = self._normalize_text(keyword)
            if keyword_normalized in ledger_normalized:
                score += 30
                matches.append(keyword)
        
        # Check variations
        for variation in keywords.get("variations", []):
            variation_normalized = self._normalize_text(variation)
            if variation_normalized in ledger_normalized:
                score += 20
                matches.append(variation)
        
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
        
        Parameters:
        -----------
        ledger_name : str
            Name of the ledger from trial balance
        threshold : int
            Minimum score threshold for confident match (default: 60)
        
        Returns:
        --------
        Dict with PBC mapping details
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
        
        Parameters:
        -----------
        df : pd.DataFrame
            Trial balance dataframe
        ledger_column : str, optional
            Name of column containing ledger names. If None, will auto-detect.
        debit_column : str, optional
            Name of column containing debit amounts
        credit_column : str, optional
            Name of column containing credit amounts
        threshold : int
            Minimum confidence score threshold
        
        Returns:
        --------
        pd.DataFrame with PBC mappings
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
        summary = {
            'total_ledgers': len(result_df),
            'high_confidence': len(result_df[result_df['Confidence_Level'] == 'High']),
            'medium_confidence': len(result_df[result_df['Confidence_Level'] == 'Medium']),
            'low_confidence': len(result_df[result_df['Confidence_Level'] == 'Low']),
            'avg_confidence_score': round(result_df['Confidence_Score'].mean(), 2),
            'success_rate': round((len(result_df[result_df['Confidence_Level'] != 'Low']) / len(result_df) * 100), 2)
        }
        
        return summary
