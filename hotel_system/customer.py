"""Customer management module."""
import json
import os


class Customer:
    """Represents a customer with management capabilities."""

    DATA_FILE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data', 'customers.json'
    )

    def __init__(self, customer_id, name, email, phone):
        """Initialize Customer instance."""
        self.customer_id = str(customer_id)
        self.name = str(name)
        self.email = str(email)
        self.phone = str(phone)

    def to_dict(self):
        """Serialize customer to dictionary."""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize customer from dictionary."""
        try:
            return cls(
                customer_id=data['customer_id'],
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
            )
        except (KeyError, ValueError, TypeError) as exc:
            print(f"Error loading customer record: {exc}")
            return None

    @classmethod
    def load_all(cls):
        """Load all customers from JSON file."""
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
            print(f"Error: Corrupt customers file - {exc}")
            return {}
        except OSError as exc:
            print(f"Error: Cannot read customers file - {exc}")
            return {}

    @classmethod
    def save_all(cls, customers):
        """Save all customers to JSON file."""
        directory = os.path.dirname(cls.DATA_FILE)
        os.makedirs(directory, exist_ok=True)
        try:
            with open(cls.DATA_FILE, 'w', encoding='utf-8') as file_h:
                json.dump(
                    {k: v.to_dict() for k, v in customers.items()},
                    file_h,
                    indent=2,
                )
        except OSError as exc:
            print(f"Error: Cannot write customers file - {exc}")

    @classmethod
    def create(cls, customer_id, name, email, phone):
        """Create and persist a new customer."""
        customers = cls.load_all()
        if customer_id in customers:
            print(f"Error: Customer '{customer_id}' already exists.")
            return None
        customer = cls(customer_id, name, email, phone)
        customers[customer_id] = customer
        cls.save_all(customers)
        print(f"Customer '{name}' created (ID: {customer_id}).")
        return customer

    @classmethod
    def delete(cls, customer_id):
        """Delete a customer by ID."""
        customers = cls.load_all()
        if customer_id not in customers:
            print(f"Error: Customer '{customer_id}' not found.")
            return False
        name = customers[customer_id].name
        del customers[customer_id]
        cls.save_all(customers)
        print(f"Customer '{name}' deleted.")
        return True

    @classmethod
    def get(cls, customer_id):
        """Return a Customer object or None."""
        return cls.load_all().get(customer_id)

    @classmethod
    def display(cls, customer_id):
        """Print customer details to console."""
        customer = cls.get(customer_id)
        if customer is None:
            print(f"Error: Customer '{customer_id}' not found.")
            return False
        print(f"Customer ID: {customer.customer_id}")
        print(f"Name       : {customer.name}")
        print(f"Email      : {customer.email}")
        print(f"Phone      : {customer.phone}")
        return True

    @classmethod
    def modify(cls, customer_id, **kwargs):
        """Update customer attributes."""
        customers = cls.load_all()
        if customer_id not in customers:
            print(f"Error: Customer '{customer_id}' not found.")
            return False
        customer = customers[customer_id]
        allowed = {'name', 'email', 'phone'}
        for key, val in kwargs.items():
            if key in allowed:
                setattr(customer, key, val)
            else:
                print(f"Warning: '{key}' is not a modifiable field.")
        cls.save_all(customers)
        print(f"Customer '{customer_id}' updated.")
        return True
