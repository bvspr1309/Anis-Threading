import sqlite3

# Path to the SQLite database file
DB_PATH = 'database/business.db'

def add_combo(customer_id, combo_name, total_uses):
    """
    Adds a new combo to the database for a specific customer.
    
    Args:
        customer_id (int): The ID of the customer purchasing the combo.
        combo_name (str): The name of the combo (e.g., "Eyebrow Threading Combo").
        total_uses (int): Total number of times the combo can be used.
    
    Returns:
        bool: True if the combo was added successfully, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO combos (customer_id, combo_name, total_uses, remaining_uses) VALUES (?, ?, ?, ?)",
            (customer_id, combo_name, total_uses, total_uses)
        )
        conn.commit()
        print(f"Combo '{combo_name}' added successfully for customer ID {customer_id}!")
        return True
    except Exception as e:
        print(f"Error adding combo: {e}")
        return False
    finally:
        conn.close()

def get_customer_combos(customer_id):
    """
    Retrieves all active combos for a specific customer (remaining uses > 0).
    
    Args:
        customer_id (int): The ID of the customer.
    
    Returns:
        list of tuples: List of active combos (id, customer_id, combo_name, total_uses, remaining_uses).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM combos WHERE customer_id = ? AND remaining_uses > 0",
            (customer_id,)
        )
        combos = cursor.fetchall()
        return combos
    except Exception as e:
        print(f"Error retrieving combos: {e}")
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
    conn = sqlite3.connect(DB_PATH)
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
        tuple: Combo details (id, customer_id, combo_name, total_uses, remaining_uses) if found, otherwise None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM combos WHERE id = ?", (combo_id,))
        combo = cursor.fetchone()
        return combo
    except Exception as e:
        print(f"Error retrieving combo status: {e}")
        return None
    finally:
        conn.close()

def delete_combo(combo_id):
    """
    Deletes a combo from the database.
    
    Args:
        combo_id (int): The ID of the combo to delete.
    
    Returns:
        bool: True if the combo was deleted successfully, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM combos WHERE id = ?", (combo_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Combo ID {combo_id} deleted successfully!")
            return True
        else:
            print(f"Error: Combo ID {combo_id} does not exist.")
            return False
    except Exception as e:
        print(f"Error deleting combo: {e}")
        return False
    finally:
        conn.close()

# Test the functions if this file is run directly
if __name__ == "__main__":
    # Test adding a combo
    add_combo(customer_id=1, combo_name="Eyebrow Threading Combo", total_uses=5)
    
    # Test retrieving combos for a customer
    combos = get_customer_combos(customer_id=1)
    print("Active Combos for Customer 1:")
    for combo in combos:
        print(combo)
    
    # Test updating combo usage
    if combos:
        combo_id = combos[0][0]  # Use the first combo
        update_combo_usage(combo_id)
    
    # Test retrieving combo status
    if combos:
        combo_status = get_combo_status(combo_id)
        print("Combo Status:", combo_status)
    
    # Test deleting a combo
    if combos:
        delete_combo(combo_id)
