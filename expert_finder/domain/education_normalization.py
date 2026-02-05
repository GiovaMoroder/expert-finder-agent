from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Optional

# -------------------- text normalization --------------------


def _clean(s: str) -> str:
    s = s.strip()
    s = s.replace("’", "'").replace("–", "-").replace("—", "-")
    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # keep letters/numbers and a few separators
    s = re.sub(r"[^\w\s\-\&\/.']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# -------------------- drop rules (high school etc.) --------------------

_DROP_PATTERNS: List[re.Pattern] = [
    # Italian secondary schools
    re.compile(r"\bliceo\b"),
    re.compile(r"\bistituto\b"),  # beware: may catch real universities in rare cases
    re.compile(r"\bitis\b"),
    re.compile(r"\biti\b"),
    re.compile(r"\bitt\b"),
    re.compile(r"\biis\b"),
    re.compile(r"\bscuola media\b"),
    re.compile(r"\bscuole\b"),

    # English secondary schools
    re.compile(r"\bhigh school\b"),
    re.compile(r"\bsecondary school\b"),
    re.compile(r"\bsixth form\b"),
    re.compile(r"\bcollege preparatory\b"),
    re.compile(r"\bgymnasium\b"),  # often secondary in EU lists

    # Pre-university curricula (treat as "not a school" for your purpose)
    re.compile(r"\binternational baccalaureate\b"),
    re.compile(r"\bib\b"),
    re.compile(r"\bigcse\b"),
    re.compile(r"\bgcse\b"),
    re.compile(r"\ba[- ]level\b"),
]


def _should_drop_school(cleaned: str) -> bool:
    return any(p.search(cleaned) for p in _DROP_PATTERNS)


# -------------------- alias mapping --------------------
# Canonical names -> aliases (few, on purpose).
# Add/edit freely as you see new variants in your data.

_CANONICAL_TO_ALIASES: Dict[str, List[str]] = {
    "Università di Pisa": ["universita di pisa", "università di pisa"],
    "Scuola Superiore Sant'Anna": ["scuola superiore sant anna", "sant'anna", "sant anna"],
    "Scuola Normale Superiore": ["scuola normale superiore", "sns"],

    "Politecnico di Milano": [
        "politecnico di milano", "polimi", "polimi graduate school of management", "polimi gsom",
        "alta scuola politecnica"  # if you prefer, keep ASP separate instead of folding it into PoliMi
    ],
    "Politecnico di Torino": ["politecnico di torino", "polito"],
    "Politecnico di Bari": ["politecnico di bari"],
    "Università di Bologna": [
        "universita di bologna",
        "alma mater studiorum universita di bologna",
        "alma mater studiorum – universita di bologna",
        "university of bologna"
    ],

    "Università Bocconi": ["universita bocconi", "università bocconi", "bocconi"],
    "SDA Bocconi School of Management": ["sda bocconi", "sda bocconi school of management"],
    "LUISS Guido Carli": ["luiss", "luiss guido carli", "luiss guido carli university"],

    "Sapienza Università di Roma": [
        "sapienza universita di roma", "sapienza", "universita di roma la sapienza",
        "dipartimento di scienze statistiche universita di roma la sapienza",
        "sapienza school for advanced studies"
    ],
    "Università degli Studi di Milano": ["universita degli studi di milano", "universita di milano", "unimi"],
    "Università di Milano-Bicocca": ["universita degli studi di milano-bicocca", "universita di milano bicocca", "unimib"],
    "Università degli Studi di Padova": [
        "universita degli studi di padova", "universita di padova", "unipd",
        "universita degli studi di padova unipd / university of padua", "universita degli studi di padova (unipd) / university of padua"
    ],
    "Università degli Studi di Torino": ["universita degli studi di torino", "universita di torino"],
    "Università Ca' Foscari Venezia": ["universita ca' foscari venezia", "universita ca foscari venezia", "ca' foscari", "ca foscari"],
    "Università Campus Bio-Medico di Roma": ["universita campus bio-medico di roma", "campus biomedico", "campus biomedico roma", "universita campus biomedico di roma"],
    "Università Cattolica del Sacro Cuore": ["universita cattolica del sacro cuore", "cattolica", "unicatt"],
    "Università degli Studi di Trento": ["universita di trento", "universita degli studi di trento", "unitrento", "unitrento disi"],
    "Università degli Studi di Pavia": ["universita di pavia", "universita degli studi di pavia", "unipv"],
    "Università degli Studi di Firenze": ["universita degli studi di firenze", "universita di firenze", "unifi"],
    "Università degli Studi di Napoli Federico II": [
        "universita degli studi di napoli federico ii", "universita di napoli federico ii",
        "unina", "apple developer academy unina federico ii"
    ],
    "Università della Svizzera italiana": ["usi universita della svizzera italiana", "universita della svizzera italiana", "usi"],
    "Università del Salento": ["universita del salento"],
    "Università della Calabria": ["universita della calabria", "unical"],
    "Università degli Studi di Genova": ["universita degli studi di genova", "university of genoa", "universita di genova"],
    "Università degli Studi di Verona": ["universita degli studi di verona", "universita di verona"],
    "Università Roma Tre": ["universita degli studi roma tre", "roma tre", "universita roma tre"],
    "Università di Roma Tor Vergata": ["university of rome tor vergata", "universita di roma tor vergata"],

    "ETH Zürich": ["eth zurich", "eth zürich", "eth"],
    "EPFL": ["epfl", "ecole polytechnique federale de lausanne", "ecole polytechnique federale de lausanne (epfl)"],
    "University of St. Gallen": ["university of st.gallen", "university of st gallen", "hsg", "st gallen"],
    "University of Zurich": ["university of zurich", "uzh"],
    "Technische Universität München": ["technical university of munich", "technische universitat munchen", "technische universität münchen", "tum", "tum school of management"],
    "RWTH Aachen University": ["rwth aachen university", "rwth aachen"],
    "Karlsruhe Institute of Technology": ["karlsruhe institute of technology", "kit"],
    "Technische Universität Wien": ["technische universitat wien", "technische universität wien", "tu wien"],
    "Technische Universität Berlin": ["technische universitat berlin", "technische universität berlin", "tu berlin"],
    "Technische Universität Darmstadt": ["technische universitat darmstadt", "technische universität darmstadt", "tu darmstadt"],
    "Technische Universiteit Delft": ["delft university of technology", "technische universiteit delft", "tu delft"],
    "DTU (Technical University of Denmark)": ["dtu", "technical university of denmark"],
    "KTH Royal Institute of Technology": ["kth royal institute of technology", "kth"],
    "Aalto University": ["aalto university"],
    "Chalmers University of Technology": ["chalmers university of technology"],
    "KU Leuven": ["ku leuven"],
    "Utrecht University": ["utrecht university"],
    "University of Amsterdam": ["university of amsterdam", "uva"],
    "Vrije Universiteit Amsterdam": ["vrije universiteit amsterdam", "vu amsterdam"],
    "Tilburg University": ["tilburg university"],
    "Eindhoven University of Technology": ["eindhoven university of technology", "tu eindhoven"],
    "Wageningen University & Research": ["wageningen university & research", "wageningen university and research", "wur"],
    "Lund University": ["lund university", "the faculty of engineering at lund university"],
    "Stockholm School of Economics": ["stockholm school of economics", "hhs"],
    "Stockholm University": ["stockholm university"],
    "Norwegian University of Science and Technology": ["norwegian university of science and technology", "ntnu"],
    "University of Oslo": ["university of oslo"],
    "University of Helsinki": ["university of helsinki"],
    "University of Bern": ["university of bern"],
    "University of Basel": ["university of basel"],
    "University of Luxembourg": ["university of luxembourg"],

    "Imperial College London": [
        "imperial college london", "department of earth science and engineering imperial college",
        "imperial college business school"
    ],
    "King's College London": ["king's college london", "kings college london"],
    "University College London": ["ucl", "university college london"],
    "The London School of Economics and Political Science": [
        "the london school of economics and political science", "lse", "london school of economics"
    ],
    "University of Cambridge": ["university of cambridge", "corpus christi college cambridge"],
    "University of Oxford": ["university of oxford"],
    "The University of Edinburgh": ["the university of edinburgh", "university of edinburgh"],
    "University of Glasgow": ["university of glasgow"],
    "University of Leeds": ["university of leeds"],
    "University of Liverpool": ["university of liverpool"],
    "University of Southampton": ["university of southampton"],
    "University of Warwick": ["university of warwick", "warwick business school", "university of warwick - warwick business school"],

    "Erasmus University Rotterdam": [
        "erasmus university rotterdam", "erasmus school of economics",
        "rotterdam school of management erasmus university"
    ],

    "Université Paris-Saclay": ["universite paris-saclay", "université paris-saclay"],
    "Université Paris Cité": ["universite paris cite", "université paris cité"],
    "Université Paris Dauphine - PSL": ["universite paris dauphine - psl", "université paris dauphine - psl"],
    "Sorbonne Université": ["sorbonne universite", "sorbonne université", "pierre and marie curie university"],
    "École Polytechnique": ["ecole polytechnique", "école polytechnique"],
    "CentraleSupélec": ["centralesupelec", "centrale supelec", "centralesupélec"],
    "Télécom Paris": ["telecom paris", "télécom paris"],
    "INSA Lyon": ["insa lyon", "institut national des sciences appliquees de lyon", "institut national des sciences appliquées de lyon"],
    "ESILV": ["esilv", "ecole superieure d'ingenieurs leonard de vinci"],
    "École normale supérieure de Lyon": ["ecole normale superieure de lyon", "école normale supérieure de lyon"],
    "Mines Paris - PSL": ["mines paris - psl", "mines paris"],

    "ESADE": ["esade", "esade business school"],
    "IESE Business School": ["iese business school", "iese"],
    "ESCP Business School": ["escp business school", "escp"],
    "ESSEC Business School": ["essec business school", "essec"],
    "INSEAD": ["insead"],
    "HEC Paris": ["hec paris"],
    "emlyon business school": ["emlyon business school", "emlyon"],

    "Peking University": ["peking university", "beida"],
    "Tsinghua University": ["tsinghua university"],
    "Shanghai Jiao Tong University": ["shanghai jiao tong university", "sjtu"],
    "Tongji University": ["tongji university"],
    "Renmin University of China": ["renmin university of china"],
    "KAUST": ["kaust", "king abdullah university of science and technology"],
    "National University of Singapore": ["national university of singapore", "nus"],
    "Nanyang Technological University": ["nanyang technological university singapore", "nanyang technological university", "ntu singapore"],
    "City University of Hong Kong": ["city university of hong kong", "cityu"],
    "The Hong Kong University of Science and Technology": ["the hong kong university of science and technology", "hkust"],
    "The Hong Kong Polytechnic University": ["the hong kong polytechnic university", "polyu"],
    "Yonsei University": ["yonsei university"],
    "Keio University": ["keio university"],

    "Harvard University": ["harvard university"],
    "Harvard Business School": ["harvard business school"],
    "Harvard Medical School": ["harvard medical school"],
    "Massachusetts Institute of Technology": ["massachusetts institute of technology", "mit"],
    "Stanford University": ["stanford university"],
    "California Institute of Technology": ["caltech", "california institute of technology"],
    "Princeton University": ["princeton university"],
    "Yale University": ["yale university"],
    "Cornell University": ["cornell university"],
    "Columbia University": ["columbia university"],
    "Columbia Business School": ["columbia business school"],
    "University of Pennsylvania": ["university of pennsylvania", "the wharton school", "wharton"],
    "New York University": ["new york university", "nyu", "nyu stern school of business", "nyu tandon school of engineering", "new york university abu dhabi"],
    "University of Chicago": ["university of chicago"],
    "Duke University": ["duke university"],
    "Boston University": ["boston university"],
    "Boston College": ["boston college"],
    "Carnegie Mellon University": ["carnegie mellon university", "cmu"],
    "Georgia Institute of Technology": ["georgia institute of technology", "georgia tech"],
    "University of Michigan": ["university of michigan", "university of michigan-dearborn"],
    "University of Toronto": ["university of toronto"],
    "University of Melbourne": ["university of melbourne"],
    "University of Sydney": ["university of sydney"],
    "The Australian National University": ["the australian national university", "anu"],
    "University of Queensland": ["the university of queensland", "university of queensland"],
    "University of Bristol": ["university of bristol"],
    "University of Southern California": ["university of southern california", "usc"],
    "University of California, Berkeley": ["university of california berkeley", "uc berkeley", "university of california, berkeley"],
    "University of California, Davis": ["university of california davis", "uc davis", "university of california, davis"],
    "University of California, San Diego": ["uc san diego", "university of california san diego", "university of california, san diego"],
    "University of California, Merced": ["university of california merced", "uc merced", "university of california, merced"],
    "UCLA": ["ucla", "university of california los angeles", "university of california, los angeles"],

    # “Organizations / programs” you may want to keep as separate entities
    "EIT Digital": ["eit digital", "eit digital master school", "eit digital alumni"],
    "SISSA": ["sissa"],
    "Max Planck Society": ["max planck society"],
    "The Alan Turing Institute": ["the alan turing institute"],
    "Y Combinator": ["y combinator", "startup school online", "startup school live", "startup school"],
}

# Build reverse lookup (cleaned alias -> canonical)
_ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, aliases in _CANONICAL_TO_ALIASES.items():
    for a in aliases + [canonical]:
        _ALIAS_TO_CANONICAL[_clean(a)] = canonical


# -------------------- main function --------------------


def normalize_school(name: Optional[str]) -> Optional[str]:
    """
    Normalize a school/institution string into a canonical name.

    Returns:
      - None if it should be dropped (high schools/licei/secondary, etc.) or missing
      - canonical institution name otherwise
    """
    if name is None:
        return None

    raw = str(name).strip()
    if raw == "" or raw.lower() == "nan":
        return None

    s = _clean(raw)

    # Drop high-school-ish entries
    if _should_drop_school(s):
        return None

    # Direct alias hit
    if s in _ALIAS_TO_CANONICAL:
        return _ALIAS_TO_CANONICAL[s]

    # Heuristic collapses for common patterns not explicitly listed:
    # 1) If it's "X School of Management" and we know parent, map to parent
    if "school of management" in s or "business school" in s:
        for alias_clean, canonical in _ALIAS_TO_CANONICAL.items():
            if alias_clean in s:
                return canonical

    # Fallback: re-titlecase a cleaned-ish version of the original
    pretty = " ".join(
        w.capitalize() if w not in {"of", "and", "the", "di", "degli", "della", "del"} else w
        for w in s.split()
    )
    return pretty
