import sqlite3

# Path to the SQLite database file
DB_PATH = 'database/business.db'

# ============================
# Helper Function
# ============================

def get_db_connection():
    """
    Provides a single database connection with timeout.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row  # Makes query results more readable
    return conn

# ============================
# Combo Types Management
# ============================

def add_combo_type(name, services, total_uses):
    """
    Adds a new combo type to the system.

    Args:
        name (str): Name of the combo type (e.g., "Eyebrow Threading Combo").
        services (str): Comma-separated list of services in the combo (e.g., "Eyebrow Threading, Facial").
        total_uses (int): Total number of uses allowed for this combo type.

    Returns:
        bool: True if the combo type was added successfully, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO combo_types (name, services, total_uses) VALUES (?, ?, ?)",
            (name, services, total_uses)
        )
        conn.commit()
        print(f"Combo type '{name}' added successfully!")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Combo type '{name}' already exists.")
        return False
    except Exception as e:
        print(f"Error adding combo type: {e}")
        return False
    finally:
        conn.close()

def get_combo_types():
    """
    Retrieves all combo types from the system.

    Returns:
        list of tuples: List of combo types (id, name, services, total_uses).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM combo_types")
        combo_types = cursor.fetchall()
        return combo_types
    except Exception as e:
        print(f"Error retrieving combo types: {e}")
        return []
    finally:
        conn.close()

def delete_combo_type(combo_type_id):
    """
    Deletes a combo type from the system.

    Args:
        combo_type_id (int): The ID of the combo type to delete.

    Returns:
        bool: True if the combo type was deleted successfully, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM combo_types WHERE id = ?", (combo_type_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Combo type ID {combo_type_id} deleted successfully!")
            return True
        else:
            print(f"Error: Combo type ID {combo_type_id} does not exist.")
            return False
    except Exception as e:
        print(f"Error deleting combo type: {e}")
        return False
    finally:
        conn.close()

# ============================
# Customer Combo Management
# ============================

def add_combo(customer_id, combo_type_id):
    """
    Assigns a combo to a customer with retries in case of database lock.
    """
    retries = 3  # Number of retries
    for attempt in range(retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            print("Opening connection in add_combo")
            cursor = conn.cursor()

            # Retrieve total uses from the combo_types table
            cursor.execute("SELECT total_uses FROM combo_types WHERE id = ?", (combo_type_id,))
            result = cursor.fetchone()
            if not result:
                print(f"Error: Combo type ID {combo_type_id} does not exist.")
                return False
            total_uses = result[0]

            # Add combo to the combos table
            cursor.execute(
                "INSERT INTO combos (customer_id, combo_type_id, remaining_uses) VALUES (?, ?, ?)",
                (customer_id, combo_type_id, total_uses)
            )
            conn.commit()
            print(f"Combo for customer ID {customer_id} added successfully!")
            return True
        except sqlite3.OperationalError as e:
            print(f"Database lock error in add_combo (attempt {attempt + 1}/{retries}): {e}")
            if attempt == retries - 1:  # On last attempt, re-raise the error
                raise
        finally:
            conn.close()
            print("Closing connection in add_combo")

def get_customer_combos(customer_id):
    """
    Retrieves all active combos for a specific customer (remaining uses > 0).

    Args:
        customer_id (int): The ID of the customer.

    Returns:
        list of tuples: List of active combos (id, customer_id, combo_type_id, remaining_uses).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT c.id, c.customer_id, c.combo_type_id, ct.name, c.remaining_uses, ct.total_uses
               FROM combos c
               JOIN combo_types ct ON c.combo_type_id = ct.id
               WHERE c.customer_id = ? AND c.remaining_uses > 0""",
            (customer_id,)
        )
        combos = cursor.fetchall()
        return combos
    except Exception as e:
        print(f"Error retrieving customer combos: {e}")
        return []
    finally:
        conn.close()

def update_combo_usage(combo_id):
    """
    Decreases the remaining uses of a combo by 1.

    Args:
        combo_id (int): The ID of the combo to update.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE combos SET remaining_uses = remaining_uses - 1 WHERE id = ? AND remaining_uses > 0",
            (combo_id,)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Combo ID {combo_id} usage updated successfully!")
            return True
        else:
            print(f"Error: Combo ID {combo_id} has no remaining uses or does not exist.")
            return False
    except Exception as e:
        print(f"Error updating combo usage: {e}")
        return False
    finally:
        conn.close()

def get_combo_status(combo_id):
    """
    Retrieves the status of a specific combo (remaining uses and total uses).

    Args:
        combo_id (int): The ID of the combo.

    Returns:
        tuple: Combo details (id, customer_id, combo_type_id, remaining_uses) if found, otherwise None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT c.id, c.customer_id, ct.name, c.remaining_uses, ct.total_uses
               FROM combos c
               JOIN combo_types ct ON c.combo_type_id = ct.id
               WHERE c.id = ?""",
            (combo_id,)
        )
        combo = cursor.fetchone()
        return combo
    except Exception as e:
        print(f"Error retrieving combo status: {e}")
        return None
    finally:
        conn.close()

# ============================
# Test Functions
# ============================

if __name__ == "__main__":
    # Test adding a combo type
    add_combo_type("Eyebrow Threading Combo", "Eyebrow Threading, Upper Lip", 5)

    # Test retrieving combo types
    print("Combo Types:")
    for combo_type in get_combo_types():
        print(combo_type)

    # Test adding a combo for a customer
    add_combo(customer_id=1, combo_type_id=1)

    # Test retrieving customer combos
    print("Customer Combos:")
    for combo in get_customer_combos(customer_id=1):
        print(combo)

    # Test updating combo usage
    update_combo_usage(combo_id=1)

    # Test getting combo status
    print("Combo Status:", get_combo_status(combo_id=1))
