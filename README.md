## Feedback Classifier (Abusive Content Detection + Sentiment)

An interactive Flask web app that classifies user feedback as Abusive or Clean and, for clean feedback, performs a simple sentiment analysis (Positive, Negative, or Neutral). The app handles obfuscated profanity (e.g., f***, f@ck) and repeated characters (e.g., goooood) and includes basic false-positive mitigation via a Trie of abusive prefixes, obfuscation-aware regex, and a small safe-words list.

### Features
- **Abusive detection**: Trie-based prefix matching for multilingual/hinglish abusive terms
- **Obfuscation handling**: Regex tolerant to censor symbols like `* @ # $ % ^ &`
- **Repeated character normalization**: Handles tokens like `goooood` → `good`
- **Emoji handling**: Detects certain abusive emoji (e.g., 🖕)
- **Sentiment for clean feedback**: Lexicon-based positive/negative word matching with fuzzy similarity
- **Fast UI**: Single-page form with async POST to a JSON API

### Tech Stack
- **Backend**: Python, Flask
- **Frontend**: HTML/CSS/JS (vanilla), served via Flask templates

### Project Structure
```text
AI/
├─ app.py                  # Flask app with routes `/` and `/check_feedback`
├─ feedback_classifier.py  # Core detection + sentiment logic
├─ stopwords.txt           # Stopword list (UTF-8)
├─ positive.txt            # Positive sentiment lexicon
├─ negative.txt            # Negative sentiment lexicon
└─ templates/
   └─ index.html          # UI (single page)
```

### How It Works (Brief)
- `feedback_classifier.py` loads `stopwords.txt`, `positive.txt`, and `negative.txt` into memory.
- Input text is lowercased and tokenized while preserving censor symbols.
- A Trie is built from a curated list of abusive prefixes; tokens are checked against the Trie and a set of obfuscation-aware regex patterns.
- If no abusive content is found, sentiment is computed using fuzzy similarity against positive/negative lexicons.

### Prerequisites
- Python 3.8+

### Installation
1. Create and activate a virtual environment (recommended).
   - Windows PowerShell:
     ```bash
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
2. Install dependencies:
   ```bash
   pip install flask
   ```

### Run Locally
```bash
python app.py
```
The server starts in debug mode on `http://127.0.0.1:5000/`.

### Usage
- Open the web UI at `/` and submit feedback via the form.
- Or call the JSON endpoint directly:
  ```bash
  curl -X POST http://127.0.0.1:5000/check_feedback \
       -H "Content-Type: application/json" \
       -d '{"text": "Your product is amazing!!!"}'
  ```
  Example JSON response:
  ```json
  { "classification": "Clean", "sentiment": "Positive" }
  ```

### API
- `GET /` → renders `templates/index.html`
- `POST /check_feedback` → body `{ "text": string }`
  - Response shape: `{ "classification": "Abusive"|"Clean"|"Please give meaningful feedback", "sentiment"?: "Positive"|"Negative"|"Neutral" }`

### Configuration Notes
- The abusive lexicon, safe words, and regex patterns are defined inside `feedback_classifier.py`. Adjust to your needs and locale.
- Ensure `stopwords.txt`, `positive.txt`, and `negative.txt` are present in the project root and encoded as UTF‑8.

### Limitations
- Lexicon-based sentiment is simplistic and may not capture nuanced context or sarcasm.
- The abusive list is illustrative and not comprehensive; adapt for production use.
- Obfuscation handling is pattern-based; extreme or novel obfuscations may evade detection.

### Extending
- Add/modify abusive prefixes and obfuscation patterns in `feedback_classifier.py`.
- Expand sentiment lexicons (`positive.txt`, `negative.txt`) for your domain/language.
- Replace lexicon sentiment with a model (e.g., transformer) if you need higher accuracy.

### Ethical Use
Use this project responsibly. Content moderation decisions can have user impact; always review, disclose limitations, and avoid bias amplification.

### License
MIT (or your preferred license). Update this section as needed.


