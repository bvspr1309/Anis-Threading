import datetime
import streamlit as st
import pandas as pd
from components.customer import (
    add_customer, get_customer_by_phone, get_all_customers, remove_customer_if_combos_used_up,
    edit_customer, delete_customer, add_combo_to_existing_customer, remove_combo_from_customer, export_customers_to_csv
)
from components.combo import (
    add_combo_type, get_combo_types, delete_combo_type, get_customer_combos, add_combo, get_services_for_combo
)
from components.appointment import (
    book_appointment, get_customer_appointments, get_appointment_by_date, delete_appointment, edit_appointment
)
from components.notifications import (
    send_appointment_confirmation, send_appointment_cancellation
)

# Set the title of the app
st.title("Ani's Threading and Skincare Management System")

# Sidebar menu
menu = ["Home", "Customer Management", "Customer N Combo", "Appointment Management", "View Appointments", "Download Data", "Combo Management"]
choice = st.sidebar.selectbox("Menu", menu)

# ============================
# Home Page
# ============================
if choice == "Home":
    st.subheader("Welcome to Ani's Threading and Skincare Management System!")
    st.write("""
        This system allows you to:
        - Manage customers and assign combos.
        - Handle combo packages for discounted services.
        - Schedule and manage appointments.
        - Track combo usage and appointment history.
    """)

# ============================
# Customer Management
# ============================
elif choice == "Customer Management":
    st.subheader("Customer Management")

    # Add a new customer with a combo
    st.write("### Add a New Customer with Combo")
    name = st.text_input("Customer Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email Address")

    # Dropdown to select a combo type
    combo_types = get_combo_types()
    if combo_types:
        combo_type_options = {f"{combo['name']} (Uses: {combo['total_uses']})": combo['id'] for combo in combo_types}
        selected_combo = st.selectbox("Select a Combo", options=list(combo_type_options.keys()))
        selected_combo_id = combo_type_options[selected_combo]
    else:
        st.warning("No combo types available. Please add combos in the Combo Management tab.")
        selected_combo_id = None

    if st.button("Add Customer with Combo"):
        if selected_combo_id and add_customer(name, phone, email, selected_combo_id):
            st.success(f"Customer '{name}' added successfully with combo '{selected_combo}'!")
            st.session_state["search_query"] = phone  # Auto-store newly added customer for quick lookup
            st.rerun()
        else:
            st.error("Failed to add the customer. Please ensure the information is correct.")

    # Search for a customer by phone
    st.write("### Search Customer by Phone")

    # Ensure search query persists in session state
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""

    search_query = st.text_input("Enter Customer Phone Number", st.session_state["search_query"])

    if st.button("Search"):
        customer = get_customer_by_phone(search_query)
        if customer:
            st.session_state["search_query"] = search_query  # Persist search query
            st.session_state["customer_data"] = customer  # Store customer data
            st.session_state["editing"] = False  # Ensure editing state resets
        else:
            st.error("Customer not found.")

    # Display customer details if found
    if "customer_data" in st.session_state and st.session_state["customer_data"]:
        customer = st.session_state["customer_data"]

        st.write("### Customer Details")
        st.write(f"**ID:** {customer['ID']}")
        st.write(f"**Name:** {customer['Name']}")
        st.write(f"**Phone:** {customer['Phone']} (Phone Number is not editable)")
        st.write(f"**Email:** {customer['Email']}")
        st.write(f"**Combos:** {customer['Combos']}")

        # Edit Customer Button
        with st.expander("Edit Customer"):
            new_name = st.text_input("New Name", customer['Name'])
            new_email = st.text_input("New Email", customer['Email'])

            if st.button("Update Customer Details"):
                result = edit_customer(customer['ID'], new_name, new_email)

                if result == 'email_exists':
                    st.error(f"Failed to update customer. Email '{new_email}' is already in use by another customer.")
                elif result:
                    st.success(f"Customer {customer['Name']} updated successfully!")
                    st.session_state["customer_data"]["Name"] = new_name  # Update session data
                    st.session_state["customer_data"]["Email"] = new_email
                    st.rerun()
                else:
                    st.error("Failed to update customer.")

        # Delete Customer Button (No Confirmation, Immediate Deletion)
        if st.button("Delete Customer"):
            delete_status = delete_customer(customer['ID'])  # Try deleting the customer
            if delete_status:
                st.success(f"Customer {customer['Name']} deleted successfully!")
                
                # Ensure UI refreshes correctly
                st.session_state.pop("customer_data", None)
                st.session_state.pop("search_query", None)
                st.rerun()
            else:
                st.error("Failed to delete customer. Customer might not exist.")


# ============================
# Customer N Combo Management
# ============================
elif choice == "Customer N Combo":
    st.subheader("Customer & Combo Management")

    # Search for customer by phone
    st.write("### Search for a Customer")
    phone = st.text_input("Enter Customer Phone Number")

    if st.button("Search Customer"):
        customer = get_customer_by_phone(phone)
        if customer:
            st.session_state["customer_data"] = customer
        else:
            st.error("Customer not found.")

    # Display and manage customer combos
    if "customer_data" in st.session_state and st.session_state["customer_data"]:
        customer = st.session_state["customer_data"]
        st.write(f"**Customer Name:** {customer['Name']}")
        st.write(f"**Phone:** {customer['Phone']}")
        st.write(f"**Email:** {customer['Email']}")

        # Display customer's current combos
        st.write("### Combos for the Customer:")
        if customer["Combos"]:
            for combo in customer["Combos"]:
                st.write(f"- {combo['name']} ({combo['remaining_uses']})")
            
            # Remove a combo
            combo_options = {f"{combo['name']}": combo["id"] for combo in customer["Combos"]}
            selected_combo_to_remove = st.selectbox("Select a Combo to Remove", options=list(combo_options.keys()))

            if st.button("Remove Selected Combo"):
                if remove_combo_from_customer(customer["ID"], combo_options[selected_combo_to_remove]):
                    st.success(f"Combo '{selected_combo_to_remove}' removed successfully.")
                    st.rerun()
                else:
                    st.error("Failed to remove combo.")

        else:
            st.write("No active combos.")

        # Add a new combo
        st.write("### Add a New Combo for This Customer")
        available_combos = get_combo_types()
        combo_selection = {f"{combo['name']} (Uses: {combo['total_uses']})": combo['id'] for combo in available_combos}
        new_combo_selected = st.selectbox("Select a New Combo", options=list(combo_selection.keys()))

        if st.button("Add Selected Combo"):
            if add_combo_to_existing_customer(customer["ID"], combo_selection[new_combo_selected]):
                st.success(f"New combo '{new_combo_selected}' added successfully!")
                st.rerun()
            else:
                st.error("Failed to add combo.")

# ============================
# Appointment Management
# ============================
elif choice == "Appointment Management":
    st.subheader("Appointment Management")

    st.write("### Book an Appointment")
    phone = st.text_input("Customer Phone Number (for appointment)")
    date = st.date_input("Appointment Date")

    customer = get_customer_by_phone(phone) if phone else None

    if customer:
        all_services = get_services_for_combo(None)
        service_options = {service['name']: service['id'] for service in all_services}
        selected_service = st.selectbox("Select a Service", list(service_options.keys()))
        selected_service_id = service_options[selected_service]

        use_combo = st.checkbox("Use Available Combo")
        selected_combo_id = None

        if use_combo:
            available_combos = get_customer_combos(customer["ID"])
            if available_combos:
                combo_options = {f"{combo['name']} (Remaining: {combo['remaining_uses']})": combo['id'] for combo in available_combos}
                selected_combo = st.selectbox("Select a Combo", options=list(combo_options.keys()))
                selected_combo_id = combo_options[selected_combo]
            else:
                st.warning("No available combos for this customer.")

        if st.button("Book Appointment"):
            if book_appointment(customer["ID"], selected_service_id, str(date), use_combo=True, combo_id=selected_combo_id):
                st.success(f"Appointment booked for {customer['Name']} on {date} with service {selected_service}!")
                
                # Send email confirmation if customer has an email
                if customer["Email"]:
                    send_appointment_confirmation(
                        customer["ID"], # Pass customer ID
                        customer["Name"],
                        customer["Email"],
                        selected_service,
                        date,
                        selected_combo_id #pass the booked combo ID
                    )
                
                st.rerun()
            else:
                st.error("Failed to book appointment.")

# ============================
# View Appointments
# ============================
elif choice == "View Appointments":
    st.subheader("View Appointments")

    # Ensure selected date exists and is valid
    if "selected_date" not in st.session_state or not isinstance(st.session_state["selected_date"], datetime.date):
        st.session_state["selected_date"] = datetime.date.today()  # Default to today

    # Properly set date_to_check
    date_to_check = st.date_input("Select a Date", value=st.session_state["selected_date"])

    if st.button("View Appointments by Date"):
        st.session_state["selected_date"] = date_to_check  # Store selected date
        appointments = get_appointment_by_date(str(st.session_state["selected_date"]))
        st.session_state["appointments"] = appointments  # Store appointments in session
        st.rerun()  # Refresh UI

    # Display appointments
    if "appointments" in st.session_state and st.session_state["appointments"]:
        for appointment in st.session_state["appointments"]:
            st.write(f"**Appointment ID:** {appointment['ID']}")
            st.write(f"**Customer:** {appointment['Name']} ({appointment['Phone']})")
            st.write(f"**Service:** {appointment['Service']}")
            st.write(f"**Date:** {appointment['Date']}")

            # Delete appointment button
            if st.button(f"Delete Appointment {appointment['ID']}", key=f"delete_appointment_{appointment['ID']}"):
                if delete_appointment(appointment['ID']):
                    st.success(f"Appointment ID {appointment['ID']} deleted successfully!")

                    # Remove deleted appointment from session manually
                    st.session_state["appointments"] = [
                        appt for appt in st.session_state["appointments"] if appt["ID"] != appointment["ID"]
                    ]
                    st.rerun()
                else:
                    st.error(f"Failed to Delete the appointment ID {appointment["ID"]}")
            st.write("---") #seperator
    else:
        st.write("No appointments found on this date")


# ============================
# Download Data Tab
# ============================
if choice == "Download Data":
    st.subheader("Download Customer Data")
    st.write("Click the button below to download all customer data as a CSV file.")

    if st.button("Download All Customers Data"):
        csv_filepath = export_customers_to_csv()
        if csv_filepath:
            with open(csv_filepath, "rb") as file:
                st.download_button(
                    label="Download CSV",
                    data=file,
                    file_name="customers_data.csv",
                    mime="text/csv"
                )
            st.success("Customer data is ready for download!")
        else:
            st.error("No customer data available.")


# ============================
# Combo Management
# ============================
elif choice == "Combo Management":
    st.subheader("Combo Management")

    # Add a new combo type
    st.write("### Add a New Combo Type")
    combo_name = st.text_input("Combo Name")
    total_uses = st.number_input("Total Uses", min_value=1, step=1)

    all_services = get_services_for_combo(None)
    service_options = {service['name']: service['id'] for service in all_services}
    selected_services = st.multiselect("Select Services for Combo", list(service_options.keys()))

    if st.button("Add Combo Type"):
        selected_service_ids = [service_options[service] for service in selected_services]
        if add_combo_type(combo_name, selected_service_ids, total_uses):
            st.success(f"Combo type '{combo_name}' added successfully with services {selected_services}!")
            st.rerun()
        else:
            st.error("Failed to add the combo type. It may already exist.")

    # View, edit, and delete combo types
    st.write("### Existing Combo Types")
    combo_types = get_combo_types()
    if combo_types:
        for combo in combo_types:
            st.write(f"**ID:** {combo['id']}, **Name:** {combo['name']}, **Total Uses:** {combo['total_uses']}")
            if st.button(f"Delete Combo '{combo['name']}'", key=f"delete_combo_{combo['id']}"):
                if delete_combo_type(combo['id']):
                    st.success(f"Combo '{combo['name']}' deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to delete combo '{combo['name']}'.")