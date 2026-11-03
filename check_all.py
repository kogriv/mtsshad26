"""Прогоняет все решения задачи 2 на официальных полях и на моих вариантах полей.

    python check_all.py          таблица результатов
    python check_all.py --draw   то же плюс схемы всех полей
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import robot  # noqa: E402
SOLUTIONS = {
    "эталон авторов": "solutions/reference_authors.kum",
    "мой ответ": "solutions/ours_submitted.kum",
    "мой первый вариант": "solutions/ours_first_attempt.kum",
}
SETS = {"официальные тесты": "tests/official_fields.json", "мои варианты": "tests/variants.json"}

draw = "--draw" in sys.argv
for set_name, path in SETS.items():
    fields = json.loads((HERE / path).read_text(encoding="utf-8"))
    print(f"\n=== {set_name} ===")
    for sol_name, sol_path in SOLUTIONS.items():
        src = (HERE / sol_path).read_text(encoding="utf-8")
        marks = []
        for f in fields:
            paint_ok, base_ok, err, _ = robot.check(src, f)
            marks.append("✔" if paint_ok and base_ok and not err else "✘")
        print(f"{sol_name:22} {' '.join(marks)}   {marks.count('✔')} из {len(marks)}")
    if draw:
        ref = (HERE / SOLUTIONS["эталон авторов"]).read_text(encoding="utf-8")
        for f in fields:
            _, base_ok, _, stop = robot.check(ref, f)
            print(f"\n{f['name']} (x показывает, где остановился эталон, если не на базе)")
            print(robot.draw(f, None if base_ok else stop))
