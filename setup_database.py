"""
setup_database.py — Seeds SQLite with synthetic customer data.

Creates tables: customers, products, support_tickets
Populates with realistic synthetic data for demo purposes.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customer_support.db")


def create_tables(cursor: sqlite3.Cursor) -> None:
    """Create the database schema."""
    cursor.executescript("""
        DROP TABLE IF EXISTS support_tickets;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS products;

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            plan TEXT NOT NULL DEFAULT 'Basic',
            signup_date TEXT NOT NULL,
            city TEXT,
            country TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        );

        CREATE TABLE support_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id INTEGER,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            priority TEXT NOT NULL DEFAULT 'Medium',
            category TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            resolution_notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """)


def seed_products(cursor: sqlite3.Cursor) -> None:
    """Insert sample products."""
    products = [
        ("CloudSync Pro", "Software", 29.99, "Cloud storage and sync solution with 1TB space"),
        ("SecureVault", "Software", 49.99, "Enterprise-grade password manager"),
        ("DataFlow Analytics", "Software", 99.99, "Real-time business analytics dashboard"),
        ("SmartDesk Hub", "Hardware", 199.99, "USB-C powered desk hub with 10 ports"),
        ("QuickCharge Pad", "Hardware", 39.99, "Wireless charging pad with fast-charge support"),
        ("NoiseFree Headset", "Hardware", 149.99, "Active noise cancelling wireless headset"),
        ("PageGuard Antivirus", "Software", 19.99, "Lightweight antivirus and malware protection"),
        ("TeamChat Business", "Software", 12.99, "Team messaging and collaboration platform"),
        ("PrintMaster 3000", "Hardware", 299.99, "All-in-one wireless color printer"),
        ("CloudSync Basic", "Software", 9.99, "Cloud storage with 100GB space"),
    ]
    cursor.executemany(
        "INSERT INTO products (product_name, category, price, description) VALUES (?, ?, ?, ?)",
        products,
    )


def seed_customers(cursor: sqlite3.Cursor) -> None:
    """Insert sample customers."""
    customers = [
        ("Ema", "Rodriguez", "ema.rodriguez@email.com", "+1-555-0101", "Premium", "2023-01-15", "New York", "USA", 1),
        ("James", "Chen", "james.chen@email.com", "+1-555-0102", "Business", "2023-03-22", "San Francisco", "USA", 1),
        ("Sarah", "Williams", "sarah.w@email.com", "+1-555-0103", "Basic", "2023-06-10", "Chicago", "USA", 1),
        ("Mohammed", "Al-Rashid", "m.alrashid@email.com", "+44-20-5550104", "Premium", "2022-11-05", "London", "UK", 1),
        ("Priya", "Sharma", "priya.sharma@email.com", "+91-555-0105", "Business", "2023-08-18", "Mumbai", "India", 1),
        ("Lucas", "Bennett", "lucas.b@email.com", "+1-555-0106", "Basic", "2024-01-03", "Toronto", "Canada", 1),
        ("Yuki", "Tanaka", "yuki.tanaka@email.com", "+81-555-0107", "Premium", "2023-04-12", "Tokyo", "Japan", 1),
        ("Ana", "Silva", "ana.silva@email.com", "+55-555-0108", "Basic", "2023-09-25", "São Paulo", "Brazil", 1),
        ("David", "Miller", "david.m@email.com", "+1-555-0109", "Business", "2022-07-14", "Austin", "USA", 1),
        ("Fatima", "Hassan", "fatima.h@email.com", "+971-555-0110", "Premium", "2023-05-08", "Dubai", "UAE", 1),
        ("Oliver", "Schmidt", "oliver.s@email.com", "+49-555-0111", "Basic", "2024-02-20", "Berlin", "Germany", 1),
        ("Maria", "Garcia", "maria.g@email.com", "+34-555-0112", "Business", "2023-07-30", "Madrid", "Spain", 1),
        ("Kevin", "Park", "kevin.park@email.com", "+82-555-0113", "Premium", "2023-02-14", "Seoul", "South Korea", 1),
        ("Emma", "Johnson", "emma.j@email.com", "+1-555-0114", "Basic", "2023-11-01", "Seattle", "USA", 0),
        ("Carlos", "Mendoza", "carlos.m@email.com", "+52-555-0115", "Business", "2022-09-20", "Mexico City", "Mexico", 1),
    ]
    cursor.executemany(
        "INSERT INTO customers (first_name, last_name, email, phone, plan, signup_date, city, country, is_active) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        customers,
    )


def seed_tickets(cursor: sqlite3.Cursor) -> None:
    """Insert sample support tickets."""
    random.seed(42)
    categories = ["Billing", "Technical", "Account", "Product", "Refund", "General"]
    statuses = ["Open", "In Progress", "Resolved", "Escalated", "Closed"]
    priorities = ["Low", "Medium", "High", "Critical"]

    tickets = [
        # Ema's tickets
        (1, 1, "Cannot sync files", "My CloudSync Pro is not syncing files since yesterday. Getting error code 503.", "Resolved", "High", "Technical", "2024-01-10", "2024-01-11", "Server-side issue resolved. Customer confirmed sync working."),
        (1, None, "Billing discrepancy", "I was charged $59.99 instead of $29.99 for CloudSync Pro.", "Resolved", "Medium", "Billing", "2024-02-15", "2024-02-16", "Duplicate charge refunded. Credit applied to next billing cycle."),
        (1, 3, "Feature request - export", "Need ability to export analytics data to CSV format.", "Open", "Low", "Product", "2024-03-20", None, None),
        (1, None, "Password reset not working", "Cannot reset password. Reset email never arrives.", "Resolved", "High", "Account", "2024-04-05", "2024-04-05", "Email was going to spam. Whitelisted our domain for customer."),

        # James's tickets
        (2, 3, "Dashboard loading slow", "DataFlow Analytics dashboard takes 30+ seconds to load.", "In Progress", "High", "Technical", "2024-03-01", None, None),
        (2, 8, "Add user to TeamChat", "Need to add 5 new team members to our TeamChat Business account.", "Resolved", "Low", "Account", "2024-02-10", "2024-02-10", "Users added successfully. Sent onboarding guide."),

        # Sarah's tickets
        (3, 10, "Upgrade plan inquiry", "Want to upgrade from CloudSync Basic to Pro. What are the steps?", "Closed", "Low", "General", "2024-01-25", "2024-01-25", "Walked customer through upgrade process. Upgrade completed."),
        (3, 5, "Charging pad not working", "QuickCharge Pad stopped charging after 2 weeks of use.", "Escalated", "High", "Product", "2024-03-15", None, None),

        # Mohammed's tickets
        (4, 2, "Security concern", "Seeing unfamiliar login attempts on my SecureVault account.", "Resolved", "Critical", "Technical", "2024-02-28", "2024-02-28", "Enabled 2FA. Revoked suspicious sessions. No data breach confirmed."),
        (4, None, "Refund request", "Requesting refund for PageGuard Antivirus - not compatible with my system.", "Resolved", "Medium", "Refund", "2024-01-18", "2024-01-20", "Full refund processed. Compatibility requirements updated in docs."),

        # Priya's tickets
        (5, 3, "Data export failed", "Trying to export last quarter's data but getting timeout errors.", "Open", "Medium", "Technical", "2024-04-01", None, None),
        (5, 8, "Cannot share channels", "Unable to share TeamChat channels between departments.", "Resolved", "Medium", "Technical", "2024-03-10", "2024-03-12", "Permission settings updated. Cross-department sharing enabled."),

        # Lucas's tickets
        (6, 10, "Storage almost full", "Getting notifications that my 100GB storage is almost full.", "Open", "Low", "General", "2024-03-28", None, None),

        # Yuki's tickets
        (7, 6, "Headset bluetooth issue", "NoiseFree Headset keeps disconnecting from my laptop.", "In Progress", "Medium", "Product", "2024-04-02", None, None),
        (7, 1, "Request annual billing", "Want to switch from monthly to annual billing for CloudSync Pro.", "Resolved", "Low", "Billing", "2024-02-05", "2024-02-06", "Switched to annual billing. 20% discount applied."),

        # David's tickets
        (9, 4, "Hub not recognized", "SmartDesk Hub not being recognized by my MacBook Pro M3.", "Resolved", "High", "Technical", "2024-01-30", "2024-02-02", "Firmware update resolved the issue. Sent updated driver link."),
        (9, 3, "API access request", "Need API access for DataFlow Analytics to integrate with our CRM.", "Resolved", "Medium", "Product", "2024-03-05", "2024-03-07", "API key generated. Documentation shared."),

        # Fatima's tickets
        (10, 9, "Printer setup help", "Need help setting up PrintMaster 3000 with our network.", "Resolved", "Low", "Technical", "2024-02-22", "2024-02-23", "Remote session completed. Printer configured for network printing."),

        # Oliver's tickets
        (11, 7, "Subscription cancellation", "Want to cancel PageGuard Antivirus subscription.", "Closed", "Low", "Billing", "2024-03-18", "2024-03-18", "Subscription cancelled. Feedback collected."),

        # Maria's tickets
        (12, 3, "Custom report builder", "Custom report builder crashes when adding more than 10 metrics.", "Open", "High", "Technical", "2024-04-03", None, None),
        (12, 8, "Integrations not syncing", "TeamChat integration with email not syncing messages.", "In Progress", "Medium", "Technical", "2024-03-25", None, None),

        # Kevin's tickets
        (13, 2, "Multi-device sync", "SecureVault not syncing passwords between phone and desktop.", "Resolved", "Medium", "Technical", "2024-03-02", "2024-03-04", "App update on phone resolved sync issue."),
        (13, None, "Invoice request", "Need tax invoices for all 2023 purchases.", "Resolved", "Low", "Billing", "2024-01-05", "2024-01-06", "Invoices generated and emailed."),

        # Carlos's tickets
        (15, 4, "Hub overheating", "SmartDesk Hub gets very hot after extended use.", "Escalated", "Critical", "Product", "2024-04-01", None, None),
        (15, 3, "Team dashboard access", "New hires cannot access the shared team dashboard.", "Resolved", "Medium", "Account", "2024-03-12", "2024-03-13", "Team roles updated. Access granted to new members."),
    ]

    cursor.executemany(
        "INSERT INTO support_tickets (customer_id, product_id, subject, description, status, priority, category, created_at, resolved_at, resolution_notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        tickets,
    )


def setup_database() -> str:
    """Create and seed the database. Returns the database path."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_tables(cursor)
    seed_products(cursor)
    seed_customers(cursor)
    seed_tickets(cursor)

    conn.commit()

    # Print summary
    cursor.execute("SELECT COUNT(*) FROM customers")
    customers_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM support_tickets")
    tickets_count = cursor.fetchone()[0]

    print(f"✅ Database created at: {DB_PATH}")
    print(f"   → {customers_count} customers")
    print(f"   → {products_count} products")
    print(f"   → {tickets_count} support tickets")

    conn.close()
    return DB_PATH


if __name__ == "__main__":
    setup_database()
