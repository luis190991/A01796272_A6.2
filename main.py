"""Hotel Reservation System - interactive command-line interface."""
from hotel_system.hotel import Hotel
from hotel_system.customer import Customer
from hotel_system.reservation import Reservation


# ---------------------------------------------------------------------------
# Hotel helpers
# ---------------------------------------------------------------------------

def _input_hotel_create():
    """Prompt user for hotel data and call Hotel.create."""
    hotel_id = input("Hotel ID: ").strip()
    name = input("Name: ").strip()
    location = input("Location: ").strip()
    try:
        rating = float(input("Rating (0.0-5.0): ").strip())
        total_rooms = int(input("Total Rooms: ").strip())
    except ValueError:
        print("Error: Rating must be decimal; Total Rooms must be integer.")
        return
    Hotel.create(hotel_id, name, location, rating, total_rooms)


def _input_hotel_modify():
    """Prompt user for hotel modification data and call Hotel.modify."""
    hotel_id = input("Hotel ID: ").strip()
    field = input("Field (name/location/rating/total_rooms): ").strip()
    value = input("New value: ").strip()
    if field == 'rating':
        try:
            value = float(value)
        except ValueError:
            print("Error: Rating must be a decimal number.")
            return
    elif field == 'total_rooms':
        try:
            value = int(value)
        except ValueError:
            print("Error: Total rooms must be an integer.")
            return
    Hotel.modify(hotel_id, **{field: value})


def hotel_menu():
    """Display and handle the Hotel management sub-menu."""
    while True:
        print("\n--- Hotel Management ---")
        print("1. Create Hotel")
        print("2. Delete Hotel")
        print("3. Display Hotel Information")
        print("4. Modify Hotel Information")
        print("5. Reserve a Room")
        print("6. Cancel a Room Reservation")
        print("0. Back")
        choice = input("Select: ").strip()

        if choice == '1':
            _input_hotel_create()
        elif choice == '2':
            Hotel.delete(input("Hotel ID: ").strip())
        elif choice == '3':
            Hotel.display(input("Hotel ID: ").strip())
        elif choice == '4':
            _input_hotel_modify()
        elif choice == '5':
            hotel_id = input("Hotel ID: ").strip()
            res_id = input("Reservation ID: ").strip()
            Hotel.reserve_room(hotel_id, res_id)
        elif choice == '6':
            hotel_id = input("Hotel ID: ").strip()
            res_id = input("Reservation ID: ").strip()
            Hotel.cancel_reservation(hotel_id, res_id)
        elif choice == '0':
            break
        else:
            print("Invalid option. Please try again.")


# ---------------------------------------------------------------------------
# Customer helpers
# ---------------------------------------------------------------------------

def _input_customer_modify():
    """Prompt user for customer modification data and call Customer.modify."""
    customer_id = input("Customer ID: ").strip()
    field = input("Field (name/email/phone): ").strip()
    value = input("New value: ").strip()
    Customer.modify(customer_id, **{field: value})


def customer_menu():
    """Display and handle the Customer management sub-menu."""
    while True:
        print("\n--- Customer Management ---")
        print("1. Create Customer")
        print("2. Delete Customer")
        print("3. Display Customer Information")
        print("4. Modify Customer Information")
        print("0. Back")
        choice = input("Select: ").strip()

        if choice == '1':
            customer_id = input("Customer ID: ").strip()
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            Customer.create(customer_id, name, email, phone)
        elif choice == '2':
            Customer.delete(input("Customer ID: ").strip())
        elif choice == '3':
            Customer.display(input("Customer ID: ").strip())
        elif choice == '4':
            _input_customer_modify()
        elif choice == '0':
            break
        else:
            print("Invalid option. Please try again.")


# ---------------------------------------------------------------------------
# Reservation helpers
# ---------------------------------------------------------------------------

def reservation_menu():
    """Display and handle the Reservation management sub-menu."""
    while True:
        print("\n--- Reservation Management ---")
        print("1. Create Reservation")
        print("2. Cancel Reservation")
        print("3. Display Reservation Information")
        print("0. Back")
        choice = input("Select: ").strip()

        if choice == '1':
            res_id = input("Reservation ID: ").strip()
            customer_id = input("Customer ID: ").strip()
            hotel_id = input("Hotel ID: ").strip()
            check_in = input("Check-in date (YYYY-MM-DD): ").strip()
            check_out = input("Check-out date (YYYY-MM-DD): ").strip()
            Reservation.create(
                res_id, customer_id, hotel_id, check_in, check_out
            )
        elif choice == '2':
            Reservation.cancel(input("Reservation ID: ").strip())
        elif choice == '3':
            Reservation.display(input("Reservation ID: ").strip())
        elif choice == '0':
            break
        else:
            print("Invalid option. Please try again.")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    """Run the Hotel Reservation System interactive menu."""
    print("=" * 42)
    print("    Hotel Reservation System")
    print("=" * 42)
    while True:
        print("\n=== Main Menu ===")
        print("1. Hotels")
        print("2. Customers")
        print("3. Reservations")
        print("0. Exit")
        choice = input("Select: ").strip()

        if choice == '1':
            hotel_menu()
        elif choice == '2':
            customer_menu()
        elif choice == '3':
            reservation_menu()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == '__main__':
    main()
