# -*- coding: utf-8 -*-
"""Dựng danh sách cổng push theo ĐÚNG bốn nhóm loại trừ ghi ở đầu run_gate.py."""
import os, re, sys

D = r"c:\Users\ADMIN\OneDrive\Desktop\astroq\AstroQhtml\scratchpad"

SKIP_PREFIX = ("test_", "verify_", "perf_", "gen_", "split_", "make_", "stamp_", "set_",
               "bundle_", "pha_", "_", "sync_font_preload", "run_gate")
SKIP_EXACT = {
    "e2e_certificate", "e2e_char_login", "probe_char_e2e", "probe_visit_beacon",
    "probe_engaged_beacon", "probe_register_now", "probe_activate_now",
    "e2e_quizlv_login", "e2e_tree_stamp", "test_login_hash", "verify_live_waitlist",
    "probe_public", "measure_shell", "gap_lv", "probe_earth_flat",
    "probe_flat_dark", "probe_flat_framing", "probe_field_space",
    "probe_field_pixels", "probe_warp_longtask", "probe_warp_frames",
    "gatelist", "smoke_waitlist", "probe_step1_new", "shot_pages",
    "grant_starter_bonus", "read_logs", "patch_util", "fetch_srcs",
    "setlv", "do_byte_trang", "do_byte_dot1", "rebalance_answers",
    "add_lv_gap_questions", "check_artifact_0819", "check_artifact_0905",
    "diff_artifact_0819", "check_mail_events", "check_meta_capi",
    "e2e_login_notactivated", "measure_corpus",

    "vendor_deps", "proto-solar-map", "solar-system-simulation",
}

names = []
for f in sorted(os.listdir(D)):
    if not f.endswith(".py"):
        continue
    n = f[:-3]
    if n in SKIP_EXACT:
        continue
    if n.startswith(SKIP_PREFIX):
        continue
    if n.startswith("shot_") or n.startswith("sim_") or n.startswith("preview"):
        continue
    names.append(n)

half = (len(names) + 1) // 2
print("TONG:", len(names))
print("A=" + " ".join(names[:half]))
print("B=" + " ".join(names[half:]))
