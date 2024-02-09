import unittest
import text_result


class TestAdd(unittest.TestCase):
    def test_1(self):
        self.assertEqual(1 + 1, 2)

    def test_2(self):
        self.assertEqual(2 + 2, 4)


class TestMinus(unittest.TestCase):
    def test_1(self):
        self.assertEqual(2 - 1, 1)

    def test_2(self):
        self.assertEqual(3 - 1, 2)

class TestSeveral(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(1, 1)

    def test_fail(self):
        self.assertEqual(1, 0)

    def test_raise(self):
        raise ValueError("Oops")
    
    @unittest.skip(reason="it can be skipped")
    def test_skip(self):
        self.assertEqual(1, 0)

    @unittest.expectedFailure
    def test_can_be_failed(self):
        self.assertEqual(1, 0)

    @unittest.expectedFailure
    def test_should_be_failed(self):
        self.assertEqual(1, 1)
    

if __name__ == "__main__":
    #text_result.ResultFirstTextResult.COLORED = False
    runner = unittest.TextTestRunner(resultclass=text_result.BeautyTextResult, verbosity=2)
    unittest.main(testRunner=runner)