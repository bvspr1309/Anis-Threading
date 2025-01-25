import sqlite3
from components.combo import add_combo, get_combo_types, get_db_connection

# Path to the SQLite database file
DB_PATH = 'database/business.db'

# ============================
# Database Initialization
# ============================

def initialize_database():
    """
    Initializes the database by creating tables defined in the schema.sql file.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)
    try:
        print("Initializing database...")
        conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode for better concurrency
        with open('database/schema.sql', 'r') as schema_file:
            conn.executescript(schema_file.read())
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

# ============================
# Customer Management
# ============================

def add_customer(name, phone, combo_type_id):
    """
    Adds a new customer to the system and assigns a combo to them.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)
    print("Opening connection in add_customer")
    cursor = conn.cursor()
    try:
        # Add customer to the database
        cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
        customer_id = cursor.lastrowid  # Get the newly created customer's ID

        # Add the combo for the customer
        if not add_combo(customer_id, combo_type_id):
            raise Exception("Failed to add combo for the customer.")

        conn.commit()
        print(f"Customer '{name}' added successfully with combo type ID {combo_type_id}!")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Customer with phone number '{phone}' already exists.")
        return False
    except Exception as e:
        print(f"Error adding customer: {e}")
        return False
    finally:
        conn.close()
        print("Closing connection in add_customer")


def get_customer_by_phone(phone):
    """
    Retrieves a customer's information using their phone number.

    Args:
        phone (str): The phone number of the customer.

    Returns:
        dict or None: The customer's details (id, name, phone) if found, otherwise None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
        customer = cursor.fetchone()
        return customer  # Returns a dictionary-like row
    except Exception as e:
        print(f"Error retrieving customer: {e}")
        return None
    finally:
        conn.close()

def get_all_customers():
    """
    Retrieves all customers from the system.

    Returns:
        list of tuples: List of all customers (id, name, phone).
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        return customers
    except Exception as e:
        print(f"Error retrieving customers: {e}")
        return []
    finally:
        conn.close()

def delete_customer(customer_id):
    """
    Deletes a customer and their associated combos from the system.

    Args:
        customer_id (int): The ID of the customer to delete.

    Returns:
        bool: True if the customer was deleted successfully, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    try:
        # Delete the customer's combos first
        cursor.execute("DELETE FROM combos WHERE customer_id = ?", (customer_id,))
        
        # Delete the customer
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        print(f"Customer ID {customer_id} deleted successfully!")
        return True
    except Exception as e:
        print(f"Error deleting customer: {e}")
        return False
    finally:
        conn.close()

def remove_customer_if_combos_used_up(customer_id):
    """
    Checks if a customer has any remaining combos, and deletes the customer if all combos are used up.

    Args:
        customer_id (int): The ID of the customer.

    Returns:
        bool: True if the customer was removed, False if the customer still has active combos or an error occurred.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM combos WHERE customer_id = ? AND remaining_uses > 0",
            (customer_id,)
        )
        active_combos_count = cursor.fetchone()[0]
        if active_combos_count == 0:
            return delete_customer(customer_id)
        return False
    except Exception as e:
        print(f"Error checking customer combos: {e}")
        return False
    finally:
        conn.close()

# ============================
# Test Functions
# ============================

if __name__ == "__main__":
    # Initialize the database
    initialize_database()

    # Test adding a customer
    print("Testing customer addition...")
    combo_types = get_combo_types()
    if combo_types:
        combo_type_id = combo_types[0][0]  # Use the first combo type for testing
        add_customer("John Doe", "1234567890", combo_type_id)

    # Test retrieving all customers
    print("All Customers:")
    for customer in get_all_customers():
        print(customer)
