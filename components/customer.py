import sqlite3
import csv
import os
from components.combo import add_combo, get_customer_combos, get_db_connection

# ============================
# Customer Management
# ============================

def add_customer(name, phone, email, combo_type_id):
    """Adds a new customer and assigns an initial combo to them."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Add customer to the database
        cursor.execute("INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
        customer_id = cursor.lastrowid  # Get the new customer ID

        print(f"Debug: Customer '{name}' added with ID {customer_id}")

        # Assign the initial combo
        if not add_combo(customer_id, combo_type_id, conn):
            raise Exception("Failed to add combo for the customer.")

        conn.commit()
        print(f"Customer '{name}' added successfully with combo type ID {combo_type_id}!")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Customer with phone number '{phone}' or email '{email}' already exists.")
        return False
    except Exception as e:
        print(f"Error adding customer: {e}")
        return False
    finally:
        conn.close()

def get_customer_by_phone(phone):
    """Retrieves a customer's information using their phone number only."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
        customer = cursor.fetchone()
        
        if not customer:
            print(f"Debug: No customer found for phone number '{phone}'")
            return None  # No customer found

        customer_id = customer["id"]
        customer_combos = get_customer_combos(customer_id)

        print(f"Debug: Retrieved Customer {customer_id}: {customer}")
        print(f"Debug: Customer {customer_id} Combos: {customer_combos}")

        return {
            "ID": customer_id,
            "Name": customer["name"],
            "Phone": customer["phone"],
            "Email": customer["email"],
            "Combos": customer_combos  # List of active combos
        }
    except Exception as e:
        print(f"Error retrieving customer: {e}")
        return None
    finally:
        conn.close()

def get_all_customers():
    """Retrieves all customers and their assigned combos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()

        print(f"Debug: Retrieved Customers from DB: {customers}")

        customer_list = []
        for customer in customers:
            customer_id = customer["id"]
            customer_combos = get_customer_combos(customer_id)

            customer_list.append({
                "ID": customer_id,
                "Name": customer["name"],
                "Phone": customer["phone"],
                "Email": customer["email"],
                "Combos": customer_combos
            })

        return customer_list
    except Exception as e:
        print(f"Error retrieving customers: {e}")
        return []
    finally:
        conn.close()

def edit_customer(customer_id, new_name, new_email):
    """Edits a customer's name and updates their Email Address, but keeps phone number fixed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure customer exists
        cursor.execute("SELECT name FROM customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            print(f"Error: Customer ID {customer_id} not found.")
            return False
        
        #check if email already exisits in the system
        cursor.execute("SELECT id FROM customers WHERE email = ? and id != ?", (new_email, customer_id))
        existing_customer = cursor.fetchone()

        if existing_customer:
            print(f"Error: Email '{new_email} is already in use by another customer")
            return "email_exists"

        # Perform the update (phone number is NOT updated)
        cursor.execute(
            """UPDATE customers 
               SET name = ?, email = ? 
               WHERE id = ?""",
            (new_name, new_email, customer_id)
        )

        conn.commit()
        print(f"Customer ID {customer_id} updated successfully!")
        return True

    except Exception as e:
        print(f"Error updating customer: {e}")
        return False
    finally:
        conn.close()

def delete_customer(customer_id):
    """Deletes a customer and all related records (appointments, combos)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure customer exists
        cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            print(f"Error: Customer ID {customer_id} does not exist.")
            return False

        # Delete all appointments associated with the customer
        cursor.execute("DELETE FROM appointments WHERE customer_id = ?", (customer_id,))
        print(f"Deleted all appointments for Customer ID {customer_id}.")

        # Delete all combos associated with the customer
        cursor.execute("DELETE FROM combos WHERE customer_id = ?", (customer_id,))
        print(f"Deleted all combos for Customer ID {customer_id}.")

        # Delete customer from the database
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
    """Checks if a customer has any remaining combos and deletes them if all combos are used up."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM combos WHERE customer_id = ? AND remaining_uses > 0",
            (customer_id,)
        )
        active_combos_count = cursor.fetchone()[0]
        if active_combos_count == 0:
            return delete_customer(customer_id)  # Now this checks for active combos before deletion
        return False
    except Exception as e:
        print(f"Error checking customer combos: {e}")
        return False
    finally:
        conn.close()


def add_combo_to_existing_customer(customer_id, combo_type_id):
    """Adds a new combo to an existing customer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure customer exists
        cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            print(f"Error: Customer ID {customer_id} does not exist.")
            return False

        # Add the new combo
        if not add_combo(customer_id, combo_type_id, conn):
            raise Exception("Failed to add the new combo.")

        conn.commit()
        print(f"New combo (ID {combo_type_id}) added for Customer ID {customer_id} successfully!")
        return True
    except Exception as e:
        print(f"Error adding combo: {e}")
        return False
    finally:
        conn.close()


def remove_combo_from_customer(customer_id, combo_id):
    """Removes a specific combo from a customer's profile."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure combo exists for the customer
        cursor.execute("SELECT id FROM combos WHERE id = ? AND customer_id = ?", (combo_id, customer_id))
        combo = cursor.fetchone()
        if not combo:
            print(f"Error: Combo ID {combo_id} not found for Customer ID {customer_id}.")
            return False

        # Delete the combo
        cursor.execute("DELETE FROM combos WHERE id = ?", (combo_id,))
        conn.commit()
        print(f"Combo ID {combo_id} removed from Customer ID {customer_id}.")
        return True
    except Exception as e:
        print(f"Error removing combo: {e}")
        return False
    finally:
        conn.close()


def export_customers_to_csv():
    """
    Exports all customer data into a CSV file and returns the file path.
    
    Returns:
        str: Path of the exported CSV file.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Retrieve all customers and their assigned combos
        cursor.execute("SELECT id, name, email, phone FROM customers")
        customers = cursor.fetchall()

        if not customers:
            print("No customers found for export.")
            return None

        csv_filename = "customers_data.csv"
        csv_filepath = os.path.join(os.getcwd(), csv_filename)

        with open(csv_filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Customer ID", "Customer Name", "Email", "Ph.no", "Combos for the customer", "Remaining uses"])

            for customer in customers:
                customer_id = customer["id"]
                name = customer["name"]
                email = customer["email"]
                phone = customer["phone"]

                # Fetch combos for the customer
                customer_combos = get_customer_combos(customer_id)
                if customer_combos:
                    combo_names = ", ".join([combo["name"] for combo in customer_combos])
                    remaining_uses = ", ".join([str(combo["remaining_uses"]) for combo in customer_combos])
                else:
                    combo_names = "No combos"
                    remaining_uses = "N/A"

                writer.writerow([customer_id, name, email, phone, combo_names, remaining_uses])

        print(f"Customer data exported successfully: {csv_filepath}")
        return csv_filepath

    except Exception as e:
        print(f"Error exporting customers to CSV: {e}")
        return None
    finally:
        conn.close()