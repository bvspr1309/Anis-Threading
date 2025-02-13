import streamlit as st
from components.customer import (
    add_customer, get_customer_by_phone, get_all_customers, remove_customer_if_combos_used_up,
    edit_customer, delete_customer
)
from components.combo import (
    add_combo_type, get_combo_types, delete_combo_type, get_customer_combos, add_combo, get_services_for_combo
)
from components.appointment import (
    book_appointment, get_customer_appointments, get_appointment_by_date, delete_appointment, edit_appointment
)

# Set the title of the app
st.title("Ani's Threading and Skincare Management System")

# Sidebar menu
menu = ["Home", "Customer Management", "Combo Management", "Appointment Management", "View Appointments"]
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
        if selected_combo_id and add_customer(name, phone, selected_combo_id):
            st.success(f"Customer '{name}' added successfully with combo '{selected_combo}'!")
        else:
            st.error("Failed to add the customer. Please ensure the information is correct.")

    # Search for a customer by phone
    st.write("### Search Customer by Phone")
    search_query = st.text_input("Enter Customer Phone Number")
    if st.button("Search"):
        customer = get_customer_by_phone(search_query)
        if customer:
            st.write("### Customer Details")
            st.write(f"**ID:** {customer['ID']}")
            st.write(f"**Name:** {customer['Name']}")
            st.write(f"**Phone:** {customer['Phone']}")
            st.write(f"**Combos:** {customer['Combos']}")

            # Edit Customer Button
            with st.expander("Edit Customer"):
                new_name = st.text_input("New Name", customer['Name'])
                new_phone = st.text_input("New Phone", customer['Phone'])
                if st.button("Update Customer Details"):
                    if edit_customer(customer['ID'], new_name, new_phone):
                        st.success(f"Customer {customer['Name']} updated successfully!")
                    else:
                        st.error("Failed to update customer.")

            # Delete Customer Button with Confirmation
            if st.button("Delete Customer"):
                confirm_delete = st.checkbox("Confirm deletion")
                if confirm_delete:
                    if delete_customer(customer['ID']):
                        st.success(f"Customer {customer['Name']} deleted successfully!")
                    else:
                        st.error("Failed to delete customer. Ensure they have no active combos.")
                else:
                    st.warning("Please confirm deletion before proceeding.")
        else:
            st.error("Customer not found.")

    # Show all customers on button click
    if st.button("Show All Customers"):
        st.write("### All Customers")
        customers = get_all_customers()
        if customers:
            for customer in customers:
                st.write(f"**ID:** {customer['ID']}")
                st.write(f"**Name:** {customer['Name']}")
                st.write(f"**Phone:** {customer['Phone']}")
                st.write(f"**Combos:** {customer['Combos']}")
                st.write("---")
        else:
            st.write("No customers found.")

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
                else:
                    st.error(f"Failed to delete combo '{combo['name']}'.")

# ============================
# Appointment Management
# ============================
elif choice == "Appointment Management":
    st.subheader("Appointment Management")

    st.write("### Book an Appointment")
    phone = st.text_input("Customer Phone Number (for appointment)")
    date = st.date_input("Appointment Date")

    all_services = get_services_for_combo(None)
    service_options = {service['name']: service['id'] for service in all_services}
    selected_service = st.selectbox("Select a Service", list(service_options.keys()))
    selected_service_id = service_options[selected_service]

    if st.button("Book Appointment"):
        customer = get_customer_by_phone(phone)
        if customer:
            if book_appointment(customer["ID"], selected_service_id, str(date)):
                st.success(f"Appointment booked for {customer['Name']} on {date} with service {selected_service}!")
            else:
                st.error("Failed to book appointment.")
        else:
            st.error("Customer not found. Please add the customer first.")

# ============================
# View Appointments
# ============================
elif choice == "View Appointments":
    st.subheader("View Appointments")

    date_to_check = st.date_input("Select a Date")
    if st.button("View Appointments by Date"):
        appointments = get_appointment_by_date(str(date_to_check))
        if appointments:
            for appointment in appointments:
                st.write(f"**Appointment ID:** {appointment['ID']}")
                st.write(f"**Customer:** {appointment['Name']} ({appointment['Phone']})")
                st.write(f"**Service:** {appointment['Service']}")
                st.write(f"**Date:** {appointment['Date']}")
                st.write("---")
        else:
            st.write("No appointments found on this date.")
