"""Unit tests for the Hotel class."""
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from hotel_system.hotel import Hotel


class TestHotel(unittest.TestCase):
    """Test cases for Hotel management."""

    def setUp(self):
        """Create a temp directory and redirect DATA_FILE."""
        self.test_dir = tempfile.mkdtemp()
        self.original_data_file = Hotel.DATA_FILE
        Hotel.DATA_FILE = os.path.join(self.test_dir, 'hotels.json')

    def tearDown(self):
        """Restore DATA_FILE and remove temp directory."""
        Hotel.DATA_FILE = self.original_data_file
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def test_to_dict(self):
        """Hotel.to_dict returns correct mapping."""
        hotel = Hotel('H1', 'Grand', 'NYC', 4.5, 100)
        result = hotel.to_dict()
        self.assertEqual(result['hotel_id'], 'H1')
        self.assertEqual(result['name'], 'Grand')
        self.assertEqual(result['location'], 'NYC')
        self.assertAlmostEqual(result['rating'], 4.5)
        self.assertEqual(result['total_rooms'], 100)
        self.assertEqual(result['available_rooms'], 100)
        self.assertEqual(result['reservations'], [])

    def test_from_dict_success(self):
        """Hotel.from_dict creates hotel from valid dict."""
        data = {
            'hotel_id': 'H1',
            'name': 'Grand',
            'location': 'NYC',
            'rating': 4.5,
            'total_rooms': 100,
            'available_rooms': 80,
            'reservations': ['R1'],
        }
        hotel = Hotel.from_dict(data)
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.hotel_id, 'H1')
        self.assertEqual(hotel.available_rooms, 80)
        self.assertIn('R1', hotel.reservations)

    def test_from_dict_missing_field(self):
        """Hotel.from_dict returns None when a required key is missing."""
        result = Hotel.from_dict({'hotel_id': 'H1', 'name': 'Grand'})
        self.assertIsNone(result)

    def test_from_dict_invalid_type(self):
        """Hotel.from_dict returns None when type conversion fails."""
        data = {
            'hotel_id': 'H1',
            'name': 'Grand',
            'location': 'NYC',
            'rating': 'not_a_float',
            'total_rooms': 100,
        }
        result = Hotel.from_dict(data)
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------
    def test_load_all_no_file(self):
        """load_all returns empty dict when file does not exist."""
        self.assertEqual(Hotel.load_all(), {})

    def test_load_all_invalid_json(self):
        """load_all returns empty dict and prints error for corrupt JSON."""
        with open(Hotel.DATA_FILE, 'w', encoding='utf-8') as fh:
            fh.write('not valid json')
        result = Hotel.load_all()
        self.assertEqual(result, {})

    def test_load_all_invalid_record(self):
        """load_all skips records with missing fields."""
        bad_data = {'H1': {'hotel_id': 'H1'}}
        with open(Hotel.DATA_FILE, 'w', encoding='utf-8') as fh:
            json.dump(bad_data, fh)
        result = Hotel.load_all()
        self.assertEqual(result, {})

    def test_load_all_os_error(self):
        """load_all returns empty dict on OS read error."""
        with open(Hotel.DATA_FILE, 'w', encoding='utf-8') as fh:
            json.dump({}, fh)
        with patch('builtins.open', side_effect=OSError('no read')):
            result = Hotel.load_all()
        self.assertEqual(result, {})

    def test_save_all_os_error(self):
        """save_all prints error on OS write error without raising."""
        hotel = Hotel('H1', 'Grand', 'NYC', 4.5, 100)
        with patch('builtins.open', side_effect=OSError('no write')):
            Hotel.save_all({'H1': hotel})

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def test_create_success(self):
        """create returns a Hotel when data is valid."""
        hotel = Hotel.create('H1', 'Grand', 'NYC', 4.5, 100)
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.hotel_id, 'H1')
        self.assertEqual(hotel.name, 'Grand')
        self.assertEqual(hotel.available_rooms, 100)

    def test_create_duplicate(self):
        """create returns None when hotel_id already exists."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 100)
        result = Hotel.create('H1', 'Other', 'LA', 3.0, 50)
        self.assertIsNone(result)

    def test_create_invalid_data(self):
        """create returns None when rating cannot be converted to float."""
        result = Hotel.create('H1', 'Grand', 'NYC', 'bad', 100)
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def test_delete_success(self):
        """delete removes hotel and returns True."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 100)
        self.assertTrue(Hotel.delete('H1'))
        self.assertIsNone(Hotel.get('H1'))

    def test_delete_not_found(self):
        """delete returns False for unknown hotel_id."""
        self.assertFalse(Hotel.delete('H999'))

    # ------------------------------------------------------------------
    # Get / Display
    # ------------------------------------------------------------------
    def test_get_existing(self):
        """get returns Hotel for known ID."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 100)
        self.assertIsNotNone(Hotel.get('H1'))

    def test_get_not_found(self):
        """get returns None for unknown ID."""
        self.assertIsNone(Hotel.get('H999'))

    def test_display_success(self):
        """display returns True and prints hotel info."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 100)
        self.assertTrue(Hotel.display('H1'))

    def test_display_not_found(self):
        """display returns False for unknown ID."""
        self.assertFalse(Hotel.display('H999'))

    # ------------------------------------------------------------------
    # Modify
    # ------------------------------------------------------------------
    def test_modify_success(self):
        """modify updates hotel fields and returns True."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 100)
        result = Hotel.modify('H1', name='Super Grand', rating=5.0)
        self.assertTrue(result)
        hotel = Hotel.get('H1')
        self.assertEqual(hotel.name, 'Super Grand')
        self.assertAlmostEqual(hotel.rating, 5.0)

    def test_modify_not_found(self):
        """modify returns False for unknown hotel_id."""
        self.assertFalse(Hotel.modify('H999', name='X'))

    def test_modify_invalid_field(self):
        """modify warns about unknown fields but still returns True."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 100)
        self.assertTrue(Hotel.modify('H1', nonexistent='value'))

    # ------------------------------------------------------------------
    # Reserve / Cancel room
    # ------------------------------------------------------------------
    def test_reserve_room_success(self):
        """reserve_room decrements available_rooms and logs reservation."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 2)
        self.assertTrue(Hotel.reserve_room('H1', 'R1'))
        hotel = Hotel.get('H1')
        self.assertEqual(hotel.available_rooms, 1)
        self.assertIn('R1', hotel.reservations)

    def test_reserve_room_hotel_not_found(self):
        """reserve_room returns False for unknown hotel."""
        self.assertFalse(Hotel.reserve_room('H999', 'R1'))

    def test_reserve_room_no_availability(self):
        """reserve_room returns False when no rooms remain."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 1)
        Hotel.reserve_room('H1', 'R1')
        self.assertFalse(Hotel.reserve_room('H1', 'R2'))

    def test_cancel_reservation_success(self):
        """cancel_reservation restores available_rooms and removes ID."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 2)
        Hotel.reserve_room('H1', 'R1')
        self.assertTrue(Hotel.cancel_reservation('H1', 'R1'))
        hotel = Hotel.get('H1')
        self.assertEqual(hotel.available_rooms, 2)
        self.assertNotIn('R1', hotel.reservations)

    def test_cancel_reservation_hotel_not_found(self):
        """cancel_reservation returns False for unknown hotel."""
        self.assertFalse(Hotel.cancel_reservation('H999', 'R1'))

    def test_cancel_reservation_id_not_found(self):
        """cancel_reservation returns False when ID not in list."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 2)
        self.assertFalse(Hotel.cancel_reservation('H1', 'R999'))

    def test_cancel_reservation_caps_at_total(self):
        """cancel_reservation does not exceed total_rooms."""
        Hotel.create('H1', 'Grand', 'NYC', 4.5, 1)
        Hotel.reserve_room('H1', 'R1')
        Hotel.cancel_reservation('H1', 'R1')
        hotel = Hotel.get('H1')
        self.assertEqual(hotel.available_rooms, 1)


if __name__ == '__main__':
    unittest.main()
