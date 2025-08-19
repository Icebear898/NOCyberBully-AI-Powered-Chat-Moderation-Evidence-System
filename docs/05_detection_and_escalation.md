# Detection & Escalation

## Detection (v1)
- Lexicon-based detection using regex word tokenization
- Abusive terms include English and a small set of Hindi/hinglish words
- Extend by loading external lists or integrating ML models

## Sensitivity → Thresholds
- High: warn at 1st offense, block on 2nd
- Medium: warn at 1st, final warning at 2nd, block on 3rd
- Low: warn at 2nd, block on 4th

## Incident Lifecycle
1. Message received and persisted
2. Detection finds abusive terms → client asked to capture screenshot
3. Incident logged with severity:
   - `warning` → first threshold
   - `final_warning` → penultimate threshold
   - `blocked` → offender auto-blocked for victim
4. Receiver is notified via private info message

## Upgrading to ML
- Integrate HuggingFace toxic classification model (e.g., `unitary/toxic-bert`)
- Or call Google Perspective API for toxicity, insult, threat attributes
- Use a confidence threshold to combine with lexicon rules
