"""Создаёт ссылки на песочницу qumir.dev: эталон авторов вместе с файлом поля. Результат пишет в shares.json."""
import json, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent
code = (HERE.parent / "solutions" / "reference_authors.kum").read_text(encoding="utf-8")
fields = {"official_1": "official_1.fil", "A": "variant_A.fil", "B": "variant_B.fil", "V": "variant_V.fil"}
out = {}
for key, fil in fields.items():
    body = json.dumps({"code": code, "args": "", "stdin": "", "files": {"field.fil": (HERE / fil).read_text(encoding="utf-8")}}).encode()
    req = urllib.request.Request("https://qumir.dev/api/share", data=body, headers={"Content-Type": "application/json"}, method="POST")
    out[key] = json.loads(urllib.request.urlopen(req, timeout=40).read())
    print(key, "https://qumir.dev/s/" + out[key]["id"])
(HERE / "shares.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
