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
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), 1), "Match Does not exists")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=2), 1), "Player Does not exists")
        self.assertEqual(ReturnValue.NOT_EXISTS, Solution.playerScoredInMatch(Match(matchID=2), Player(playerID=1), 1), "Match Does not exists")
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

    def test_popularTeams(self):
        """
        team 1 is popular by definition
        team 2 is popular in empty way
        team 3 isn't popular
        team 4 is popular
        team 5 isn't popular
        team 6 is popular in empty way
        :return:
        """
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(4), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(5), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(6), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(2, "Domestic", 3, 4)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(3, "Domestic", 4, 5)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(4, "Domestic", 5, 1)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(5, "Domestic", 3, 4)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addStadium(Stadium(1, 50000, 1)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(1), stadium=Stadium(1), attendance=40001))
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(2), stadium=Stadium(1), attendance=40000))
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(3), stadium=Stadium(1), attendance=40001))
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(5), stadium=Stadium(1), attendance=50000))
        self.assertEqual([6, 4, 2, 1], Solution.popularTeams())

    def test_getMostAttractiveStadiums(self):
        """
        Stadium 1 : 1 Match of 3 goal
        Stadium 2 : 2 Matches 2 goals + 2 goals (total of 4 goals)
        Stadium 3 : 2 Match of 2 goals + 1 goal (total of 3 goals)
        Stadium 4 : no matches
        Stadium 5 : 1 Match, no goals
        :return: [2, 1, 3, 4, 5]
        """
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(1, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(2, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(3, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(4, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(5, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(6, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addStadium(Stadium(1, 50000, 1)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addStadium(Stadium(2, 50000, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addStadium(Stadium(3, 50000, None)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addStadium(Stadium(4, 50000, None)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addStadium(Stadium(5, 50000, None)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(1), stadium=Stadium(1), attendance=40001))
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), 3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(2), stadium=Stadium(2), attendance=40001))
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(3), stadium=Stadium(2), attendance=40001))
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=2), Player(playerID=1), 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=3), Player(playerID=1), 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(4), stadium=Stadium(3), attendance=40001))
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(5), stadium=Stadium(3), attendance=40001))
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=4), Player(playerID=1), 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=5), Player(playerID=1), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.matchInStadium(match=Match(6), stadium=Stadium(5), attendance=40001))
        self.assertEqual([2, 1, 3, 4, 5], Solution.getMostAttractiveStadiums())

    def test_mostGoalsForTeam(self):
        """
        Team1 contains players 1, 2, 3, 4
        Team2 contains player 5 - best scorer, irrelevant
        player 1 - Scores 1, 1 in two games
        player 2 - Scores 3
        player 3,6,7 - Didn't score
        player 4 - Scores 2

        player 5, irrelevant - scores 5 in a match against team 1

        :return: [2, 4, 1, 7, 6]
        """
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(1, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(2, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(3, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(4, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(5, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(6, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(7, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(2, "Domestic", 2, 1)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=2), Player(playerID=1), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=2), 3), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=4), 2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=5), 7), "Should work")
        self.assertEqual([2, 4, 1, 7, 6], Solution.mostGoalsForTeam(1))

    def test_getClosePlayers(self):
        """
        player 1, Scored in 4 matches (ids: 1, 2, 3, 4) 20 goals
        player 2, didn't score at all
        player 3, scored in 4 matches, (ids: 3, 4, 5, 6) // close to 1
        player 4, scored in 2 matches, (ids: 4, 5) // not close to 1
        player 5, scored in 1 match, (ids: 4) // not close to 1
        player 6, scored in all 7 matches // close to 1
        player 7, scored in 4 matches (id: 4, 5, 6, 7) // not close to 1
        player 8, 9, 10, 11, 12 didn't score at all

        :return: Close to player 1 : [6, 3]
        :return: Close to player 8 : [12, 11, 10, 9, 7, 6, 5, 4, 3, 2]
        """
        self.assertEqual(ReturnValue.OK, Solution.addTeam(1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addTeam(2), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(1, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(2, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(3, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(4, 1, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(5, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(6, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(7, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(8, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(9, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(10, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(11, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addPlayer(Player(12, 2, 20, 195, "Left")), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(1, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(2, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(3, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(4, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(5, "Domestic", 1, 2)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(6, "Domestic", 2, 1)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.addMatch(Match(7, "Domestic", 2, 1)), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=1), 5), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=2), Player(playerID=1), 5), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=3), Player(playerID=1), 5), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=4), Player(playerID=1), 5), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=3), Player(playerID=3), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=4), Player(playerID=3), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=5), Player(playerID=3), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=6), Player(playerID=3), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=4), Player(playerID=4), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=5), Player(playerID=4), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=4), Player(playerID=5), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=1), Player(playerID=6), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=2), Player(playerID=6), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=3), Player(playerID=6), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=4), Player(playerID=6), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=5), Player(playerID=6), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=6), Player(playerID=6), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=7), Player(playerID=6), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=4), Player(playerID=7), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=5), Player(playerID=7), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=6), Player(playerID=7), 1), "Should work")
        self.assertEqual(ReturnValue.OK, Solution.playerScoredInMatch(Match(matchID=7), Player(playerID=7), 1), "Should work")
        self.assertEqual([3, 6], Solution.getClosePlayers(1))
        self.assertEqual([1, 2, 3, 4, 5, 6, 7, 9, 10, 11], Solution.getClosePlayers(8))


        def test_deleteOfRecord:
        #teams: 1,2,3
        #player 1 in team 2

        #stadiums: 10,20

        #return
        #TODO: shouldwork? , when we have BADPARAMS?

        self.assertEqual((ReturnValue.OK,Solution.addTeam(1)), "Should work")
        self.assertEqual((ReturnValue.OK, Solution.addTeam(2)), "Should work")
        self.assertEqual((ReturnValue.OK, Solution.addTeam(30)), "Should work")
        self.assertEqual((ReturnValue.ALREADY_EXISTS, Solution.addTeam(1)), "Shoult work")  #trying to add again team1
        #self.assertEqual((ReturnValue.OK, Solution.defineTables),)
        self.assertEqual(ReturnValue.OK,Solution.addPlayer(Player(1,2,20,195, "Left")))  #add player 1 to team 2
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addPlayer(Player(1, 2, 20, 195, "Left"))) #trying to add player 1 to team 2
        self.assertEqual(ReturnValue.ALREADY_EXISTS, Solution.addPlayer(Player(1, 3, 20, 195, "Left")))
        self.assertEqual(ReturnValue.OK, Solution.deletePlayer(Player(1, 2, 20, 195, "Left")))  #deleting player 1
        self.assertEqual(ReturnValue.OK, Solution.getPlayerProfile(1))     #trying to get profile of a player who doesnt exist
        self.assertEqual((ReturnValue.OK, Solution.addStadium(Stadium(10,300))),"Should work")
        self.assertEqual((ReturnValue.OK, Solution.addStadium(Stadium(20, 200))),"Should work")
        self.assertEqual((ReturnValue.ALREADY_EXISTS, Solution.addStadium(Stadium(10, 300))), "Should work") #trying to add an existing stadium
        self.assertEqual((ReturnValue.OK, Solution.deleteStadium(Stadium(20, 200))),"Should work" )
        self.assertEqual((ReturnValue.NOT_EXISTS, Solution.getStadiumProfile(20),"Should work") #trying to get a profile of stadium that doesnt exist




        def test_getRecords:

        def test_cleanTables

# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
