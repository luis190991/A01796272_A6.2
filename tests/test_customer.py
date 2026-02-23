"""Unit tests for the Customer class."""
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from hotel_system.customer import Customer


class TestCustomer(unittest.TestCase):
    """Test cases for Customer management."""

    def setUp(self):
        """Create a temp directory and redirect DATA_FILE."""
        self.test_dir = tempfile.mkdtemp()
        self.original_data_file = Customer.DATA_FILE
        Customer.DATA_FILE = os.path.join(self.test_dir, 'customers.json')

    def tearDown(self):
        """Restore DATA_FILE and remove temp directory."""
        Customer.DATA_FILE = self.original_data_file
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def test_to_dict(self):
        """Customer.to_dict returns correct mapping."""
        customer = Customer('C1', 'Alice', 'alice@example.com', '555-1234')
        result = customer.to_dict()
        self.assertEqual(result['customer_id'], 'C1')
        self.assertEqual(result['name'], 'Alice')
        self.assertEqual(result['email'], 'alice@example.com')
        self.assertEqual(result['phone'], '555-1234')

    def test_from_dict_success(self):
        """Customer.from_dict creates customer from valid dict."""
        data = {
            'customer_id': 'C1',
            'name': 'Alice',
            'email': 'alice@example.com',
            'phone': '555-1234',
        }
        customer = Customer.from_dict(data)
        self.assertIsNotNone(customer)
        self.assertEqual(customer.customer_id, 'C1')

    def test_from_dict_missing_field(self):
        """Customer.from_dict returns None on missing key."""
        result = Customer.from_dict({'customer_id': 'C1', 'name': 'Alice'})
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------
    def test_load_all_no_file(self):
        """load_all returns empty dict when file does not exist."""
        self.assertEqual(Customer.load_all(), {})

    def test_load_all_invalid_json(self):
        """load_all returns empty dict for corrupt JSON."""
        with open(Customer.DATA_FILE, 'w', encoding='utf-8') as fh:
            fh.write('not valid json')
        self.assertEqual(Customer.load_all(), {})

    def test_load_all_invalid_record(self):
        """load_all skips records with missing required fields."""
        bad_data = {'C1': {'customer_id': 'C1'}}
        with open(Customer.DATA_FILE, 'w', encoding='utf-8') as fh:
            json.dump(bad_data, fh)
        self.assertEqual(Customer.load_all(), {})

    def test_load_all_os_error(self):
        """load_all returns empty dict on OS read error."""
        with open(Customer.DATA_FILE, 'w', encoding='utf-8') as fh:
            json.dump({}, fh)
        with patch('builtins.open', side_effect=OSError('no read')):
            result = Customer.load_all()
        self.assertEqual(result, {})

    def test_save_all_os_error(self):
        """save_all prints error on OS write error without raising."""
        customer = Customer('C1', 'Alice', 'alice@example.com', '555')
        with patch('builtins.open', side_effect=OSError('no write')):
            Customer.save_all({'C1': customer})

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def test_create_success(self):
        """create returns a Customer when data is valid."""
        customer = Customer.create(
            'C1', 'Alice', 'alice@example.com', '555-1234'
        )
        self.assertIsNotNone(customer)
        self.assertEqual(customer.customer_id, 'C1')
        self.assertEqual(customer.name, 'Alice')

    def test_create_duplicate(self):
        """create returns None when customer_id already exists."""
        Customer.create('C1', 'Alice', 'alice@example.com', '555-1234')
        result = Customer.create('C1', 'Bob', 'bob@example.com', '555-5678')
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def test_delete_success(self):
        """delete removes customer and returns True."""
        Customer.create('C1', 'Alice', 'alice@example.com', '555-1234')
        self.assertTrue(Customer.delete('C1'))
        self.assertIsNone(Customer.get('C1'))

    def test_delete_not_found(self):
        """delete returns False for unknown customer_id."""
        self.assertFalse(Customer.delete('C999'))

    # ------------------------------------------------------------------
    # Get / Display
    # ------------------------------------------------------------------
    def test_get_existing(self):
        """get returns Customer for known ID."""
        Customer.create('C1', 'Alice', 'alice@example.com', '555-1234')
        self.assertIsNotNone(Customer.get('C1'))

    def test_get_not_found(self):
        """get returns None for unknown ID."""
        self.assertIsNone(Customer.get('C999'))

    def test_display_success(self):
        """display returns True and prints customer info."""
        Customer.create('C1', 'Alice', 'alice@example.com', '555-1234')
        self.assertTrue(Customer.display('C1'))

    def test_display_not_found(self):
        """display returns False for unknown ID."""
        self.assertFalse(Customer.display('C999'))

    # ------------------------------------------------------------------
    # Modify
    # ------------------------------------------------------------------
    def test_modify_success(self):
        """modify updates customer fields and returns True."""
        Customer.create('C1', 'Alice', 'alice@example.com', '555-1234')
        result = Customer.modify('C1', name='Alicia', phone='555-9999')
        self.assertTrue(result)
        customer = Customer.get('C1')
        self.assertEqual(customer.name, 'Alicia')
        self.assertEqual(customer.phone, '555-9999')

    def test_modify_not_found(self):
        """modify returns False for unknown customer_id."""
        self.assertFalse(Customer.modify('C999', name='X'))

    def test_modify_invalid_field(self):
        """modify warns about unknown fields but still returns True."""
        Customer.create('C1', 'Alice', 'alice@example.com', '555-1234')
        self.assertTrue(Customer.modify('C1', nonexistent='value'))

    def test_modify_email(self):
        """modify can update email field."""
        Customer.create('C1', 'Alice', 'old@example.com', '555-1234')
        Customer.modify('C1', email='new@example.com')
        customer = Customer.get('C1')
        self.assertEqual(customer.email, 'new@example.com')


if __name__ == '__main__':
    unittest.main()
