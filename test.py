import unittest
from workout import getInput
from workout import get_categories
from workout import get_exercises
from workout import get_category
from workout import choose_exercise
from workout import get_choices


class TestFileName(unittest.TestCase):
    def test_get_categories_return_type(self):
        self.assertIsInstance(get_categories("UPPER"),
                            dict, "Is not dictionary")

    def test_get_categories_for_valid_response(self):
        upper = get_categories("UPPER")
        compare_upper = {8: "arms", 12: "back", 11: "chest", 13: "shoulders"}
        self.assertEqual(upper, compare_upper)

        lower = get_categories("LOWER")
        compare_lower = {14: "calves", 9: "legs"}
        self.assertEqual(lower, compare_lower)

        all = get_categories("ALL")
        compare_all = {10: "abs", 8: "arms", 12: "back",
                        14: "calves", 11: "chest", 9: "legs", 13: "shoulders"}
        self.assertEqual(all, compare_all)

        bnb = get_categories("BNB")
        compare_bnb = {8: "arms", 12: "back"}
        self.assertEqual(bnb, compare_bnb)

        cnt = get_categories("CNT")
        compare_cnt = {8: "arms", 11: "chest"}
        self.assertEqual(cnt, compare_cnt)

    def test_get_categories_for_invalid_response(self):
        random_bad_input = get_categories("INVALID")
        self.assertFalse(random_bad_input)

    def test_get_exercises_return_type(self):
        # can assume get_category will return a valid int
        resp = get_exercises(8)
        self.assertIsInstance(resp, dict)

    def test_get_exercises_invalid_input(self):
        resp = get_exercises(-1)
        self.assertIsInstance(resp, dict)
        # empty dicts assert false
        self.assertFalse(resp)

    def test_get_choice(self):
        print("")


if __name__ == '__main__':
    unittest.main()
