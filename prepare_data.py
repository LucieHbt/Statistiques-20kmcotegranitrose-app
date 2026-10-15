"""Transforme les fichiers .xlsx (une feuille = une édition) en format long.

Usage :
    python prepare_data.py [results_10km.xlsx] [results_20km.xlsx]

Colonnes attendues dans chaque feuille (format du scraping) :
    Place; Dossard; Nom; Place Cat.; Equipe / Club; Temps Officiel (Réel);
    Écart; TpsOff; TpsReel; Nat.
"""
import datetime as dt
import os
import re
import sys

import pandas as pd

src10km = sys.argv[1] if len(sys.argv) > 1 else "data/results_10km.xlsx"
src20km = sys.argv[2] if len(sys.argv) > 2 else "data/results_20km.xlsx"

SOURCES = {"10km": src10km, "20km": src20km}

# "NOM Prénom H - SH" -> nom, sexe, catégorie (la catégorie peut être vide)
NOM_RE = re.compile(r"^(.*?)\s+([HF])\s+-\s*(.*)$")


def to_seconds(v):
    if isinstance(v, (dt.time, dt.datetime)):
        return v.hour * 3600 + v.minute * 60 + v.second
    if isinstance(v, dt.timedelta):
        return v.total_seconds()
    if isinstance(v, float) and 0 < v < 1:  # durée stockée par Excel en fraction de jour
        return round(v * 86400)
    if isinstance(v, str):
        p = v.strip().split(":")
        if len(p) == 3 and all(q.isdigit() for q in p):
            return int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
    return float("nan")  # DNF, vide...


def clean_header(c):
    return str(c).replace("\xa0", " ").strip()


def clean_text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return re.sub(r"\s+", " ", str(v).replace("\xa0", " ")).strip()


def get(d, *names):
    """Première colonne trouvée parmi `names`, sinon une série vide (NaN)."""
    for n in names:
        if n in d.columns:
            return d[n]
    return pd.Series([float("nan")] * len(d), index=d.index)


def text(s):
    return (
        s.astype("string").str.replace("\xa0", " ", regex=False).str.strip().fillna("")
    )


def num(s):
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def split_nom(v):
    """'CARO Florian    H  -   SH' -> ('CARO Florian', 'H', 'SH')."""
    s = clean_text(v)
    m = NOM_RE.match(s)
    if m:
        return m.group(1).strip(), m.group(2), m.group(3).strip()
    return s, "", ""


def year_of(sheet):
    m = re.search(r"\d{4}", str(sheet))
    if not m:
        raise ValueError(f"Nom de feuille sans année : {sheet!r}")
    return int(m.group())


frames = []
for course, src in SOURCES.items():
    if not os.path.exists(src):
        print(f"Fichier introuvable, ignoré : {src}")
        continue
    x = pd.ExcelFile(src)
    for sheet in x.sheet_names:
        d = x.parse(sheet)
        d.columns = [clean_header(c) for c in d.columns]

        # Nom / sexe / catégorie extraits de la colonne "Nom" (sauf si colonnes dédiées)
        parts = get(d, "Nom").map(split_nom)
        nom = parts.map(lambda t: t[0]).astype("string")
        sexe_p = parts.map(lambda t: t[1]).astype("string")
        cat_p = parts.map(lambda t: t[2]).astype("string")

        sexe = text(get(d, "Sexe"))
        sexe = sexe.where(sexe != "", sexe_p)
        cat = text(get(d, "Catégorie", "Cat"))
        cat = cat.where(cat != "", cat_p)

        out = pd.DataFrame({
            "Annee": year_of(sheet),
            "Course": course,
            "Dossard": num(get(d, "Dossard")),
            "Place": num(get(d, "Place")),
            "Nom": nom,  # format NOM Prénom
            "Sexe": sexe,
            "Club": text(get(d, "Equipe / Club", "Club")),
            "Catégorie": cat,
            "Classement_Cat": num(get(d, "Place Cat.", "Classement Catégorie")),
            "Nat": text(get(d, "Nat.", "Nat")),
            "Temps_s": get(d, "TpsOff", "Temps Officiel").map(to_seconds),
            "Temps_reel_s": get(d, "TpsReel", "Temps Réel").map(to_seconds),
        })
        frames.append(out)

if not frames:
    raise SystemExit("Aucun fichier source trouvé.")

df = pd.concat(frames, ignore_index=True)
os.makedirs("data", exist_ok=True)
df.to_csv("data/resultats.csv", index=False)
print(
    df.groupby(["Course", "Annee"]).agg(
        coureurs=("Nom", "size"), arrivants=("Temps_s", "count")
    )
)