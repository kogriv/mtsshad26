"""Переводит поле из tests/*.json в файл поля Робота .fil для песочницы qumir.dev.

Формат .fil: первая строка размер (ширина высота), вторая позиция робота (с единицы),
дальше строки клеток: x y стены цвет радиация температура символ символ1 точка.
Стены задаются маской: 1 север, 2 юг, 4 запад, 8 восток.
"""
def to_fil(field):
    NC, NR = field["NC"], field["NR"]
    hw = set(map(tuple, field["hwalls"])); vw = set(map(tuple, field["vwalls"]))
    dots = set(map(tuple, field["dots"])); base = tuple(field["base"])
    lines = ["; " + field.get("name", "поле"), f"{NC} {NR}", f"{field['robot'][0] + 1} {field['robot'][1] + 1}"]
    for y in range(NR):
        for x in range(NC):
            mask = 0
            if y > 0 and (x, y - 1) in hw: mask |= 1
            if y < NR - 1 and (x, y) in hw: mask |= 2
            if x > 0 and (x - 1, y) in vw: mask |= 4
            if x < NC - 1 and (x, y) in vw: mask |= 8
            sym = "Б" if (x, y) == base else "$"
            point = 1 if (x, y) in dots else 0
            if mask or sym != "$" or point:
                lines.append(f"{x + 1} {y + 1} {mask} 0 0 0 {sym} $ {point}")
    return "\n".join(lines) + "\n"
