import re
from typing import List, Tuple

# Simple v1 abusive lexicon. Extend as needed or load from file.
ABUSIVE_WORDS = {
    # English
    "idiot", "stupid", "loser", "moron", "bitch", "slut", "dumb",
    "fool", "trash", "whore", "bastard", "asshole", "hate", "kill",
    # Basic Hindi/hinglish (extend later)
    "chutiya", "gandu", "randi", "kutte", "kamina", "bewakoof", "bhosdike",
}

WORD_REGEX = re.compile(r"\b([\w']+)\b", re.IGNORECASE)


def detect_abuse(text: str) -> Tuple[bool, List[str]]:
    if not text:
        return False, []
    words = [m.group(1).lower() for m in WORD_REGEX.finditer(text)]
    hits = sorted({w for w in words if w in ABUSIVE_WORDS})
    return (len(hits) > 0), hits
