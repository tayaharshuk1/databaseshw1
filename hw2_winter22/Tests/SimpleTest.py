import unittest
import Solution
from Utility.ReturnValue import ReturnValue
from Tests.abstractTest import AbstractTest
from Business.Match import Match
from Business.Stadium import Stadium
from Business.Player import Player

'''
    Simple test, create one of your own
    make sure the tests' names start with test_
'''


class Test(AbstractTest):
    def test_Team(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addTeam(1), "ID 1 already exists")

    def test_Match(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(4), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(5), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(2, "Domestic", 1, 3)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(3, "Domestic", 1, 4)), "Should work")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addMatch(Match(1, "Domestic", 1, 5)), "ID 1 already exists")
        self.assertEqual(ReturnValue.OK, Solution.deleteMatch(Match(1)), "Should work")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.deleteMatch(Match(1)), "Match already deleted")

    def test_Player(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(1, 1, 20, 185, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(2, 1, 20, 185, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(3, 1, 20, 185, "Left")), "Should work")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addPlayer(Player(1, 1, 20, 185, "Left")), "ID 1 already exists")

    def test_Stadium(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addStadium(Stadium(1, 55000, 1)), "Should work")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addStadium(Stadium(1, 5000, 1)), "ID 1 already exists")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addStadium(Stadium(2, 5000, 3)), "teamID 3 not exists")

    def test_MatchBetweenSameTeam(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addMatch(Match(1, "Domestic", 1, 1)), "Team can't play against itself")

    def test_nonPositive(self) -> None:
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addTeam(0), "Non Positive IDs")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addTeam(-1), "Non Positive IDs")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPlayer(Player(-1, 1, 20, 185, "Left")), "Non Positive IDs")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPlayer(Player(1, -1, 20, 185, "Left")), "Non Positive team")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPlayer(Player(1, 1, -20, 185, "Left")), "Non Positive age")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPlayer(Player(1, 1, 20, -185, "Left")), "Non Positive height")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addMatch(Match(-1, "Domestic", 1, 2)), "Non Positive IDs")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addStadium(Stadium(-1, 5000, 1)), "Non Positive IDs")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addStadium(Stadium(1, -100, 1)), "Non Positive IDs")

    def test_strings(self) -> None:
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPlayer(Player(1, 1, 20, 185, "Lefti like it")), "Bad String")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addMatch(Match(1, "Dome", 1, 2)), "Bad String")

    def test_PlayerScore(self):
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addPlayer(Player(1, 3, 20, 185, "Left")), "No team")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(1, 1, 20, 185, "Left")), "Should work")
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addPlayer(Player(1, 1, 20, 185, "Left")), "Already exists")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), 1), "Match Does not exists")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=2), 1), "Player Does not exists")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.playerScoredInMatch(Match(matchID=2), Player(playerID=1), 1), "Match Does not exists")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), 0), "amount not positive")
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), -1), "amount not positive")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), 1), "Should work")




# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
