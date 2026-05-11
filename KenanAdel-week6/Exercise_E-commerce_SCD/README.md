# E-commerce Data Pipeline

## Project Overview
This project is an automated Data Engineering pipeline designed to extract e-commerce data from a transactional PostgreSQL database (`hi_DB`), transform it into a dimensional model using Python and Pandas, and load it into a target Data Warehouse (`hi_DWH`). 

The pipeline supports both **Initial Load** (bulk import and table creation) and **Incremental Load** (updating changes and capturing historical data changes via Slowly Changing Dimensions - SCD Type 2).

## Project Structure
```text
Code/
  ├── notebook_for_practice/
  │    └── kenan.ipynb         # Jupyter Notebook for exploratory and pipeline testing
  ├── src_code/
  │    ├── initial_load.py     # Script to perform full table loads and build the Dimension and Fact tables from scratch
  │    └── incremental_load.py # Script specifically built to capture new/updated records and load them into the DWH
Photos/                        # There'r Photos for E-comerceDB and E-comerceDWH .. Normalization - Denormalization
```

## Prerequisites & Dependencies
To run this pipeline successfully, you will need the following installed:

*   **Python 3.8+**
*   **PostgreSQL** (Ensure you have two databases setup: `hi_DB` for source data and `hi_DWH` for target warehouse)
*   **Python Libraries:**
    *   `pandas` (Data manipulation)
    *   `SQLAlchemy` (Database connection and SQL execution)

### Database Configuration
Before running the code, make sure your PostgreSQL credentials are correct inside the scripts:
Both scripts connect to the databases via:
```python
engine = create_engine('postgresql://postgres:kenan123@localhost:5432/hi_DB')      # Source
engine_load = create_engine('postgresql://postgres:kenan123@localhost:5432/hi_DWH') # Target (Data Warehouse)
```
*(Update `postgres:kenan123` to match your local setup database user and password.)*

## Setup & Installation

1.  **Clone or Download** the project to your local machine.
2.  **Create a Virtual Environment** (Highly Recommended):
    ```bash
    python -m venv venv
    ```
3.  **Activate Virtual Environment**:
    *   *Windows:* `venv\Scripts\activate`
    *   *Mac/Linux:* `source venv/bin/activate`
4.  **Install Required Dependencies**:
    ```bash
    pip install pandas sqlalchemy
    ```
5.  **Database Preparation**:
    *   Create `hi_DB` and populate it with your source E-commerce tables (orders, order_items, users, products, categories, brands, branches, currencies).
    *   Create an empty `hi_DWH` database.

## How to Run

### 1. Perform an Initial Load
To initially populate your data warehouse and generate surrogate keys (`_sk`), execute `initial_load.py` first. This establishes the baseline for your Star Schema (Fact and Dimension tables).
```bash
python Code/src_code/initial_load.py
```

### 2. Perform Incremental Loads
For regular pipeline updates (e.g., ran via a cron job on a daily basis), run `incremental_load.py`. This reads recently updated records, expires old records using `end_date` and `is_active` flags, and inserts new active rows.
```bash
python Code/src_code/incremental_load.py
```

### 3. Explore data using Notebook
You can also use the Jupyter Notebook included for debugging or developing new schema features before adding them to production scripts:
```bash
pip install jupyter
jupyter notebook Code/notebook_for_practice/kenan.ipynb
```
