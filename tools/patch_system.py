"""Патчит исходники ZealOS для TempleOS 2026 и кладёт результат в theme/Sys."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "src"
OUT = ROOT / "theme" / "Sys"
OUT.mkdir(parents=True, exist_ok=True)


def patch(rel, subs, out_name, prefix=""):
    text = (SRC / rel).read_text(encoding="utf-8", errors="surrogateescape")
    for old, new, count in subs:
        n = text.count(old)
        assert n == count, f"{rel}: {old!r} found {n}, expected {count}"
        text = text.replace(old, new)
    (OUT / out_name).write_text(prefix + text, encoding="utf-8", errors="surrogateescape", newline="")


# 1. Хук 32-битного компоновщика: если тема загружена, она рисует кадр сама.
patch("System/Gr/GrScreen.ZC", [
    ("U0 GrUpdateScreen()\n{",
     "public U0 (*fp_theme_update32)();\nfp_theme_update32 = NULL;\n\nU0 GrUpdateScreen()\n{", 1),
    ("\tDCBlotColor4(gr.dc1->body, gr.dc2->body, gr.dc_cache->body, GR_HEIGHT * GR_WIDTH >> 3);\n\tGrUpdateScreen32;\n",
     "\tDCBlotColor4(gr.dc1->body, gr.dc2->body, gr.dc_cache->body, GR_HEIGHT * GR_WIDTH >> 3);\n"
     "\tif (fp_theme_update32 && gr.screen_zoom == 1)\n\t{\n"
     "\t\ttry\n\t\t\t(*fp_theme_update32)();\n"
     "\t\tcatch\n\t\t{\n\t\t\tfp_theme_update32 = NULL;\n\t\t\tFs->catch_except = TRUE;\n\t\t\tLFBFlush;\n\t\t}\n\t}\n"
     "\telse\n\t\tGrUpdateScreen32;\n", 1),
], "GrScreen.ZC")

# 2. Окна не залезают под верхнюю панель (строки 0-3) и док (нижние строки).
WT, WB, WL = "WIN_TOP_ROW", "WIN_BOT_ROWS", "WIN_SIDE_COLS"
patch("System/Win.ZC", [
    ("2 - no_border", f"{WT} - no_border", 4),
    ("TEXT_ROWS - 2 + no_border", f"TEXT_ROWS - {WB} + no_border", 3),
    ("TEXT_ROWS - 2,", f"TEXT_ROWS - {WB},", 2),
    ("(TEXT_ROWS - 1) / c", f"(TEXT_ROWS - {WB} - {WT} + 1) / c", 2),
    ("1 - no_border, TEXT_COLS - 2 + no_border", f"{WL} - no_border, TEXT_COLS - {WL} - 1 + no_border", 3),
    ("TEXT_COLS - 2, ", f"TEXT_COLS - {WL} - 1, ", 2),
    ("horz_size + 1 - no_border, (i & 3 + 1) * horz_size - 1 + no_border",
     f"horz_size + {WL} - no_border, (i & 3 + 1) * horz_size - 2 + no_border", 1),
    ("TEXT_ROWS / 2 + 1 - no_border", "TEXT_ROWS / 2 + 2 - no_border", 1),
], "Win.ZC", prefix=f"#define {WT}\t5\n#define {WB}\t12\n#define {WL}\t2\n\n")

# 3. Ядро стартует в 1920x1080 (если VBE не даст, само откатится на 1024x768).
patch("Kernel/KStart16.ZC", [
    ("REQUESTED_SCREEN_WIDTH:\t\tDU16\t1024;", "REQUESTED_SCREEN_WIDTH:\t\tDU16\t1920;", 1),
    ("REQUESTED_SCREEN_HEIGHT:\tDU16\t768;", "REQUESTED_SCREEN_HEIGHT:\tDU16\t1080;", 1),
], "KStart16.ZC")
print("ok")
