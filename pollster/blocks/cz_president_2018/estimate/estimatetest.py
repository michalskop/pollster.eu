"""Unit test for estimation"""

import estimate
import unittest


class CorrectDownloadsDatapackages(unittest.TestCase):
    '''Number of rows in the dp is more than 0'''
    def testTisportValuesExist(self):
        self.assertTrue(len(estimate.tipsport_dp.resources) > 0)

    def testFortunaValuesExist(self):
        self.assertTrue(len(estimate.fortuna_dp.resources) > 0)

    def testBetfairValuesExist(self):
        self.assertTrue(len(estimate.betfair_dp.resources) > 0)

    '''Number of rows in the dp for last time is more than 1'''
    def testTisportLastValuesExist(self):
        self.assertTrue(len(estimate.tipsport_odds) > 1)

    def testFortunaLastValuesExist(self):
        self.assertTrue(len(estimate.fortuna_odds) > 1)

    def testBetfairLastValuesExist(self):
        self.assertTrue(len(estimate.betfair_odds) > 1)

    '''probability of all is 1'''
    def testTipsportProbability1(self):
        s = 0
        for candidate in estimate.candidates:
            s += candidate['tipsport_probability']
        self.assertTrue(round(s * 1000000) / 1000000 == 1)  # round errors awareness

    def testFortunaProbability1(self):
        s = 0
        for candidate in estimate.candidates:
            s += candidate['fortuna_probability']
        self.assertTrue(round(s * 1000000) / 1000000 == 1)  # round errors awareness

    def testProbability1(self):
        s = 0
        for candidate in estimate.candidates:
            s += candidate['probability']
        self.assertTrue(round(s * 1000000) / 1000000 == 1)


if __name__ == '__main__':
    unittest.main()
