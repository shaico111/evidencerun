"""Pure, unit-testable temporal reconstruction + anti-leakage rules for Stack Exchange threads.

Cutoff policy (conservative): effective cutoff = min(first published answer time,
earliest question-comment that already discloses the accepted solution).
Every evidence unit must have timestamp STRICTLY BEFORE the cutoff.
Equal / missing / malformed timestamps -> abstain (unit rejected, reason logged).
"""
import re
from datetime import datetime

# PostHistoryTypeId values (public dump schema)
H_INIT_TITLE, H_INIT_BODY, H_INIT_TAGS = 1, 2, 3
H_EDIT_TITLE, H_EDIT_BODY, H_EDIT_TAGS = 4, 5, 6
H_ROLLBACK_TITLE, H_ROLLBACK_BODY, H_ROLLBACK_TAGS = 7, 8, 9
BODY_TYPES = {H_INIT_BODY, H_EDIT_BODY, H_ROLLBACK_BODY}

RESOLUTION_RE = re.compile(
    r"\b(solv(?:es?|ed)|fix(?:es|ed)|that (?:worked|did it|fixed)|it works now|works now|now (?:it )?works|"
    r"problem (?:is )?(?:solved|gone)|resolved|figured (?:it )?out|found (?:the )?(?:solution|fix|answer)|"
    r"the (?:solution|answer|fix) (?:was|is)|thanks?[ ,!.]*(?:it )?work)", re.I)
THANKS_RE = re.compile(r"^\W*(thanks?|thank you|thx|cheers|ok|okay|great|nice|awesome|yes|no)\b\W*$", re.I)
TOKEN_RE = re.compile(r"[A-Za-z0-9_./\\:+\-=@#$%]{2,}")
MIN_NEW_FACT_TOKENS = 10
# a comment counts as an observation only if it shows evidence of a concrete observed fact
OBS_MARKER_RE = re.compile(r"(\d|[/\=$]|\b(error|output|says?|tried|try|running|ran|installed|version|"
                           r"message|warning|fails?|failed|crash\w*|boot\w*|happens?|started|stopped)\b)", re.I)
REQUEST_RE = re.compile(r"\b((can|could|would) you|please|any ideas|anyone know|how (?:do|can|to)|what do you mean|hoping|elaborate)\b", re.I)
HARD_FACT_RE = re.compile(r"(\d|[/\=$])")


def parse_ts(s):
    """ISO timestamp -> datetime or None (malformed => None => abstain)."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


_TAG_RE = re.compile(r"<[^>]+>")
_PRE_RE = re.compile(r"<pre[^>]*>.*?</pre>", re.S | re.I)


def html_to_text(html):
    import html as _h
    t = html or ""
    t = re.sub(r"</?(p|br|li|ul|ol|h\d|blockquote)[^>]*>", "\n", t, flags=re.I)
    t = _TAG_RE.sub("", t)
    return _h.unescape(t).strip()


def tokens(text):
    out = []
    for t in TOKEN_RE.findall(text or ""):
        t = t.lower().strip(".,:;()-=_/\\")
        if len(t) >= 2:
            out.append(t)
    return out


def shingles(text, n=4):
    tk = tokens(text)
    return {" ".join(tk[i:i + n]) for i in range(len(tk) - n + 1)}


def added_tokens(prev_text, new_text):
    """Content tokens in new_text that were not present in prev_text (bag-of-types)."""
    prev = set(tokens(prev_text))
    return [t for t in tokens(new_text) if t not in prev]


def novel_added_text(prev_text, new_text):
    """Lines of new_text not present in prev_text (line-level diff; formatting-only edits yield '')."""
    prev_lines = {re.sub(r"\s+", " ", l).strip() for l in (prev_text or "").splitlines()}
    out = [l for l in (new_text or "").splitlines()
           if re.sub(r"\s+", " ", l).strip() and re.sub(r"\s+", " ", l).strip() not in prev_lines]
    return "\n".join(out)


def solution_overlap(text, answer_text, exclude_text=""):
    """# of distinctive 4-gram shingles of `text` that also appear in the accepted answer
    and not in the already-legitimate question context (exclude_text)."""
    s = shingles(text) & shingles(answer_text)
    return len(s - shingles(exclude_text))


def build_thread_states(q, history, comments, answers, accepted_id):
    """Reconstruct pre-cutoff information states for one thread.

    q: dict(id, owner, created, title)
    history: list of dict(type, created, user, text, revision_guid)   (question PostHistory rows)
    comments: list of dict(id, created, user, text)                   (question comments only)
    answers: list of dict(id, created, body)                          (all answers)
    accepted_id: int or None
    Returns dict with cutoff, reasons, units, n_states, rejected (list of (unit, reason)).
    """
    out = dict(question_id=q["id"], reasons=[], units=[], rejected=[], n_states=0,
               cutoff=None, cutoff_reason=None, early_text=None, later_text=None, advanced_text=None,
               leakage="none", leakage_detail="")
    acc = next((a for a in answers if a["id"] == accepted_id), None)
    if acc is None:
        out["reasons"].append("accepted_answer_not_in_dump")
        return out
    ans_ts = [(parse_ts(a["created"]), a) for a in answers]
    ans_ts = [(t, a) for t, a in ans_ts if t is not None]
    if not ans_ts:
        out["reasons"].append("no_valid_answer_timestamp")
        return out
    first_ans_t = min(t for t, _ in ans_ts)
    cutoff, cutoff_reason = first_ans_t, "first_answer"
    acc_text = html_to_text(acc.get("body", ""))
    qt0 = parse_ts(q["created"])
    if qt0 is None:
        out["reasons"].append("question_timestamp_invalid")
        return out
    # reconstruct initial body from history (never final body)
    body_rev = sorted(
        [h for h in history if h["type"] in BODY_TYPES and parse_ts(h["created"]) is not None],
        key=lambda h: (parse_ts(h["created"]), h.get("order", 0)))
    inits = [h for h in body_rev if h["type"] == H_INIT_BODY]
    if not inits:
        out["reasons"].append("no_initial_body_in_history")
        return out
    init = inits[0]
    early_body = html_to_text(init["text"])
    early_title = ""
    for h in sorted(history, key=lambda h: parse_ts(h["created"]) or datetime.max):
        if h["type"] == H_INIT_TITLE:
            early_title = (h["text"] or "").strip()
            break
    early_title = early_title or q.get("title", "")
    if parse_ts(init["created"]) is None or parse_ts(init["created"]) >= cutoff:
        out["reasons"].append("initial_version_not_before_cutoff")
        return out
    # earlier solution disclosure in a non-OP question comment moves cutoff earlier
    for c in sorted(comments, key=lambda c: parse_ts(c["created"]) or datetime.max):
        ct = parse_ts(c["created"])
        if ct is None or ct >= cutoff or c["user"] == q["owner"]:
            continue
        if solution_overlap(c["text"], acc_text, early_body) >= 2:
            cutoff, cutoff_reason = ct, "comment_discloses_solution"
            out["leakage"], out["leakage_detail"] = "suspected", f"comment {c['id']} overlaps accepted answer"
            break
    out["cutoff"], out["cutoff_reason"] = cutoff, cutoff_reason
    if parse_ts(init["created"]) >= cutoff:
        out["reasons"].append("initial_version_not_before_cutoff")
        return out

    # candidate evidence units after the initial version, strictly before cutoff
    units = []
    for h in body_rev:
        if h is init:
            continue
        ht = parse_ts(h["created"])
        if ht >= cutoff:
            if ht == cutoff:
                out["rejected"].append((("edit", h.get("revision_guid")), "equal_timestamp_abstain"))
            continue
        units.append(dict(kind="edit", id=h.get("revision_guid"), t=ht, user=h["user"],
                          text=html_to_text(h["text"]), by_owner=(h["user"] == q["owner"])))
    for c in comments:
        ct = parse_ts(c["created"])
        if ct is None:
            out["rejected"].append((("comment", c["id"]), "malformed_timestamp"))
            continue
        if ct >= cutoff:
            if ct == cutoff:
                out["rejected"].append((("comment", c["id"]), "equal_timestamp_abstain"))
            continue
        units.append(dict(kind="comment", id=c["id"], t=ct, user=c["user"], text=c["text"],
                          by_owner=(c["user"] == q["owner"])))
    units.sort(key=lambda u: (u["t"], str(u["id"])))

    # walk the timeline, keeping the running OP-visible text
    running = early_body
    seen_tokens = set(tokens(early_title + " " + early_body))
    states = []  # accepted new-fact units
    prev_edit_text = early_body
    for u in units:
        uid = (u["kind"], u["id"])
        if u["kind"] == "comment" and not u["by_owner"]:
            out["rejected"].append((uid, "non_owner_comment_not_symptom"))  # a question/conjecture, not an observation
            continue
        if u["kind"] == "edit" and not u["by_owner"]:
            out["rejected"].append((uid, "edit_by_non_owner"))
            continue
        if u["t"] <= qt0:
            out["rejected"].append((uid, "not_after_question_creation"))
            continue
        if u["kind"] == "edit":
            new_text = novel_added_text(prev_edit_text, u["text"])
            prev_edit_text = u["text"]
        else:
            new_text = u["text"]
        long_paste = len(tokens(new_text)) >= 40
        probe = re.sub(r"@\w+", " ", new_text)  # usernames such as @user123 must not count as digits/facts
        if not long_paste and not OBS_MARKER_RE.search(probe):
            out["rejected"].append((uid, "no_observation_marker"))
            continue
        if not long_paste and REQUEST_RE.search(probe) and not HARD_FACT_RE.search(probe):
            out["rejected"].append((uid, "request_not_observation"))
            continue
        if THANKS_RE.match(new_text.strip() or "x"):
            out["rejected"].append((uid, "thanks_or_ack"))
            continue
        new_tok = [t for t in tokens(new_text) if t not in seen_tokens]
        if len(new_tok) < MIN_NEW_FACT_TOKENS:
            out["rejected"].append((uid, f"too_few_new_tokens({len(new_tok)})"))
            continue
        if RESOLUTION_RE.search(new_text):
            out["rejected"].append((uid, "resolution_claim"))
            out["leakage"] = "suspected" if out["leakage"] == "none" else out["leakage"]
            out["leakage_detail"] += f" resolution_claim in {uid};"
            continue
        ov = solution_overlap(new_text, acc_text, early_body)
        if ov >= 3:
            out["rejected"].append((uid, f"solution_overlap({ov})"))
            out["leakage"] = "suspected"
            out["leakage_detail"] += f" overlap_with_accepted({ov}) in {uid};"
            continue
        seen_tokens.update(tokens(new_text))
        states.append(dict(u, new_text=new_text, n_new_tokens=len(new_tok)))
        out["units"].append(dict(kind=u["kind"], id=u["id"], t=u["t"].isoformat(), n_new_tokens=len(new_tok),
                                 text=new_text[:500]))
    out["n_states"] = 1 + len(states)
    out["early_text"] = (early_title + "\n" + early_body).strip()
    if states:
        out["later_text"] = out["early_text"] + "\n" + states[0]["new_text"]
    if len(states) >= 2:
        out["advanced_text"] = out["later_text"] + "\n" + states[1]["new_text"]
    return out
