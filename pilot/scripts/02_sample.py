"""Seeded sampling (seed 42) from saved frames. Run before inspecting any case text."""
import csv, random, json
from common import ROOT, CONFIG

SEED, N = CONFIG["random_seed"], CONFIG["sample_size_per_source"]


def read(p):
    with open(ROOT / "sampling_frames" / p, encoding="utf8") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with open(ROOT / "samples" / name, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def simple(frame):
    rng = random.Random(SEED)
    idx = sorted(rng.sample(range(len(frame)), min(N, len(frame))))
    return [frame[i] for i in idx]


def stratified(frame, key):
    rng = random.Random(SEED)
    groups = {}
    for r in frame:
        groups.setdefault(r[key], []).append(r)
    total = len(frame)
    quota = {g: N * len(v) / total for g, v in groups.items()}
    alloc = {g: int(q) for g, q in quota.items()}
    rest = N - sum(alloc.values())
    for g in sorted(groups, key=lambda g: quota[g] - alloc[g], reverse=True)[:rest]:
        alloc[g] += 1
    out = []
    for g in sorted(groups):
        out += rng.sample(groups[g], alloc[g])
    return out


if __name__ == "__main__":
    write("gitlab_sample.csv", simple(read("gitlab_frame.csv")))
    write("wikimedia_sample.csv", simple(read("wikimedia_frame.csv")))
    m = stratified(read("mantis_frame.csv"), "domain")
    write("mantis_sample.csv", m)
    print({d: sum(1 for r in m if r["domain"] == d) for d in CONFIG["mantis"]["domains"]})
