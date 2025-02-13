import sqlite3
from components.combo import update_combo_usage, get_db_connection

# ============================
# Appointment Management
# ============================

def book_appointment(customer_id, service_id, date, combo_id=None):
    """
    Books an appointment for a customer and optionally links it to a combo.

    Args:
        customer_id (int): The ID of the customer booking the appointment.
        service_id (int): The ID of the service being booked.
        date (str): The date of the appointment in 'YYYY-MM-DD' format.
        combo_id (int, optional): The ID of the combo being used.

    Returns:
        bool: True if successfully booked, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert appointment into the database
        cursor.execute(
            "INSERT INTO appointments (customer_id, service_id, date, combo_id) VALUES (?, ?, ?, ?)",
            (customer_id, service_id, date, combo_id)
        )

        # If using a combo, decrement remaining uses
        if combo_id:
            update_combo_usage(combo_id)

        conn.commit()
        print(f"Appointment booked for Customer ID {customer_id} on {date} (Service ID {service_id}).")
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
        list: List of structured appointments.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT a.id, c.name, c.phone, s.name AS service, a.date, a.combo_id
               FROM appointments a
               JOIN customers c ON a.customer_id = c.id
               JOIN services s ON a.service_id = s.id
               WHERE a.customer_id = ? 
               ORDER BY a.date""",
            (customer_id,)
        )
        appointments = cursor.fetchall()
        return [
            {"ID": appt["id"], "Name": appt["name"], "Phone": appt["phone"],
             "Service": appt["service"], "Date": appt["date"], "Combo ID": appt["combo_id"]}
            for appt in appointments
        ]
    except Exception as e:
        print(f"Error retrieving appointments: {e}")
        return []
    finally:
        conn.close()

def get_appointment_by_date(date):
    """
    Retrieves all appointments on a specific date.

    Args:
        date (str): The date in 'YYYY-MM-DD' format.

    Returns:
        list: List of structured appointments.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT a.id, c.name, c.phone, s.name AS service, a.date, a.combo_id
               FROM appointments a
               JOIN customers c ON a.customer_id = c.id
               JOIN services s ON a.service_id = s.id
               WHERE a.date = ?
               ORDER BY a.date""",
            (date,)
        )
        appointments = cursor.fetchall()
        return [
            {"ID": appt["id"], "Name": appt["name"], "Phone": appt["phone"],
             "Service": appt["service"], "Date": appt["date"], "Combo ID": appt["combo_id"]}
            for appt in appointments
        ]
    except Exception as e:
        print(f"Error retrieving appointments by date: {e}")
        return []
    finally:
        conn.close()

def delete_appointment(appointment_id):
    """
    Deletes an appointment by its ID and restores combo usage if applicable.

    Args:
        appointment_id (int): The ID of the appointment to delete.

    Returns:
        bool: True if successfully deleted, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Retrieve combo_id before deleting the appointment
        cursor.execute("SELECT combo_id FROM appointments WHERE id = ?", (appointment_id,))
        result = cursor.fetchone()
        combo_id = result["combo_id"] if result else None

        # Delete the appointment
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()

        # Restore combo usage if an appointment was linked to a combo
        if combo_id:
            cursor.execute("UPDATE combos SET remaining_uses = remaining_uses + 1 WHERE id = ?", (combo_id,))
            conn.commit()

        print(f"Appointment ID {appointment_id} deleted successfully! Combo usage restored if applicable.")
        return True
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        return False
    finally:
        conn.close()

def edit_appointment(appointment_id, new_date, new_service_id):
    """
    Updates the date and service of an appointment.

    Args:
        appointment_id (int): The ID of the appointment to update.
        new_date (str): The new date for the appointment in 'YYYY-MM-DD' format.
        new_service_id (int): The new service ID for the appointment.

    Returns:
        bool: True if successfully updated, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Update the appointment
        cursor.execute(
            "UPDATE appointments SET date = ?, service_id = ? WHERE id = ?",
            (new_date, new_service_id, appointment_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Appointment ID {appointment_id} updated to new date {new_date} and service ID {new_service_id}.")
            return True
        else:
            print(f"No appointment found with ID {appointment_id}.")
            return False
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return False
    finally:
        conn.close()
