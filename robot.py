"""Маленький симулятор Робота из КуМира.

Понимает ровно то, что нужно для задачи 2: команды вверх/вниз/влево/вправо/закрасить,
условия «сверху/снизу/слева/справа свободно|стена», «клетка чистая|закрашена», связки и/или/не,
циклы «нц пока … кц» и ветвления «если … то … иначе … все». Комментарии после «|» пропускаются.

Поле: NC столбцов, NR рядов, клетки (столбец, ряд) с нуля от левого верхнего угла.
hwalls задаёт стены ПОД клеткой (c, r), vwalls задаёт стены СПРАВА от клетки (c, r). Края поля тоже считаются стенами.
"""
import re

class Crash(Exception):
    pass

DIRS = {"вверх": (0, -1), "вниз": (0, 1), "влево": (-1, 0), "вправо": (1, 0)}
SIDE = {"сверху": "вверх", "снизу": "вниз", "слева": "влево", "справа": "вправо"}

class Field:
    def __init__(self, f):
        self.NC, self.NR = f["NC"], f["NR"]
        self.hw = set(map(tuple, f["hwalls"]))
        self.vw = set(map(tuple, f["vwalls"]))
        self.x, self.y = f["robot"]
        self.painted = set()
        self.steps = 0

    def wall(self, d):
        x, y = self.x, self.y
        return {"вверх": y == 0 or (x, y - 1) in self.hw,
                "вниз": y == self.NR - 1 or (x, y) in self.hw,
                "влево": x == 0 or (x - 1, y) in self.vw,
                "вправо": x == self.NC - 1 or (x, y) in self.vw}[d]

    def move(self, d):
        if self.wall(d):
            raise Crash(f"удар о стену: {d} из клетки {(self.x, self.y)}")
        dx, dy = DIRS[d]
        self.x += dx; self.y += dy; self.steps += 1
        if self.steps > 100000:
            raise Crash("робот ходит по кругу")

def _cond(f, text):
    def atom(a):
        a = a.strip(); neg = a.startswith("не ")
        if neg: a = a[3:].strip()
        m = re.fullmatch(r"(сверху|снизу|слева|справа) (свободно|стена)", a)
        if m: v = f.wall(SIDE[m.group(1)]) == (m.group(2) == "стена")
        elif a == "клетка закрашена": v = (f.x, f.y) in f.painted
        elif a == "клетка чистая": v = (f.x, f.y) not in f.painted
        else: raise ValueError("непонятное условие: " + a)
        return not v if neg else v
    return any(all(atom(a) for a in part.split(" и ")) for part in text.split(" или "))

def parse(src):
    lines = [re.sub(r"\|.*", "", l).strip() for l in src.split("\n")]
    lines = [l for l in lines if l]
    i = lines.index("нач") + 1
    def block(stop):
        nonlocal i
        out = []
        while lines[i] not in stop:
            l = lines[i]
            if l.startswith("нц пока "):
                c = l[8:]; i += 1; body = block(("кц",)); i += 1; out.append(("while", c, body))
            elif l.startswith("если "):
                c = l[5:]; c = c[:-3].strip() if c.endswith(" то") else c; i += 1
                if lines[i] == "то": i += 1
                yes = block(("иначе", "все")); no = []
                if lines[i] == "иначе": i += 1; no = block(("все",))
                i += 1; out.append(("if", c, yes, no))
            else:
                out.append(("cmd", l)); i += 1
        return out
    return block(("кон",))

def run(prog, f):
    for st in prog:
        if st[0] == "cmd":
            if st[1] == "закрасить": f.painted.add((f.x, f.y))
            elif st[1] in DIRS: f.move(st[1])
            else: raise ValueError("непонятная команда: " + st[1])
        elif st[0] == "while":
            while _cond(f, st[1]): run(st[2], f)
        else:
            run(st[2] if _cond(f, st[1]) else st[3], f)

def check(src, field):
    """Возвращает (закраска верна, робот на базе, текст ошибки, где остановился)."""
    f = Field(field)
    try:
        run(parse(src), f); err = ""
    except Crash as e:
        err = str(e)
    return f.painted == set(map(tuple, field["dots"])), (f.x, f.y) == tuple(field["base"]), err, (f.x, f.y)

def draw(field, stop=None):
    """Рисует поле. Р старт, Б база, • отмеченная клетка, ━ и ┃ стенки, x место, где остановился робот."""
    hw = set(map(tuple, field["hwalls"])); vw = set(map(tuple, field["vwalls"]))
    dots = set(map(tuple, field["dots"])); base = tuple(field["base"]); start = tuple(field["robot"])
    NC, NR = field["NC"], field["NR"]
    rows = ["┌" + "───" * NC + "┐"]
    for r in range(NR):
        s = "│"
        for c in range(NC):
            if (c, r) == start: ch = "Р"
            elif (c, r) == base: ch = "Б"
            elif stop is not None and (c, r) == tuple(stop): ch = "x"
            elif (c, r) in dots: ch = "•"
            else: ch = " "
            s += " " + ch + ("┃" if c < NC - 1 and (c, r) in vw else " ")
        rows.append(s + "│")
        if r < NR - 1:
            rows.append("│" + "".join("━━━" if (c, r) in hw else "   " for c in range(NC)) + "│")
    rows.append("└" + "───" * NC + "┘")
    return "\n".join(rows)
