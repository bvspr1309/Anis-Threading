import sqlite3

# Path to the SQLite database file
DB_PATH = 'database/business.db'

def book_appointment(customer_id, service, date, combo_id=None):
    """
    Books an appointment for a customer and optionally links it to a combo.

    Args:
        customer_id (int): The ID of the customer booking the appointment.
        service (str): The service being booked (e.g., "Eyebrow Threading").
        date (str): The date of the appointment in 'YYYY-MM-DD' format.
        combo_id (int): The ID of the combo being used (if applicable).

    Returns:
        bool: True if the appointment was booked successfully, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO appointments (customer_id, service, date, combo_id) VALUES (?, ?, ?, ?)",
            (customer_id, service, date, combo_id)
        )
        conn.commit()
        print(f"Appointment booked for Customer ID {customer_id} on {date} for service '{service}'.")
        return True
    except Exception as e:
        print(f"Error booking appointment: {e}")
        return False
    finally:
        conn.close()

def get_customer_appointments(customer_id):
    """
    Retrieves all appointments for a specific customer.

    Args:
        customer_id (int): The ID of the customer.

    Returns:
        list of tuples: List of appointments (id, customer_id, service, date, combo_id).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM appointments WHERE customer_id = ? ORDER BY date",
            (customer_id,)
        )
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        print(f"Error retrieving appointments: {e}")
        return []
    finally:
        conn.close()

def delete_appointment(appointment_id):
    """
    Deletes an appointment by its ID.

    Args:
        appointment_id (int): The ID of the appointment to delete.

    Returns:
        bool: True if the appointment was deleted successfully, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Appointment ID {appointment_id} deleted successfully!")
            return True
        else:
            print(f"No appointment found with ID {appointment_id}.")
            return False
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        return False
    finally:
        conn.close()

def get_appointment_by_date(date):
    """
    Retrieves all appointments on a specific date.

    Args:
        date (str): The date to search for appointments (in 'YYYY-MM-DD' format).

    Returns:
        list of tuples: List of appointments (id, customer_id, service, date, combo_id).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM appointments WHERE date = ? ORDER BY customer_id",
            (date,)
        )
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        print(f"Error retrieving appointments by date: {e}")
        return []
    finally:
        conn.close()

def update_appointment_date(appointment_id, new_date):
    """
    Updates the date of an appointment.

    Args:
        appointment_id (int): The ID of the appointment to update.
        new_date (str): The new date for the appointment (in 'YYYY-MM-DD' format).

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE appointments SET date = ? WHERE id = ?",
            (new_date, appointment_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Appointment ID {appointment_id} updated to new date {new_date}.")
            return True
        else:
            print(f"No appointment found with ID {appointment_id}.")
            return False
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return False
    finally:
        conn.close()

# Test the functions if this file is run directly
if __name__ == "__main__":
    # Test booking an appointment
    book_appointment(customer_id=1, service="Eyebrow Threading", date="2025-01-25", combo_id=1)

    # Test retrieving appointments for a customer
    print("Appointments for Customer ID 1:")
    appointments = get_customer_appointments(customer_id=1)
    for appointment in appointments:
        print(appointment)

    # Test updating an appointment's date
    if appointments:
        appointment_id = appointments[0][0]  # Get the first appointment's ID
        update_appointment_date(appointment_id, "2025-01-30")

    # Test retrieving appointments by date
    print("Appointments on 2025-01-30:")
    print(get_appointment_by_date("2025-01-30"))

    # Test deleting an appointment
    if appointments:
        appointment_id = appointments[0][0]
        delete_appointment(appointment_id)
