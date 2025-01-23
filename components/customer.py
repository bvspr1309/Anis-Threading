import sqlite3

# Path to the SQLite database file
DB_PATH = 'database/business.db'

def initialize_database():
    """
    Initializes the database by creating tables defined in the schema.sql file.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        with open('database/schema.sql', 'r') as schema_file:
            conn.executescript(schema_file.read())
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def add_customer(name, phone):
    """
    Adds a new customer to the database.
    
    Args:
        name (str): The name of the customer.
        phone (str): The phone number of the customer.
    
    Returns:
        bool: True if the customer was added successfully, False if the phone number already exists.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        print(f"Customer '{name}' added successfully!")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Customer with phone number '{phone}' already exists.")
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
    Retrieves all customers from the database.
    
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

def delete_customer_by_phone(phone):
    """
    Deletes a customer from the database using their phone number.
    
    Args:
        phone (str): The phone number of the customer to delete.
    
    Returns:
        bool: True if the customer was deleted successfully, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM customers WHERE phone = ?", (phone,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Customer with phone number '{phone}' deleted successfully!")
            return True
        else:
            print(f"No customer found with phone number '{phone}'.")
            return False
    except Exception as e:
        print(f"Error deleting customer: {e}")
        return False
    finally:
        conn.close()

def update_customer_name(phone, new_name):
    """
    Updates a customer's name in the database.
    
    Args:
        phone (str): The phone number of the customer to update.
        new_name (str): The new name of the customer.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE customers SET name = ? WHERE phone = ?", (new_name, phone))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Customer with phone number '{phone}' updated successfully!")
            return True
        else:
            print(f"No customer found with phone number '{phone}'.")
            return False
    except Exception as e:
        print(f"Error updating customer: {e}")
        return False
    finally:
        conn.close()

# Test the functions if this file is run directly
if __name__ == "__main__":
    # Initialize the database (run this only once)
    initialize_database()
    
    # Add test customers
    add_customer("John Doe", "1234567890")
    add_customer("Jane Smith", "9876543210")
    
    # Retrieve a customer by phone
    customer = get_customer_by_phone("1234567890")
    if customer:
        print("Retrieved Customer:", customer)
    else:
        print("Customer not found.")
    
    # Get all customers
    print("All Customers:")
    for customer in get_all_customers():
        print(customer)
    
    # Update a customer's name
    update_customer_name("1234567890", "Johnathan Doe")
    
    # Delete a customer
    delete_customer_by_phone("9876543210")
