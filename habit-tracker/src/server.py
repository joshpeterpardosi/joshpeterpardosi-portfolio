"""Habit tracker HTTP server. Python 3 stdlib only.

Env: HABIT_DATA_FILE (JSON path, default ./habits.json),
     HABIT_TODAY (ISO date override for "today"; default = real local date).
Usage: python server.py [port]   (default 8000)
"""
import datetime, json, os, re, sys, tempfile, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DATA_FILE = os.environ.get("HABIT_DATA_FILE", "habits.json")


def today():
    t = os.environ.get("HABIT_TODAY")
    return datetime.date.fromisoformat(t) if t else datetime.date.today()


def load():
    if not os.path.exists(DATA_FILE):
        return {"habits": []}
    with open(DATA_FILE) as f:
        return json.load(f)


def save(data):
    d = os.path.dirname(os.path.abspath(DATA_FILE))
    fd, tmp = tempfile.mkstemp(dir=d)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, DATA_FILE)  # atomic: no half-written file on kill


def streak(check_ins, now):
    """Consecutive days ending today or yesterday; 0 if last check-in is older."""
    days = {datetime.date.fromisoformat(d) for d in check_ins}
    cur = now if now in days else now - datetime.timedelta(days=1)
    n = 0
    while cur in days:
        n += 1
        cur -= datetime.timedelta(days=1)
    return n


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def find(self, data, hid):
        return next((h for h in data["habits"] if h["habit_id"] == hid), None)

    def do_POST(self):
        data = load()
        if self.path == "/habits":
            try:
                n = int(self.headers.get("Content-Length", 0))
                name = json.loads(self.rfile.read(n) or b"{}").get("name")
            except (ValueError, AttributeError):
                return self.send(400, {"error": "invalid JSON"})
            if not isinstance(name, str) or not name.strip():
                return self.send(400, {"error": "name required"})
            h = {"habit_id": uuid.uuid4().hex, "name": name.strip(),
                 "created_at": today().isoformat(), "check_ins": []}
            data["habits"].append(h)
            save(data)
            return self.send(201, h)
        m = re.fullmatch(r"/habits/([^/]+)/check-in", self.path)
        if m:
            h = self.find(data, m.group(1))
            if not h:
                return self.send(404, {"error": "habit not found"})
            t = today().isoformat()
            if t in h["check_ins"]:
                return self.send(409, {"error": "already checked in today", "habit": h})
            h["check_ins"].append(t)
            save(data)
            return self.send(201, h)
        self.send(404, {"error": "not found"})

    def do_GET(self):
        m = re.fullmatch(r"/habits/([^/]+)/streak", self.path)
        if not m:
            return self.send(404, {"error": "not found"})
        h = self.find(load(), m.group(1))
        if not h:
            return self.send(404, {"error": "habit not found"})
        self.send(200, {"habit_id": h["habit_id"], "streak": streak(h["check_ins"], today()),
                        "check_ins": h["check_ins"]})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"READY {port}", flush=True)
    srv.serve_forever()
