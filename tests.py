import unittest
from generate_timings import *

class TestTempos(unittest.TestCase):
  def test_fixed(self):
    t = FIXED_TEMPO(100)

    self.assertEquals(t(-100, -1), 100)
    self.assertEquals(t(100, -1), 100)
    self.assertEquals(t(1000, -1), 100)

  def test_ramp(self):
    r = TEMPO_RAMP_SECONDS(0, 100, 10)
  
    self.assertEquals(r(-1, -1), 0)
    self.assertEqual(r(0, -1), 00)
    self.assertEqual(r(2, -1), 20)
    self.assertEqual(r(5, -1), 50)
    self.assertEqual(r(10, -1), 100)
    self.assertEquals(r(100, -1), 100)

class TestNoteDuration(unittest.TestCase):
  def test_unchanging_tempo(self):
    def TF(ts, beats):
      return 120

    g = Gesture()
    self.assertAlmostEquals(0.5, g._ComputeNoteDuration(Quarter(), 0, 0, TF))

  def test_linear_tempo_change(self):
    def TF(ts, beats):
      return 60 + beats

    g = Gesture()
    self.assertAlmostEqual(3.87232376, g._ComputeNoteDuration(Whole(), 0, 0, TF))

  def test_exponential_tempo_change(self):
    def TF(ts, beats):
      return 60**(beats + 1)

    g = Gesture()
    self.assertAlmostEqual(0.24443937, g._ComputeNoteDuration(Whole(), 0, 0, TF))

if __name__ == "__main__":
  unittest.main()
