# Hive Customer SCD Type 2 Implementation

## Project Description and Purpose
This project demonstrates how to implement a Slowly Changing Dimension (SCD) Type 2 using Apache Hive. It is designed to track historical changes to customer information over time. 

The process uses standard Hive SQL queries to:
1. Base table creation (Internal and External) to test setups.
2. Initialize a `customer_dim` dimension table with historical data.
3. Ingest fresh incoming data into a temporary `customer_stage` staging table.
4. Apply an `INSERT OVERWRITE` utilizing multiple `UNION ALL` statements to logically resolve unchanging records, mark old records as inactive (with dynamic `end_date`), and insert new records or new updates as active (`is_current = '1'`).

## Prerequisites and Required Dependencies
To run this project, make sure you have the following environment and dependencies configured:
- **Hadoop Ecosystem:** HDFS should be up and running.
- **Apache Hive:** Hive must be installed and properly configured (with the OpenCSVSerde library available to parse CSV files).
- **Paths:** A configured Hive server supporting standard SQL semantics (`date_format()`, `current_date()`).
- **File System:** 
  You need local access to copy the CSV files onto your local edge/Hadoop node before loading them into Hive, or adjust the scripting for HDFS generic loads.

## Step-by-Step Setup and Installation Instructions

1. **Clone or Download the Project:**
   Extract the files into a working directory Your folder should contain:
   * `Hive_Code/customer_scd2_mixed.csv`
   * `Hive_Code/customer_updated.csv`
   * `Hive_Code/Kenan_Script.sql`

2. **Move CSV files to your Hive Gateway Node:**
   The SQL script relies on loading data via the `LOAD DATA LOCAL INPATH` command. 
   Upload the `customer_scd2_mixed.csv` and `customer_updated.csv` to the `/home/itversity/` directory on your node (or update the file paths inside `Kenan_Script.sql` to match your actual Unix/Linux file system paths).
   ```bash
   mkdir -p /home/itversity/
   cp Hive_Code/*.csv /home/itversity/
   ```

3. **Verify File Permissions:**
   Ensure the `hive` user (or the user you are running Hive under) has read permissions on these CSV files.
   ```bash
   chmod 644 /home/itversity/*.csv
   ```

## How to Run and Use

### Running the Script
You can execute the script using DBeaver connected to your Hive environment.

**Using DBeaver:**
1. Open DBeaver and connect to your Apache Hive server.
2. Open a new SQL Editor window for the Hive connection.
3. Open `Hive_Code/Kenan_Script.sql` internally or copy its contents into the SQL Editor.
4. Execute the script using the **"Execute SQL Script"** button (or press `Alt + X`).

**What the script does when executed:**
1. **Initializes Test Tables:** It will first create and drop `customer_int` and `customer_ext` tables to test data ingress from standard comma-separated text files utilizing `OpenCSVSerde`.
2. **Dimension Build:** Sets up the `customer_dim` table and populates its initial snapshot. 
3. **Staging Build:** Sets up the `customer_stage` table with updated customer records.
4. **SCD Type 2 Merge:** Performs the overwrite using complex `UNION ALL` subsets (Inactive retention, active retention, active retirement, and fresh inserts). 

### Basic Data Query Example
Once the script has completed, you can check your SCD2 implementation by running the following query in your DBeaver SQL Editor:

```sql
-- View the full dimension tracking table
SELECT CustomerID, Name, Start_Date, End_Date, Is_Current 
FROM customer_dim 
ORDER BY CustomerID, Start_Date;
```

**Expected results logic:**
* A customer who changed their address or email will appear twice.
* The older record will have `Is_Current = '0'` and an updated `End_Date`.
* The latest record will retain `Is_Current = '1'` and the `End_Date` should be `NULL`.