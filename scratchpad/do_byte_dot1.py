# -*- coding: utf-8 -*-
r"""Do xem bao nhieu byte cua bank la SIEU DU LIEU KIEM CHUNG (khong ai doc luc chay).

⚠️ Viet thanh FILE chu khong chay qua heredoc — heredoc cua shell an mat dau `\`
   trong regex va cho ra "unterminated character set". Bai hoc da ghi trong
   CLAUDE.md; trong phien 06/08/2026 toi mac lai BA lan truoc khi chiu tach file.
"""
import gzip
import io
import re

S = io.open("js/quiz-questions.js", encoding="utf-8").read()
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

print("\n=== MOT LUOT CHOI DUNG BAO NHIEU PHAN CUA BANK? ===")
n = len(re.findall(r'\n    \{\s*\n\s*term:\s*"', S))
print(f"  bank {n} cau · mot luot ROUND_SIZE=5 -> dung {5/n*100:.0f}%, "
      f"tai ve 100% ({GOC/1024:.1f} KB gzip)")
