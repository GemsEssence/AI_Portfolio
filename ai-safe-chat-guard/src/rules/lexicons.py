# rules/lexicons.py

# --- Abuse / Toxicity ---
ABUSE_KEYWORDS = {
    "idiot", "stupid", "dumb", "shut up",
    "loser", "moron", "ugly", "trash",
    "nobody likes you", "fool", "clown",
    "disgusting", "pathetic", "worthless"
}
    
# --- Threats / Violence ---
THREAT_KEYWORDS = {
    "hurt you", "punch you", "kill you", "end you",
    "stab you", "burn your house", "make you pay",
    "break your legs", "destroy you", "beat you up",
    "ruin your life", "shoot you", "hang you"
}

# --- Crisis / Mental Health ---
CRISIS_SELF_HARM = {
    "hate myself", "cut myself", "self harm", "hopeless",
    "bleeding", "pain all the time", "want to disappear",
    "worthless", "life is pointless", "i can’t go on",
    "i don’t want to live", "overdose"
}

CRISIS_SUICIDE = {
    "suicide", "end it all", "kill myself", "end my life",
    "jump off", "hang myself", "take my life",
    "goodbye forever", "better if i wasn’t here",
    "nothing matters anymore"
}

# --- Age Taxonomy ---
AGE_TAXONOMY = {
    "7+": {
        "cartoon", "toy", "play", "game", "puppy",
        "school", "funny", "friendship", "lego", "superhero"
    },
    "13+": {
        "mild", "argument", "romance", "dating", "crush",
        "scary", "fight", "blood", "alcohol", "bully",
        "gossip", "video game", "fantasy"
    },
    "18+": {
        "explicit", "sexual", "graphic", "violence",
        "drugs", "gambling", "nude", "porn", "murder",
        "rape", "weapon", "terrorist", "cocaine",
        "fetish", "genitals", "heroin"
    },
}
