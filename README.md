# 📉 Automated Trade Reconciliation System

### 🚀 Project Overview
A Python-based reconciliation engine designed to automate trade settlement workflows. It ingests Internal Ledger and External Bank Statement data, performing an **Outer Join** to identify discrepancies in Price, Quantity, or Settlement Status.

### 🛠️ Features
* **Auto-Categorization:** Uses conditional logic to classify breaks (e.g., "PRICE MISMATCH" vs "MISSING IN BANK").
* **Visual Reporting:** Exports a conditionally formatted Excel dashboard using `XlsxWriter` for immediate risk visibility.
* **Scalability:** Tested on 500+ trade rows with simulated data noise.

### 
