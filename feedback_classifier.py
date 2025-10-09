
# ==============================
# 📌 Cell 1: Imports + Stopwords
# ==============================
import re
import difflib

# Load stopwords from file (put stopwords.txt in same directory)
with open("stopwords.txt", "r", encoding="utf-8") as f:
    stopwords = set(word.strip().lower() for word in f.readlines())

# Load positive and negative words for sentiment analysis
with open("positive.txt", "r", encoding="utf-8") as f:
    positive_words = set(word.strip().lower() for word in f.readlines())

with open("negative.txt", "r", encoding="utf-8") as f:
    negative_words = set(word.strip().lower() for word in f.readlines())
    
# ==============================
# 📌 Word Variation Handling
# ==============================

def normalize_repeated_chars(word):
    """
    Normalize words with repeated characters like 'goooood' to 'good'
    """
    if not word:
        return word

    # Allow up to two consecutive repeated characters.
    # This preserves legitimate double-letter words like 'good', 'better', etc.
    result_chars = []
    prev_char = None
    repeat_count = 0

    for char in word:
        if char == prev_char:
            repeat_count += 1
        else:
            repeat_count = 1
            prev_char = char

        # keep the char if it occurs at most twice consecutively
        if repeat_count <= 2:
            result_chars.append(char)

    return ''.join(result_chars)

def is_similar_to_any(word, word_list, threshold=0.8):
    """
    Check if a word is similar to any word in the word_list using fuzzy matching
    """
    # First normalize repeated characters
    normalized_word = normalize_repeated_chars(word)
    
    # Try exact match with normalized word
    if normalized_word in word_list:
        return True
    
    # Try fuzzy matching
    for dict_word in word_list:
        similarity = difflib.SequenceMatcher(None, normalized_word, dict_word).ratio()
        if similarity >= threshold:
            return True
    
    return False



def preprocess(text: str):
    """
    Preprocess text:
    - Lowercase
    - Tokenize into words WITH common censor symbols kept (so 'f***' stays one token)
    - Remove stopwords
    """
    text = text.lower().strip()

    # Words + common censor symbols in the same token; keep emojis too
    tokens = re.findall(
        r"[a-z0-9@#\*\$\%\&\^\_]+|[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]",
        text
    )

    # Filter stopwords but keep positive and negative sentiment words
    tokens = [t for t in tokens if t not in stopwords or t in positive_words or t in negative_words]
    return tokens

# ==============================
# 📌 Cell 3: Trie Data Structure
# ==============================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search_prefix(self, word: str):
        """
        Returns True if any abusive word is a prefix
        of the given token (e.g., 'chut' in 'chutiya').
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
            if node.is_end_of_word:
                return True
        return False

# ==============================
# 📌 Cell 4: Build Abusive Trie + Safe Words
# ==============================
abusive_words= [
    # Hindi/Hinglish
    "chut", "chu", "chodu","madar", "behenchod","bhenchod"
    "bhosdike", "randi", "harami", "gand", "lodu","laude","lavde","lauda","loda", "lund",
    "tatti", "gaand", "bhadwe", "bhadwa", "chinal", "kutta", "kuttiya",
    "kamina", "haram","chud","lendi","saala","saale",

    # English
    "fuck","motherfucker", "bullshit", "bastard",
    "slut", "whore", "asshole", "dick", "pussy", "bitch", "cock", "cunt",
    "dildo", "jerk", "wanker", "retard",

    # Short forms / Obfuscations
    "fck", "fuk", "fk", "phuck", "fuq",
    "mc", "bc", "bsdk", "chod", "ch0d",
    "kutti", "kutte", "rndi"
]

safe_words = ["gandhiji", "gandagi", "gandhak"]   # prevents false positives

trie = Trie()
for word in abusive_words:
    trie.insert(word)

# ==============================
# 📌 Cell 5: Regex for Obfuscated Words (Dynamic Generation)
# ==============================

OBFUSCATION = r"[*#x@\$%&^!]+"

def create_obfuscation_regex(word):
    """
    Create regex for abusive word allowing obfuscation like:
    - f***, f@ck
    - chutiy@, ch##tiya
    - m@dar, mad@r
    """
    first, last = word[0], word[-1]
    middle = word[1:-1]

    middle_pattern = ""
    for ch in middle:
        # Each char can be itself OR replaced by obfuscation symbols
        middle_pattern += f"(?:{re.escape(ch)}|{OBFUSCATION})+"

    pattern = f"^{re.escape(first)}(?:[\\W_]*{middle_pattern})?[\\W_]*{re.escape(last)}$"
    return re.compile(pattern, re.IGNORECASE)


# Build regex patterns
patterns = [create_obfuscation_regex(w) for w in abusive_words]

# ==============================
# 📌 Cell 6: Main Detection Function
# ==============================

def analyze_sentiment(tokens, debug: bool = False):
    """
    Analyze sentiment of tokens:
    - Count positive and negative words using fuzzy matching
    - Return sentiment (positive, negative, or neutral)
    """
    positive_count = 0
    negative_count = 0

    details = []  # per-token debug info

    for token in tokens:
        # normalize repeated chars and lowercase (preprocess already lowercases but be safe)
        norm = normalize_repeated_chars(token.lower())

        token_info = {
            "token": token,
            "normalized": norm,
            "exact_positive": False,
            "exact_negative": False,
            "fuzzy_positive_matches": [],
            "fuzzy_negative_matches": []
        }

        # Prefer exact normalized matches first to avoid fuzzy false-positives/negatives
        if norm in positive_words:
            positive_count += 1
            token_info["exact_positive"] = True
            details.append(token_info)
            continue
        if norm in negative_words:
            negative_count += 1
            token_info["exact_negative"] = True
            details.append(token_info)
            continue

        # Fall back to fuzzy matching when no exact match (collect matches for debug)
        # check positive fuzzies
        for pw in positive_words:
            sim = difflib.SequenceMatcher(None, norm, pw).ratio()
            if sim >= 0.8:
                token_info["fuzzy_positive_matches"].append({"word": pw, "score": sim})

        # check negative fuzzies
        for nwrd in negative_words:
            sim = difflib.SequenceMatcher(None, norm, nwrd).ratio()
            if sim >= 0.8:
                token_info["fuzzy_negative_matches"].append({"word": nwrd, "score": sim})

        # increment counts based on fuzzy results
        if token_info["fuzzy_positive_matches"]:
            positive_count += 1
        if token_info["fuzzy_negative_matches"]:
            negative_count += 1

        details.append(token_info)
    
    if positive_count > negative_count:
        label = "Positive"
    elif negative_count > positive_count:
        label = "Negative"
    else:
        label = "Neutral"

    if debug:
        return {
            "label": label,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "token_details": details,
        }

    return label

def is_abusive(text: str, debug: bool = False) -> dict:
    tokens = preprocess(text)
    result = {"classification": "", "sentiment": ""}

    if not tokens:   # if only stopwords / empty
        result["classification"] = "Please give meaningful feedback"
        return result

    for token in tokens:
        # Skip safe words
        if token in safe_words:
            continue

        # Check Trie-based abusive detection
        if trie.search_prefix(token):   # ✅ use your trie, not empty regex
            result["classification"] = "Abusive"
            return result

        # Check obfuscation regex patterns
        for pattern in patterns:
            if pattern.fullmatch(token):   # ✅ stricter than search
                result["classification"] = "Abusive"
                return result

        # Check abusive emoji
        if "🖕" in tokens:
            result["classification"] = "Abusive"
            return result

    # If feedback is clean, analyze sentiment
    result["classification"] = "Clean"
    sentiment_analysis = analyze_sentiment(tokens, debug=debug)
    result["sentiment"] = sentiment_analysis

    if debug:
        # include tokens and per-token debug info at top-level for convenience
        result["tokens"] = tokens
        if isinstance(sentiment_analysis, dict):
            result["details"] = sentiment_analysis
    
    return result
