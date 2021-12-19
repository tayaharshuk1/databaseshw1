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
        self.assertEqual(ReturnValue.BAD_PARAMS, Solution.addMatch(Match(1, "domestic", 1, 2)), "Bad String")

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

    def test_playerIsWinner(self):
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(1, 1, 20, 185, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(2, 1, 20, 185, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), 1), "Should work")
        self.assertEqual(True, Solution.playerIsWinner(1, 1))
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=2), 1), "Should work")
        self.assertEqual(True, Solution.playerIsWinner(1, 1))
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=2), 1), "AlreadyExists")
        self.assertEqual(ReturnValue.OK, Solution.playerDidntScoreInMatch(match=Match(1), player=Player(2)))
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=2), 2), "Should work")
        self.assertEqual(False, Solution.playerIsWinner(1, 1))

    def test_activeTallTeams1(self):
        """
        team 1 both tall and active
        team 2 is active
        team 3 is tall
        team 4 neither
        """
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(4), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(1, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(2, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(3, 3, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(4, 3, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(5, 2, 20, 190, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(6, 2, 20, 190, "Left")), "Should work")
        self.assertEqual([1], Solution.getActiveTallTeams())

    def test_activeTallTeams2(self):
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(4), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(5), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(6), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(2, "Domestic", 3, 4)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(3, "Domestic", 5, 6)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(1, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(2, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(3, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(4, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(5, 3, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(6, 3, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(11, 6, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(12, 6, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(7, 4, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(8, 4, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(9, 5, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(10, 5, 20, 195, "Left")), "Should work")
        self.assertEqual([6, 5, 4, 3, 2], Solution.getActiveTallTeams())








# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
