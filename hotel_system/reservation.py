"""Reservation management module."""
import json
import os
from datetime import datetime

from hotel_system.hotel import Hotel
from hotel_system.customer import Customer


class Reservation:
    """Represents a hotel reservation."""

    DATA_FILE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data', 'reservations.json'
    )
    DATE_FMT = '%Y-%m-%d'

    def __init__(
        self, reservation_id, customer_id, hotel_id, check_in, check_out
    ):
        """Initialize Reservation instance."""
        self.reservation_id = str(reservation_id)
        self.customer_id = str(customer_id)
        self.hotel_id = str(hotel_id)
        self.check_in = str(check_in)
        self.check_out = str(check_out)
        self.status = 'active'

    def to_dict(self):
        """Serialize reservation to dictionary."""
        return {
            'reservation_id': self.reservation_id,
            'customer_id': self.customer_id,
            'hotel_id': self.hotel_id,
            'check_in': self.check_in,
            'check_out': self.check_out,
            'status': self.status,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize reservation from dictionary."""
        try:
            res = cls(
                reservation_id=data['reservation_id'],
                customer_id=data['customer_id'],
                hotel_id=data['hotel_id'],
                check_in=data['check_in'],
                check_out=data['check_out'],
            )
            res.status = data.get('status', 'active')
            return res
        except (KeyError, ValueError, TypeError) as exc:
            print(f"Error loading reservation record: {exc}")
            return None

    @classmethod
    def load_all(cls):
        """Load all reservations from JSON file."""
        if not os.path.exists(cls.DATA_FILE):
            return {}
        try:
            with open(cls.DATA_FILE, 'r', encoding='utf-8') as file_h:
                raw = json.load(file_h)
            result = {}
            for key, val in raw.items():
                obj = cls.from_dict(val)
                if obj is not None:
                    result[key] = obj
            return result
        except json.JSONDecodeError as exc:
            print(f"Error: Corrupt reservations file - {exc}")
            return {}
        except OSError as exc:
            print(f"Error: Cannot read reservations file - {exc}")
            return {}

    @classmethod
    def save_all(cls, reservations):
        """Save all reservations to JSON file."""
        directory = os.path.dirname(cls.DATA_FILE)
        os.makedirs(directory, exist_ok=True)
        try:
            with open(cls.DATA_FILE, 'w', encoding='utf-8') as file_h:
                json.dump(
                    {k: v.to_dict() for k, v in reservations.items()},
                    file_h,
                    indent=2,
                )
        except OSError as exc:
            print(f"Error: Cannot write reservations file - {exc}")

    @classmethod
    def validate_dates(cls, check_in, check_out):
        """Validate date strings and their order.

        Returns (datetime, datetime) tuple or (None, None) on error.
        """
        try:
            date_in = datetime.strptime(check_in, cls.DATE_FMT)
            date_out = datetime.strptime(check_out, cls.DATE_FMT)
        except ValueError as exc:
            print(f"Error: Invalid date format (use YYYY-MM-DD) - {exc}")
            return None, None
        if date_out <= date_in:
            print("Error: Check-out must be after check-in.")
            return None, None
        return date_in, date_out

    @classmethod
    def create(
        cls, reservation_id, customer_id, hotel_id, check_in, check_out
    ):
        """Create and persist a new reservation."""
        date_in, _ = cls.validate_dates(check_in, check_out)
        if date_in is None:
            return None

        reservations = cls.load_all()
        if reservation_id in reservations:
            print(f"Error: Reservation '{reservation_id}' already exists.")
            return None

        if Customer.get(customer_id) is None:
            print(f"Error: Customer '{customer_id}' not found.")
            return None

        if not Hotel.reserve_room(hotel_id, reservation_id):
            return None

        res = cls(
            reservation_id, customer_id, hotel_id, check_in, check_out
        )
        reservations[reservation_id] = res
        cls.save_all(reservations)
        print(f"Reservation '{reservation_id}' created.")
        return res

    @classmethod
    def cancel(cls, reservation_id):
        """Cancel an existing reservation."""
        reservations = cls.load_all()
        if reservation_id not in reservations:
            print(f"Error: Reservation '{reservation_id}' not found.")
            return False
        res = reservations[reservation_id]
        if res.status == 'cancelled':
            print(
                f"Error: Reservation '{reservation_id}' already cancelled."
            )
            return False
        Hotel.cancel_reservation(res.hotel_id, reservation_id)
        res.status = 'cancelled'
        cls.save_all(reservations)
        print(f"Reservation '{reservation_id}' cancelled.")
        return True

    @classmethod
    def get(cls, reservation_id):
        """Return a Reservation object or None."""
        return cls.load_all().get(reservation_id)

    @classmethod
    def display(cls, reservation_id):
        """Print reservation details to console."""
        res = cls.get(reservation_id)
        if res is None:
            print(f"Error: Reservation '{reservation_id}' not found.")
            return False
        print(f"Reservation ID: {res.reservation_id}")
        print(f"Customer ID   : {res.customer_id}")
        print(f"Hotel ID      : {res.hotel_id}")
        print(f"Check-in      : {res.check_in}")
        print(f"Check-out     : {res.check_out}")
        print(f"Status        : {res.status}")
        return True
