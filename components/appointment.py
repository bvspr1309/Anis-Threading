import sqlite3

# Path to the SQLite database file
DB_PATH = 'database/business.db'

# ============================
# Appointment Management
# ============================

def book_appointment(customer_id, service, date, start_time, end_time, combo_id=None):
    """
    Books an appointment for a customer and optionally links it to a combo.

    Args:
        customer_id (int): The ID of the customer booking the appointment.
        service (str): The service being booked (e.g., "Eyebrow Threading").
        date (str): The date of the appointment in 'YYYY-MM-DD' format.
        start_time (str): The start time of the appointment in 'HH:MM' format.
        end_time (str): The end time of the appointment in 'HH:MM' format.
        combo_id (int): The ID of the combo being used (if applicable).

    Returns:
        bool: True if the appointment was booked successfully, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Check for overlapping appointments
        cursor.execute(
            """SELECT * FROM appointments
               WHERE date = ? AND (
                   (start_time < ? AND end_time > ?) OR
                   (start_time < ? AND end_time > ?)
               )""",
            (date, end_time, end_time, start_time, start_time)
        )
        overlapping_appointments = cursor.fetchall()
        if overlapping_appointments:
            print(f"Error: Overlapping appointments found for the time range {start_time} - {end_time}.")
            return False

        # Insert the appointment
        cursor.execute(
            "INSERT INTO appointments (customer_id, service, date, start_time, end_time, combo_id) VALUES (?, ?, ?, ?, ?, ?)",
            (customer_id, service, date, start_time, end_time, combo_id)
        )
        conn.commit()
        print(f"Appointment booked for Customer ID {customer_id} on {date} from {start_time} to {end_time}.")
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
        list of tuples: List of appointments (id, customer_id, service, date, start_time, end_time, combo_id).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM appointments WHERE customer_id = ? ORDER BY date, start_time",
            (customer_id,)
        )
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        print(f"Error retrieving appointments: {e}")
        return []
    finally:
        conn.close()

def get_appointment_by_date(date):
    """
    Retrieves all appointments on a specific date.

    Args:
        date (str): The date to search for appointments (in 'YYYY-MM-DD' format).

    Returns:
        list of tuples: List of appointments (id, customer_id, service, date, start_time, end_time, combo_id).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM appointments WHERE date = ? ORDER BY start_time",
            (date,)
        )
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        print(f"Error retrieving appointments by date: {e}")
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

def update_appointment_date_and_time(appointment_id, new_date, new_start_time, new_end_time):
    """
    Updates the date and time of an appointment.

    Args:
        appointment_id (int): The ID of the appointment to update.
        new_date (str): The new date for the appointment (in 'YYYY-MM-DD' format).
        new_start_time (str): The new start time for the appointment (in 'HH:MM' format).
        new_end_time (str): The new end time for the appointment (in 'HH:MM' format).

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Check for overlapping appointments
        cursor.execute(
            """SELECT * FROM appointments
               WHERE date = ? AND id != ? AND (
                   (start_time < ? AND end_time > ?) OR
                   (start_time < ? AND end_time > ?)
               )""",
            (new_date, appointment_id, new_end_time, new_end_time, new_start_time, new_start_time)
        )
        overlapping_appointments = cursor.fetchall()
        if overlapping_appointments:
            print(f"Error: Overlapping appointments found for the new time range {new_start_time} - {new_end_time}.")
            return False

        # Update the appointment
        cursor.execute(
            "UPDATE appointments SET date = ?, start_time = ?, end_time = ? WHERE id = ?",
            (new_date, new_start_time, new_end_time, appointment_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Appointment ID {appointment_id} updated to new date {new_date} and time {new_start_time} - {new_end_time}.")
            return True
        else:
            print(f"No appointment found with ID {appointment_id}.")
            return False
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return False
    finally:
        conn.close()

# ============================
# Test Functions
# ============================

if __name__ == "__main__":
    # Test booking an appointment
    book_appointment(customer_id=1, service="Eyebrow Threading", date="2025-01-25", start_time="10:00", end_time="10:30", combo_id=1)

    # Test retrieving appointments for a customer
    print("Appointments for Customer ID 1:")
    appointments = get_customer_appointments(customer_id=1)
    for appointment in appointments:
        print(appointment)

    # Test retrieving appointments by date
    print("Appointments on 2025-01-25:")
    print(get_appointment_by_date("2025-01-25"))

    # Test updating an appointment
    if appointments:
        appointment_id = appointments[0][0]  # Get the first appointment's ID
        update_appointment_date_and_time(appointment_id, "2025-01-26", "11:00", "11:30")

    # Test deleting an appointment
    if appointments:
        appointment_id = appointments[0][0]
        delete_appointment(appointment_id)
