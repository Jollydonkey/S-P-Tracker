"""Exercise the custom fixes with synthetic data, not a live AC server."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / 'stracker', ROOT / 'stracker' / 'externals'):
    sys.path.insert(0, str(path))

# The application provides this adapter before importing its shared libraries.
import ptracker_lib
ptracker_lib.acsim = SimpleNamespace(offline=lambda: False, ac=SimpleNamespace(log=lambda *a: None))
from stracker_lib import config, logger
config.create_default_config(logger)
from stracker_lib.ac_monitor import ACDriver
from ptracker_lib.dbgeneric import GenericBackend, compress
from ptracker_lib.dbapsw import ApswConnectionWrapper
import apsw


class ReconnectTests(unittest.TestCase):
    def test_reconnect_refreshes_identity_and_clears_old_ptracker_connection(self):
        driver = ACDriver('synthetic-guid', lambda *a: None)
        driver.newConnectionEvent(SimpleNamespace(driverName='Old', driverTeam='A', carModel='car-a', carId=1))
        driver.ptracker_conn = object()
        driver.reconnectDriver(SimpleNamespace(driverName='New', driverTeam='B', carModel='car-b', carId=4))
        self.assertEqual((driver.name, driver.team, driver.car, driver.carId), ('New', 'B', 'car-b', 4))
        self.assertIsNone(driver.ptracker_conn)
        self.assertEqual(driver.guid, 'synthetic-guid')


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.connection = apsw.Connection(':memory:')
        sectors = ','.join('SectorTime%d INTEGER' % i for i in range(10))
        self.connection.execute('CREATE TABLE LapTimes (LapId INTEGER, Track TEXT, Car TEXT, '
                                'SteamGuid TEXT, Valid INTEGER, LapTime INTEGER, '
                                'SectorsAreSoftSplits INTEGER, ' + sectors + ')')
        self.connection.execute('CREATE TABLE LapBinBlob (LapId INTEGER, HistoryInfo BLOB)')
        self.backend = GenericBackend.__new__(GenericBackend)
        self.backend.db = ApswConnectionWrapper(self.connection)
        self.backend.invalidSplit = 86400000
        self.backend.lapHistoryFactory = lambda **kw: SimpleNamespace(**kw)
        invalid = self.backend.invalidSplit
        for row in [(1, 'track', 'car', 'one', 1, 90000, 0, 30000, 30000, 30000),
                    (2, 'track', 'car', 'two', 1, 95000, 0, 31000, 32000, 32000)]:
            values = row + (invalid,) * 7
            self.connection.execute('INSERT INTO LapTimes VALUES (' + ','.join('?' for _ in values) + ')', values)
        history = compress([0, 90000], [(0., 0., 0.), (1., 0., 0.)],
                           [(1., 0., 0.), (1., 0., 0.)], [0., 1.])
        self.connection.execute('INSERT INTO LapBinBlob VALUES (?,?)', (1, history))
        self.connection.execute('INSERT INTO LapBinBlob VALUES (?,?)', (2, None))

    def tearDown(self):
        self.connection.close()

    def test_pb_sb_and_sectors_reuse_one_cursor(self):
        # Multiple consecutive queries exercise the APSW cursor-consumption fix.
        with self.backend.db:
            cur = self.backend.db.cursor()
            for _ in range(3):
                self.assertEqual(self.backend.getSBandPB('track', 'car', 'two', cur), {'pb': 95000, 'sb': 90000})
                self.assertEqual(self.backend.getBestSectorTimes('track', 'car', cursor=cur), [30000] * 3 + [None] * 7)

    def test_empty_queries_return_no_records(self):
        self.assertEqual(self.backend.getSBandPB('missing', 'car', 'one'), {'pb': None, 'sb': None})
        self.assertEqual(self.backend.getBestSectorTimes('missing', 'car'), [None] * 10)
        self.assertIsNone(self.backend.getBestLap('missing', 'car'))

    def test_best_lap_preserves_history(self):
        lap = self.backend.getBestLap('track', 'car', assertHistoryInfo=True)
        self.assertEqual(lap.lapTime, 90000)
        self.assertEqual(lap.sectorTimes, [30000] * 3 + [None] * 7)
        self.assertEqual(lap.sampleTimes, [0, 90000])

    def test_best_lap_without_history_uses_fallback(self):
        lap = self.backend.getBestLap('track', 'car', playerGuid='two')
        self.assertEqual(lap.lapTime, 95000)
        self.assertIsNone(lap.sampleTimes)


if __name__ == '__main__':
    unittest.main(verbosity=2)
