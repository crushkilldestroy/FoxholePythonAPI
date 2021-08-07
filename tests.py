import foxholewar
import unittest


class TestFoxholeWar(unittest.TestCase):

    def setUp(self):
        self.clients = [foxholewar.Client('live1'), foxholewar.Client('live2')]

    def testWarInfo(self):
        for client in self.clients:
            war = client.fetch_current_war()
            self.assertTrue(war.warId)
            self.assertTrue(war.warNumber)
            self.assertTrue(war.winner)
            self.assertTrue(war.conquestStartTime)
            self.assertTrue(war.conquestEndTime or foxholewar.Team[war.winner] is foxholewar.Team.NONE)
            self.assertTrue(war.resistanceStartTime or not war.conquestEndTime)
            self.assertTrue(war.requiredVictoryTowns)

    def testMapList(self):
        for client in self.clients:
            map_list = client.fetch_map_list()
            self.assertTrue(map_list)

            for current_map in map_list:
                self.assertTrue(current_map.rawName)
                self.assertTrue(current_map.prettyName)
                self.assertTrue(current_map.scorchedVictoryTowns is not None)
                self.assertTrue(current_map.regionId)

                for item in current_map.mapTextItems:
                    self.assertTrue(item.text)
                    self.assertTrue(item.x)
                    self.assertTrue(item.y)
                    self.assertTrue(item.mapMarkerType)

                for item in current_map.mapItems:
                    self.assertTrue(item.teamId)
                    self.assertTrue(item.iconType)
                    self.assertTrue(item.x)
                    self.assertTrue(item.y)
                    self.assertTrue(item.flags is not None)

                report = client.fetch_report(current_map)
                self.assertTrue(report is not None)

    def tearDown(self):
        for client in self.clients:
            client.close()


if __name__ == '__main__':
    unittest.main()
