import pandas as pd
import pymysql
import matplotlib.pyplot as plt
from datetime import date
import os

# setup folder
OUTPUT_DIR = "sample_output"
MAKING_CHARGE = 0.20
os.makedirs(OUTPUT_DIR, exist_ok=True)

# connect to db
conn = pymysql.connect(host='localhost', user='root', password='YOUR_MYSQL_PASSWORD', database='jewellery_db')
cursor = conn.cursor()

# ---------- utilities ----------
def load_catalogue():
    try:
        return pd.read_csv("Catalogue.txt")
    except FileNotFoundError:
        print("'Catalogue.txt' missing!")
        return None

def get_latest_prices():
    try:
        df = pd.read_csv("metal_prices.txt")
        last = df.iloc[-1]
        return {"gold": last["Gold"], "silver": last["Silver"]}
    except FileNotFoundError:
        print("'metal_prices.txt' missing!")
        return None

# ---------- customer stuff ----------
def add_customer():
    n = input("Name: ")
    ph = input("Phone: ")
    em = input("Email: ")
    cursor.execute("INSERT INTO customers (name, phone, email) VALUES (%s,%s,%s)", (n, ph, em))
    conn.commit()
    print("Customer added\n")

def view_customers():
    cursor.execute("SELECT customer_id,name,phone,email FROM customers")
    df = pd.DataFrame(cursor.fetchall(), columns=["id", "name", "phone", "email"])
    if df.empty:
        print("No customers!\n")
    else:
        print("Customer list:")
        print(df.to_string(index=False))

# ---------- invoice ----------
def create_invoice():
    cursor.execute("SELECT customer_id,name FROM customers")
    custs = cursor.fetchall()
    if not custs:
        print("No customers yet. Add one first.\n")
        return

    print("\nCustomers:")
    for c in custs:
        print(f"{c[0]} - {c[1]}")
    print()

    try:
        cid = int(input("Customer ID: "))
    except:
        print("Invalid ID")
        return

    cat = load_catalogue()
    prices = get_latest_prices()
    if cat is None or prices is None or cat.empty:
        return

    items = []
    while True:
        print("\nItems:")
        for i, row in cat.iterrows():
            print(f"{i+1}. {row['Item']} ({row['Metal']},{row['Weight_g']}g)")

        try:
            ch = int(input("Select item (0 to close): "))
            if ch == 0:
                break
            if 1 <= ch <= len(cat):
                sel = cat.iloc[ch - 1]
                metal = sel['Metal'].lower()
                if metal not in prices:
                    print(f"{metal} price missing!")
                    continue
                qty = int(input("Qty: "))

                # ---- price calculation ----
                base_price = prices[metal] * sel['Weight_g'] * qty
                making_charge_val = base_price * MAKING_CHARGE
                subtotal = base_price + making_charge_val

                if metal == "gold":
                    gst_rate = 0.03
                else:
                    gst_rate = 0.05

                gst = subtotal * gst_rate
                total_price = subtotal + gst
                items.append((sel['Item'], qty, base_price/qty, making_charge_val/qty, gst_rate * 100, gst/qty, total_price/qty))

                print(f"{sel['Item']} x{qty} @ ₹{total_price/qty:.2f} each "
                      f"(includes ₹{making_charge_val/qty:.2f} making charge, {gst_rate*100:.1f}% GST = ₹{gst/qty:.2f} per item)")
        except:
            print("Invalid input")

    if not items:
        print("No items selected")
        return

    df_inv = pd.DataFrame(items, columns=["item", "qty", "base_price", "making_charge", "gst_rate(%)", "gst", "unit_price"])
    df_inv["total"] = df_inv["qty"] * df_inv["unit_price"]
    tot = df_inv["total"].sum()

    cursor.execute("INSERT INTO invoices (customer_id,date,total) VALUES (%s,%s,%s)", (cid, date.today(), tot))
    inv_id = cursor.lastrowid

    for _, r in df_inv.iterrows():
        cursor.execute("INSERT INTO invoice_items (invoice_id,item_name,quantity,rate,total_price) VALUES (%s,%s,%s,%s,%s)",
                       (inv_id, r["item"], r["qty"], r["unit_price"], r["total"]))
    conn.commit()

    cursor.execute("SELECT name,phone,email FROM customers WHERE customer_id=%s", (cid,))
    cname, cphone, cemail = cursor.fetchone()

    cust_df = pd.DataFrame([
        ["Customer Name", cname],
        ["Phone", cphone],
        ["Email", cemail],
        ["Invoice ID", inv_id],
        ["Date", date.today()]
    ], columns=["field", "value"])

    total_row = pd.DataFrame([["Total", "", "", "", "", "", tot]],
                             columns=["item", "qty", "base_price", "making_charge", "gst_rate(%)", "gst", "unit_price"])
    export_df = pd.concat([cust_df, pd.DataFrame([["", "", "", "", "", "", ""]], columns=total_row.columns),
                           df_inv, total_row], ignore_index=True)

    csv_path = f"{OUTPUT_DIR}/invoice_{inv_id}.csv"
    export_df.to_csv(csv_path, index=False)
    print(f"\nInvoice #{inv_id} saved to {csv_path}\n")

# ---------- view invoices ----------
def view_invoices():
    cursor.execute("SELECT i.invoice_id,i.date,c.name,i.total FROM invoices i JOIN customers c ON i.customer_id=c.customer_id ORDER BY i.invoice_id DESC")
    df = pd.DataFrame(cursor.fetchall(), columns=["invoice_id", "date", "customer", "total"])
    if df.empty:
        print("No invoices!\n")
        return
    print("Past invoices:")
    print(df.to_string(index=False))

    try:
        iid = int(input("\nInvoice ID (0 cancel): "))
        if iid == 0:
            return
        cursor.execute("SELECT item_name,quantity,rate,total_price FROM invoice_items WHERE invoice_id=%s", (iid,))
        df_it = pd.DataFrame(cursor.fetchall(), columns=["item", "qty", "rate", "total"])
        print(f"\nInvoice {iid} details:")
        print(df_it.to_string(index=False))
    except:
        print("Invalid input")

# ---------- charts ----------
def show_price_growth():
    df = pd.read_csv("metal_prices.txt")
    fig, ax = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
    ax[0].plot(df["Year"], df["Gold"], marker='o', color='gold', linewidth=2)
    ax[0].set_title("Gold Prices Over Years")
    ax[0].set_ylabel("Gold (₹)")
    ax[0].grid(True, linestyle='--', alpha=0.7)
    ax[1].plot(df["Year"], df["Silver"], marker='o', color='gray', linewidth=2)
    ax[1].set_title("Silver Prices Over Years")
    ax[1].set_xlabel("Year")
    ax[1].set_ylabel("Silver (₹)")
    ax[1].grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def show_jewellery_summary():
    cursor.execute("SELECT item_name,SUM(total_price) FROM invoice_items GROUP BY item_name")
    data = cursor.fetchall()
    if not data:
        print("No sales data")
        return
    df_sum = pd.DataFrame(data, columns=["item", "total_sales"])
    tot_sales = df_sum["total_sales"].sum()
    print("=== Jewellery Sales Summary ===")
    print(df_sum.to_string(index=False))
    print(f"TOTAL SALES: ₹{tot_sales:,.2f}\n")

    plt.figure(figsize=(10, 6))
    plt.bar(df_sum["item"], df_sum["total_sales"], color=plt.cm.Paired.colors)
    plt.title(f"Sales Breakdown\nTotal ₹{tot_sales:,.2f}")
    plt.xlabel("Item")
    plt.ylabel("Total (₹)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# ---------- menu ----------
def main():
    while True:
        print("\n===== Jewellery Invoice System =====")
        print("1. Add Customer")
        print("2. View Customers")
        print("3. Create Invoice")
        print("4. View Past Invoices")
        print("5. Show Metal Price Growth")
        print("6. Show Jewellery Sales Summary")
        print("7. Exit")
        choice = input("Select: ")
        if choice == '1':
            add_customer()
        elif choice == '2':
            view_customers()
        elif choice == '3':
            create_invoice()
        elif choice == '4':
            view_invoices()
        elif choice == '5':
            show_price_growth()
        elif choice == '6':
            show_jewellery_summary()
        elif choice == '7':
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
