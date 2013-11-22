import unittest
from generate_timings import *

class TestTempos(unittest.TestCase):
  def test_fixed(self):
    t = FIXED_TEMPO(100)

    self.assertEquals(t(-100), 100)
    self.assertEquals(t(100), 100)
    self.assertEquals(t(1000), 100)

  def test_ramp(self):
    r = TEMPO_RAMP(0, 100, 10)
  
    self.assertEquals(r(-1), 0)
    self.assertEqual(r(0), 00)
    self.assertEqual(r(2), 20)
    self.assertEqual(r(5), 50)
    self.assertEqual(r(10), 100)
    self.assertEquals(r(100), 100)

if __name__ == "__main__":
  unittest.main()
