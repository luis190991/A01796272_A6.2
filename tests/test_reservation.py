"""Unit tests for the Reservation class."""
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from hotel_system.hotel import Hotel
from hotel_system.customer import Customer
from hotel_system.reservation import Reservation


class TestReservation(unittest.TestCase):
    """Test cases for Reservation management."""

    def setUp(self):
        """Create temp dir and redirect all DATA_FILE attributes."""
        self.test_dir = tempfile.mkdtemp()

        self.orig_res = Reservation.DATA_FILE
        self.orig_hotel = Hotel.DATA_FILE
        self.orig_customer = Customer.DATA_FILE

        Reservation.DATA_FILE = os.path.join(
            self.test_dir, 'reservations.json'
        )
        Hotel.DATA_FILE = os.path.join(self.test_dir, 'hotels.json')
        Customer.DATA_FILE = os.path.join(self.test_dir, 'customers.json')

        # Seed one hotel and one customer for most tests
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 5)
        Customer.create('C1', 'Alice', 'alice@example.com', '555-1234')

    def tearDown(self):
        """Restore DATA_FILE attributes and remove temp directory."""
        Reservation.DATA_FILE = self.orig_res
        Hotel.DATA_FILE = self.orig_hotel
        Customer.DATA_FILE = self.orig_customer
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def test_to_dict(self):
        """Reservation.to_dict returns correct mapping."""
        res = Reservation('R1', 'C1', 'H1', '2025-01-10', '2025-01-15')
        result = res.to_dict()
        self.assertEqual(result['reservation_id'], 'R1')
        self.assertEqual(result['status'], 'active')

    def test_from_dict_success(self):
        """Reservation.from_dict creates object from valid dict."""
        data = {
            'reservation_id': 'R1',
            'customer_id': 'C1',
            'hotel_id': 'H1',
            'check_in': '2025-01-10',
            'check_out': '2025-01-15',
            'status': 'active',
        }
        res = Reservation.from_dict(data)
        self.assertIsNotNone(res)
        self.assertEqual(res.reservation_id, 'R1')
        self.assertEqual(res.status, 'active')

    def test_from_dict_missing_field(self):
        """Reservation.from_dict returns None on missing key."""
        result = Reservation.from_dict({'reservation_id': 'R1'})
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------
    def test_load_all_no_file(self):
        """load_all returns empty dict when file does not exist."""
        self.assertEqual(Reservation.load_all(), {})

    def test_load_all_invalid_json(self):
        """load_all returns empty dict for corrupt JSON."""
        with open(Reservation.DATA_FILE, 'w', encoding='utf-8') as fh:
            fh.write('not valid json')
        self.assertEqual(Reservation.load_all(), {})

    def test_load_all_invalid_record(self):
        """load_all skips records with missing fields."""
        bad_data = {'R1': {'reservation_id': 'R1'}}
        with open(Reservation.DATA_FILE, 'w', encoding='utf-8') as fh:
            json.dump(bad_data, fh)
        self.assertEqual(Reservation.load_all(), {})

    def test_load_all_os_error(self):
        """load_all returns empty dict on OS read error."""
        with open(Reservation.DATA_FILE, 'w', encoding='utf-8') as fh:
            json.dump({}, fh)
        with patch('builtins.open', side_effect=OSError('no read')):
            result = Reservation.load_all()
        self.assertEqual(result, {})

    def test_save_all_os_error(self):
        """save_all prints error on OS write error without raising."""
        res = Reservation('R1', 'C1', 'H1', '2025-01-10', '2025-01-15')
        with patch('builtins.open', side_effect=OSError('no write')):
            Reservation.save_all({'R1': res})

    # ------------------------------------------------------------------
    # Date validation
    # ------------------------------------------------------------------
    def test_validate_dates_invalid_format(self):
        """validate_dates returns (None, None) for bad format."""
        date_in, date_out = Reservation.validate_dates(
            '10-01-2025', '2025-01-15'
        )
        self.assertIsNone(date_in)
        self.assertIsNone(date_out)

    def test_validate_dates_checkout_before_checkin(self):
        """validate_dates returns (None, None) when out <= in."""
        date_in, date_out = Reservation.validate_dates(
            '2025-01-15', '2025-01-10'
        )
        self.assertIsNone(date_in)
        self.assertIsNone(date_out)

    def test_validate_dates_same_day(self):
        """validate_dates returns (None, None) for same day."""
        date_in, _ = Reservation.validate_dates(
            '2025-01-10', '2025-01-10'
        )
        self.assertIsNone(date_in)

    def test_validate_dates_success(self):
        """validate_dates returns datetime objects for valid input."""
        date_in, date_out = Reservation.validate_dates(
            '2025-01-10', '2025-01-15'
        )
        self.assertIsNotNone(date_in)
        self.assertIsNotNone(date_out)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def test_create_success(self):
        """create returns a Reservation for valid inputs."""
        res = Reservation.create(
            'R1', 'C1', 'H1', '2025-01-10', '2025-01-15'
        )
        self.assertIsNotNone(res)
        self.assertEqual(res.reservation_id, 'R1')
        self.assertEqual(res.status, 'active')
        hotel = Hotel.get('H1')
        self.assertEqual(hotel.available_rooms, 4)

    def test_create_duplicate(self):
        """create returns None when reservation_id already exists."""
        Reservation.create('R1', 'C1', 'H1', '2025-01-10', '2025-01-15')
        result = Reservation.create(
            'R1', 'C1', 'H1', '2025-02-10', '2025-02-15'
        )
        self.assertIsNone(result)

    def test_create_invalid_dates(self):
        """create returns None for invalid date format."""
        result = Reservation.create(
            'R1', 'C1', 'H1', 'bad-date', '2025-01-15'
        )
        self.assertIsNone(result)

    def test_create_customer_not_found(self):
        """create returns None when customer does not exist."""
        result = Reservation.create(
            'R1', 'C999', 'H1', '2025-01-10', '2025-01-15'
        )
        self.assertIsNone(result)

    def test_create_hotel_not_found(self):
        """create returns None when hotel does not exist."""
        result = Reservation.create(
            'R1', 'C1', 'H999', '2025-01-10', '2025-01-15'
        )
        self.assertIsNone(result)

    def test_create_no_rooms(self):
        """create returns None when hotel has no available rooms."""
        Hotel.create('H2', 'Small', 'LA', 3.0, 1)
        Reservation.create('R1', 'C1', 'H2', '2025-01-10', '2025-01-15')
        result = Reservation.create(
            'R2', 'C1', 'H2', '2025-02-10', '2025-02-15'
        )
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Cancel
    # ------------------------------------------------------------------
    def test_cancel_success(self):
        """cancel sets status to cancelled and restores room."""
        Reservation.create('R1', 'C1', 'H1', '2025-01-10', '2025-01-15')
        self.assertTrue(Reservation.cancel('R1'))
        res = Reservation.get('R1')
        self.assertEqual(res.status, 'cancelled')
        hotel = Hotel.get('H1')
        self.assertEqual(hotel.available_rooms, 5)

    def test_cancel_not_found(self):
        """cancel returns False for unknown reservation_id."""
        self.assertFalse(Reservation.cancel('R999'))

    def test_cancel_already_cancelled(self):
        """cancel returns False when reservation is already cancelled."""
        Reservation.create('R1', 'C1', 'H1', '2025-01-10', '2025-01-15')
        Reservation.cancel('R1')
        self.assertFalse(Reservation.cancel('R1'))

    # ------------------------------------------------------------------
    # Get / Display
    # ------------------------------------------------------------------
    def test_get_existing(self):
        """get returns Reservation for known ID."""
        Reservation.create('R1', 'C1', 'H1', '2025-01-10', '2025-01-15')
        self.assertIsNotNone(Reservation.get('R1'))

    def test_get_not_found(self):
        """get returns None for unknown ID."""
        self.assertIsNone(Reservation.get('R999'))

    def test_display_success(self):
        """display returns True and prints reservation info."""
        Reservation.create('R1', 'C1', 'H1', '2025-01-10', '2025-01-15')
        self.assertTrue(Reservation.display('R1'))

    def test_display_not_found(self):
        """display returns False for unknown ID."""
        self.assertFalse(Reservation.display('R999'))


if __name__ == '__main__':
    unittest.main()
