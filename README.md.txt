# Jewellery Invoice System

A Python-based **Jewellery Invoice System** developed as a Class 12 Informatics Practices project. The system uses Python, Pandas, Matplotlib and MySQL to manage customers, generate jewellery invoices, store sales information and display graphical data.

## Features

* Add and view customer details
* Create jewellery invoices
* Calculate jewellery prices based on:

  * Metal price
  * Weight
  * Quantity
  * Making charges
  * GST
* Store invoices and invoice items in a MySQL database
* View previous invoices
* Generate invoice files in CSV format
* Display gold and silver price growth using graphs
* Display a jewellery sales summary using a bar chart

## Technologies Used

* **Python**
* **MySQL**
* **Pandas** – data handling and CSV processing
* **Matplotlib** – graphs and data visualization
* **PyMySQL** – connecting Python with MySQL

## Project Structure

```text
Jewellery-Invoice-System/
│
├── main.py
├── Catalogue.txt
├── metal_prices.txt
├── requirements.txt
├── README.md
│
└── sample_output/
    └── invoice_*.csv
```

> The exact file names may be different depending on how the project is organized.

## Requirements

Make sure you have:

* Python 3
* MySQL Server
* A MySQL database named `jewellery_db`
* The required Python libraries

Install the Python libraries using:

```bash
pip install -r requirements.txt
```

## Input Files

### Catalogue.txt

This file contains the jewellery catalogue. It should contain columns such as:

```text
Item,Metal,Weight_g
```

Example:

```text
Gold Ring,Gold,5
Silver Chain,Silver,10
Gold Necklace,Gold,20
```

### metal_prices.txt

This file contains historical metal prices and should contain:

```text
Year,Gold,Silver
```

The program uses the latest row to obtain the current gold and silver prices.

## MySQL Database Setup

Create a MySQL database named:

```sql
CREATE DATABASE jewellery_db;
```

The program requires the following tables:

* `customers`
* `invoices`
* `invoice_items`

The database should contain the following fields:

### customers

```text
customer_id
name
phone
email
```

### invoices

```text
invoice_id
customer_id
date
total
```

### invoice_items

```text
invoice_id
item_name
quantity
rate
total_price
```

A database setup `.sql` file can be included in this repository to make database installation easier.

## Running the Project

1. Install Python 3.
2. Install MySQL Server.
3. Create the `jewellery_db` database and required tables.
4. Place `Catalogue.txt` and `metal_prices.txt` in the same folder as the Python program.
5. Install the required Python libraries:

```bash
pip install -r requirements.txt
```

6. Update the MySQL connection details in the Python program.
7. Run the program:

```bash
python main.py
```

## Main Menu

The program provides the following options:

```text
1. Add Customer
2. View Customers
3. Create Invoice
4. View Past Invoices
5. Show Metal Price Growth
6. Show Jewellery Sales Summary
7. Exit
```

## Price Calculation

The invoice calculation includes:

**Base Price**

```text
Metal Price × Weight × Quantity
```

**Making Charge**

```text
Base Price × 20%
```

**GST**

* Gold: 3%
* Silver: 5%

The final price is calculated by adding the base price, making charge and GST.

## Output

Generated invoices are saved as CSV files inside the `sample_output` folder.

Example:

```text
sample_output/
└── invoice_1.csv
```

The project also generates graphical visualizations for:

* Gold price growth over the years
* Silver price growth over the years
* Jewellery sales by item

## Important Note

The MySQL connection settings are specific to the computer on which the project is being run. Before running the program, update the database username, password and database settings as required.

For security, passwords and other private credentials should not be uploaded to GitHub.

## Project Purpose

This project demonstrates the use of Python programming, database connectivity, data handling, file handling and data visualization as part of a Class 12 Informatics Practices project.

## Author

**Class 12 Informatics Practices Project**

Name: *Your Name*
Class/Section: *Your Class & Section*
School: *Your School Name*

```
```
