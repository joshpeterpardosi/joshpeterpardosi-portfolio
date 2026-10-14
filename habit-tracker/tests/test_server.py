"""Black-box harness: every test talks HTTP to a real server subprocess."""
import json, os, shutil, socket, subprocess, sys, tempfile, unittest, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "..", "src", "server.py")
FIXTURES = os.path.join(HERE, "..", "fixtures")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Server:
    def __init__(self, data_file, today):
        self.port = free_port()
        env = dict(os.environ, HABIT_DATA_FILE=data_file, HABIT_TODAY=today)
        self.proc = subprocess.Popen([sys.executable, SERVER, str(self.port)], env=env,
                                     stdout=subprocess.PIPE, text=True)
        line = self.proc.stdout.readline()
        assert line.startswith("READY"), f"server failed to start: {line!r}"

    def call(self, method, path, body=None):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def kill(self):
        self.proc.kill()
        self.proc.wait()
        self.proc.stdout.close()


class HabitTrackerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.data = os.path.join(self.tmp, "habits.json")
        self.servers = []

    def tearDown(self):
        for s in self.servers:
            if s.proc.poll() is None:
                s.kill()
        shutil.rmtree(self.tmp)

    def start(self, today):
        s = Server(self.data, today)
        self.servers.append(s)
        return s

    def test_duplicate_check_in_same_day_rejected(self):
        s = self.start("2026-10-05")
        code, h = s.call("POST", "/habits", {"name": "Read"})
        self.assertEqual(code, 201)
        hid = h["habit_id"]
        self.assertEqual(s.call("POST", f"/habits/{hid}/check-in")[0], 201)
        code, _ = s.call("POST", f"/habits/{hid}/check-in")
        self.assertEqual(code, 409)
        _, st = s.call("GET", f"/habits/{hid}/streak")
        self.assertEqual(st["check_ins"], ["2026-10-05"])
        with open(self.data) as f:  # on-disk state too, not just the response
            self.assertEqual(json.load(f)["habits"][0]["check_ins"], ["2026-10-05"])

    def test_streak_resets_after_missed_day(self):
        shutil.copy(os.path.join(FIXTURES, "streak_cases.json"), self.data)
        s = self.start("2026-10-05")
        expected = {"gap": 1, "unbroken": 5, "yesterday": 3, "stale": 0}
        for hid, want in expected.items():
            with self.subTest(habit=hid):
                code, st = s.call("GET", f"/habits/{hid}/streak")
                self.assertEqual(code, 200)
                self.assertEqual(st["streak"], want)

    def test_missed_day_live_reset(self):
        # Same rule, driven through check-ins across real server restarts with new "today".
        hid = self.start("2026-10-01").call("POST", "/habits", {"name": "Run"})[1]["habit_id"]
        for day in ["2026-10-01", "2026-10-02"]:
            s = self.start(day); s.call("POST", f"/habits/{hid}/check-in"); s.kill()
        self.assertEqual(self.start("2026-10-02").call("GET", f"/habits/{hid}/streak")[1]["streak"], 2)
        # skip 10-03; 10-04 has no check-in yet -> last is 2 days ago -> 0
        self.assertEqual(self.start("2026-10-04").call("GET", f"/habits/{hid}/streak")[1]["streak"], 0)
        s = self.start("2026-10-04"); s.call("POST", f"/habits/{hid}/check-in")
        self.assertEqual(s.call("GET", f"/habits/{hid}/streak")[1]["streak"], 1)

    def test_data_persists_across_restart(self):
        s1 = self.start("2026-10-05")
        hid = s1.call("POST", "/habits", {"name": "Meditate"})[1]["habit_id"]
        s1.call("POST", f"/habits/{hid}/check-in")
        s1.kill()
        self.assertIsNotNone(s1.proc.returncode)
        s2 = self.start("2026-10-05")
        self.assertNotEqual(s1.proc.pid, s2.proc.pid)
        code, st = s2.call("GET", f"/habits/{hid}/streak")
        self.assertEqual(code, 200)
        self.assertEqual(st["check_ins"], ["2026-10-05"])
        self.assertEqual(st["streak"], 1)
        self.assertEqual(s2.call("POST", f"/habits/{hid}/check-in")[0], 409)
        with open(self.data) as f:
            self.assertEqual(set(json.load(f)["habits"][0]), {"habit_id", "name", "created_at", "check_ins"})


if __name__ == "__main__":
    unittest.main()
