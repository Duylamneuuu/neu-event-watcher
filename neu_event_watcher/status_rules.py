"""Deterministic, conservative classifier, not a substitute for human audit."""
import hashlib
import re
import unicodedata


STATUS_PATTERNS = {
    'SOLD_OUT': [r'\bhết\s+vé\b', r'\bhết\s+suất\b', r'\bhết\s+chỗ\b', r'\bsold\s*out\b', r'\bfully\s*booked\b'],
    'CLOSED': [r'\bđóng\s+đơn\b', r'\bđóng\s+đăng\s+ký\b', r'\bđã\s+đóng\s+(?:biểu\s+mẫu|form)\b', r'\bregistration\s+closed\b', r'\bkhông\s+còn\s+nhận\s+đăng\s+ký\b'],
}


def normalize_text(raw):
    txt = unicodedata.normalize('NFKC', raw or '').lower()
    return re.sub(r'\s+', ' ', txt).strip()


def classify_status(text):
    txt = normalize_text(text)
    # Label only when an explicit phrase on a dedicated event page supports it.
    # Never infer OPEN merely because a deadline has not elapsed.
    for status, patterns in STATUS_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, txt)
            if match:
                start, end = match.span()
                # A phrase like 'chưa hết vé' or 'chưa đóng đơn' is not
                # evidence that registration is closed. Prefer review.
                prefix = txt[max(0, start - 28):start]
                if re.search(r'(?:\bchưa|\bkhông|\bvẫn chưa)\s+$', prefix):
                    continue
                return status, txt[max(0, start-95):min(len(txt), end+125)], 'explicit_text'
    return 'UNCERTAIN', '', 'insufficient_evidence'


def fingerprint(text):
    return hashlib.sha256(normalize_text(text).encode('utf-8')).hexdigest()
