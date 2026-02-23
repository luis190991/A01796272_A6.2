"""Hotel management module."""
import json
import os


class Hotel:
    """Represents a hotel with management capabilities."""

    DATA_FILE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data', 'hotels.json'
    )

    def __init__(self, hotel_id, name, location, rating, total_rooms):
        """Initialize Hotel instance."""
        self.hotel_id = str(hotel_id)
        self.name = str(name)
        self.location = str(location)
        self.rating = float(rating)
        self.total_rooms = int(total_rooms)
        self.available_rooms = int(total_rooms)
        self.reservations = []

    def to_dict(self):
        """Serialize hotel to dictionary."""
        return {
            'hotel_id': self.hotel_id,
            'name': self.name,
            'location': self.location,
            'rating': self.rating,
            'total_rooms': self.total_rooms,
            'available_rooms': self.available_rooms,
            'reservations': self.reservations,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize hotel from dictionary."""
        try:
            hotel = cls(
                hotel_id=data['hotel_id'],
                name=data['name'],
                location=data['location'],
                rating=data['rating'],
                total_rooms=data['total_rooms'],
            )
            hotel.available_rooms = int(
                data.get('available_rooms', hotel.total_rooms)
            )
            hotel.reservations = list(data.get('reservations', []))
            return hotel
        except (KeyError, ValueError, TypeError) as exc:
            print(f"Error loading hotel record: {exc}")
            return None

    @classmethod
    def load_all(cls):
        """Load all hotels from JSON file."""
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
            print(f"Error: Corrupt hotels file - {exc}")
            return {}
        except OSError as exc:
            print(f"Error: Cannot read hotels file - {exc}")
            return {}

    @classmethod
    def save_all(cls, hotels):
        """Save all hotels to JSON file."""
        directory = os.path.dirname(cls.DATA_FILE)
        os.makedirs(directory, exist_ok=True)
        try:
            with open(cls.DATA_FILE, 'w', encoding='utf-8') as file_h:
                json.dump(
                    {k: v.to_dict() for k, v in hotels.items()},
                    file_h,
                    indent=2,
                )
        except OSError as exc:
            print(f"Error: Cannot write hotels file - {exc}")

    @classmethod
    def create(cls, hotel_id, name, location, rating, total_rooms):
        """Create and persist a new hotel."""
        hotels = cls.load_all()
        if hotel_id in hotels:
            print(f"Error: Hotel '{hotel_id}' already exists.")
            return None
        try:
            hotel = cls(hotel_id, name, location, rating, total_rooms)
        except (ValueError, TypeError) as exc:
            print(f"Error: Invalid hotel data - {exc}")
            return None
        hotels[hotel_id] = hotel
        cls.save_all(hotels)
        print(f"Hotel '{name}' created (ID: {hotel_id}).")
        return hotel

    @classmethod
    def delete(cls, hotel_id):
        """Delete a hotel by ID."""
        hotels = cls.load_all()
        if hotel_id not in hotels:
            print(f"Error: Hotel '{hotel_id}' not found.")
            return False
        name = hotels[hotel_id].name
        del hotels[hotel_id]
        cls.save_all(hotels)
        print(f"Hotel '{name}' deleted.")
        return True

    @classmethod
    def get(cls, hotel_id):
        """Return a Hotel object or None."""
        return cls.load_all().get(hotel_id)

    @classmethod
    def display(cls, hotel_id):
        """Print hotel details to console."""
        hotel = cls.get(hotel_id)
        if hotel is None:
            print(f"Error: Hotel '{hotel_id}' not found.")
            return False
        print(f"Hotel ID   : {hotel.hotel_id}")
        print(f"Name       : {hotel.name}")
        print(f"Location   : {hotel.location}")
        print(f"Rating     : {hotel.rating}")
        print(f"Total Rooms: {hotel.total_rooms}")
        print(f"Available  : {hotel.available_rooms}")
        return True

    @classmethod
    def modify(cls, hotel_id, **kwargs):
        """Update hotel attributes."""
        hotels = cls.load_all()
        if hotel_id not in hotels:
            print(f"Error: Hotel '{hotel_id}' not found.")
            return False
        hotel = hotels[hotel_id]
        allowed = {'name', 'location', 'rating', 'total_rooms'}
        for key, val in kwargs.items():
            if key in allowed:
                setattr(hotel, key, val)
            else:
                print(f"Warning: '{key}' is not a modifiable field.")
        cls.save_all(hotels)
        print(f"Hotel '{hotel_id}' updated.")
        return True

    @classmethod
    def reserve_room(cls, hotel_id, reservation_id):
        """Decrement available rooms and track reservation ID."""
        hotels = cls.load_all()
        if hotel_id not in hotels:
            print(f"Error: Hotel '{hotel_id}' not found.")
            return False
        hotel = hotels[hotel_id]
        if hotel.available_rooms <= 0:
            print(f"Error: No available rooms at hotel '{hotel_id}'.")
            return False
        hotel.available_rooms -= 1
        hotel.reservations.append(reservation_id)
        cls.save_all(hotels)
        return True

    @classmethod
    def cancel_reservation(cls, hotel_id, reservation_id):
        """Increment available rooms and remove reservation record."""
        hotels = cls.load_all()
        if hotel_id not in hotels:
            print(f"Error: Hotel '{hotel_id}' not found.")
            return False
        hotel = hotels[hotel_id]
        if reservation_id not in hotel.reservations:
            print(
                f"Error: Reservation '{reservation_id}' "
                f"not found at hotel '{hotel_id}'."
            )
            return False
        hotel.reservations.remove(reservation_id)
        hotel.available_rooms = min(
            hotel.available_rooms + 1, hotel.total_rooms
        )
        cls.save_all(hotels)
        return True
