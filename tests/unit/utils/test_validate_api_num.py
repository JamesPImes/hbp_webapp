import unittest

from backend.utils import validate_api_num


class TestValidateApiNum(unittest.TestCase):
    def test_success_3_components(self):
        yes = "05-123-45678"
        self.assertTrue(validate_api_num(yes))

    def test_success_5_components(self):
        yes = "05-123-45678-00-00"
        self.assertTrue(validate_api_num(yes))

    def test_fail_4_components(self):
        no = "05-123-45678-99"
        self.assertFalse(validate_api_num(no))

    def test_fail_6_components(self):
        no = "05-123-45678-99-99-99"
        self.assertFalse(validate_api_num(no))

    def test_fail_wrong_state(self):
        no = "99-123-45678"
        self.assertFalse(validate_api_num(no))

    def test_fail_county_code_wrong_length_3_components(self):
        no = "99-12-45678"
        self.assertFalse(validate_api_num(no))

    def test_fail_well_code_wrong_length_3_components(self):
        no = "99-123-4567"
        self.assertFalse(validate_api_num(no))

    def test_fail_county_code_wrong_length_5_components(self):
        no = "99-12-45678-99-99"
        self.assertFalse(validate_api_num(no))

    def test_fail_well_code_wrong_length_5_components(self):
        no = "99-123-4567-99-99"
        self.assertFalse(validate_api_num(no))


if __name__ == "__main__":
    unittest.main()
