import sqlite3
from components.combo import add_combo, get_combo_types

# Path to the SQLite database file
DB_PATH = 'database/business.db'

# ============================
# Customer Management
# ============================

def add_customer(name, phone, combo_type_id):
    """
    Adds a new customer to the system and assigns a combo to them.

    Args:
        name (str): The name of the customer.
        phone (str): The phone number of the customer.
        combo_type_id (int): The ID of the combo type being assigned to the customer.

    Returns:
        bool: True if the customer and combo were added successfully, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
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

def get_customer_by_phone(phone):
    """
    Retrieves a customer's information using their phone number.

    Args:
        phone (str): The phone number of the customer.

    Returns:
        tuple: The customer's details (id, name, phone) if found, otherwise None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
        customer = cursor.fetchone()
        return customer
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
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
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
    # Initialize test data
    combo_types = get_combo_types()
    if not combo_types:
        print("No combo types found. Add combo types before testing!")
    else:
        # Use the first available combo type
        combo_type_id = combo_types[0][0]
        
        # Test adding a customer with a combo
        add_customer("John Doe", "1234567890", combo_type_id)
        add_customer("Jane Smith", "9876543210", combo_type_id)
        
        # Test retrieving a customer by phone
        print("Customer by phone (1234567890):", get_customer_by_phone("1234567890"))
        
        # Test retrieving all customers
        print("All Customers:")
        for customer in get_all_customers():
            print(customer)
        
        # Test deleting a customer
        customer = get_customer_by_phone("1234567890")
        if customer:
            delete_customer(customer[0])
        
        # Test removing a customer if combos are used up
        customer = get_customer_by_phone("9876543210")
        if customer:
            remove_customer_if_combos_used_up(customer[0])
