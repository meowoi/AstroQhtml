# -*- coding: utf-8 -*-
r"""Do xem bao nhieu byte cua bank la SIEU DU LIEU KIEM CHUNG (khong ai doc luc chay).

⚠️ Viet thanh FILE chu khong chay qua heredoc — heredoc cua shell an mat dau `\`
   trong regex va cho ra "unterminated character set". Bai hoc da ghi trong
   CLAUDE.md; trong phien 06/08/2026 toi mac lai BA lan truoc khi chiu tach file.
"""
import gzip
import io
import os
import re

# ⚠️ TRO LAI SANG HINH DANG MOI (07/08/2026): bank khong con la mot file
#    `js/quiz-questions.js` ma la `js/quiz-index.js` + mot file moi cau trong
#    `js/quiz/`. Chinh phep do cua script NAY la dau vao cho quyet dinh cat file,
#    nen giu no song thay vi bo — cau hoi "bao nhieu byte la sieu du lieu kiem
#    chung" con dung cho Dot 3-5, khi bank len ~870 cau.
QDIR = "js/quiz"
QFILES = sorted(f for f in os.listdir(QDIR) if f.endswith(".js"))
S = io.open("js/quiz-index.js", encoding="utf-8").read() + "\n" + "\n".join(
    io.open(os.path.join(QDIR, f), encoding="utf-8").read() for f in QFILES)
Q = io.open("quiz.html", encoding="utf-8").read()


def gz(t):
    return len(gzip.compress(t.encode("utf-8"), 9))


GOC = gz(S)
PAT = {
    "srcQuote":   r'\n\s*srcQuote:\s*"(?:[^"\\]|\\.)*",?',
    "srcChecked": r'\n\s*srcChecked:\s*"[^"]*",?',
    "lv":         r"\n\s*lv:\s*\d,?",
}

print("=== BAO NHIEU BYTE LA SIEU DU LIEU (khong ai doc luc chay)? ===")
for ten, pat in PAT.items():
    bot = re.sub(pat, "", S)
    print(f"  bo `{ten:11s}`: {(GOC - gz(bot)) / 1024:5.2f} KB gzip "
          f"({len(re.findall(pat, S))} cho)")
ca = S
for pat in PAT.values():
    ca = re.sub(pat, "", ca)
print(f"  bo CA BA        : {(GOC - gz(ca)) / 1024:5.2f} KB gzip  "
      f"/ tong bank {GOC / 1024:.1f} KB")

print("\n=== quiz.html co THAT SU can codex-terms.js khong? ===")
goi = re.findall(r"AstroQCodex\.\w+", Q)
print(f"  so lan goi AstroQCodex: {len(goi)}  {sorted(set(goi))}")
for m in list(re.finditer(r"AstroQCodex\.\w+", Q))[:4]:
    j = Q.rfind("\n", 0, m.start())
    print("   ", Q[j + 1:Q.find("\n", m.end())].strip()[:118])

print("\n=== MOT LUOT CHOI TAI BAO NHIEU PHAN CUA BANK? ===")
n = len(QFILES)
ix = gz(io.open("js/quiz-index.js", encoding="utf-8").read())
per = [gz(io.open(os.path.join(QDIR, f), encoding="utf-8").read()) for f in QFILES]
avg = sum(per) / len(per)
print(f"  bank {n} cau · mot luot ROUND_SIZE=5 -> dung {5/n*100:.0f}% cau hoi")
print(f"  va nay CHI TAI dung phan do: muc luc {ix/1024:.1f} KB + 5 file "
      f"{avg*5/1024:.1f} KB = {(ix+avg*5)/1024:.1f} KB gzip")
print(f"  (truoc 07/08/2026: tai ve 100% bank = {GOC/1024:.1f} KB gzip du dung 5%)")
print("  Con so day du + doi chieu: scratchpad/check_quiz_split.py muc [8]")
