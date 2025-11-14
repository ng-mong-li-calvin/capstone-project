import json, re, logging, string, nltk
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Union
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

# Public API
__all__ = [
    "extract_by_bleu_and_sections",
    "best_bleu_match",
    "normalize",
    "tokenize",
]

logger = logging.getLogger(__name__)

# Default BLEU threshold
BLEU_THRESHOLD_DEFAULT = 0.25

# Precompile regex for numbered lines like "1.", "2)", etc.
_NUMBERED_RE = re.compile(r"^\d+[.)]\s*")


def normalize(text: str) -> str:
    """
    Lowercase and remove punctuation from text.
    """
    if text is None:
        return ""
    return text.lower().translate(str.maketrans("", "", string.punctuation))


def tokenize(text: str) -> List[str]:
    """
    Tokenize text using NLTK's word_tokenize, falling back to split()
    if required resources are missing.
    """
    text = normalize(text)
    try:
        # Ensure required punkt model is available; if not, a LookupError will be raised.
        return nltk.word_tokenize(text)
    except LookupError:
        logger.warning("NLTK punkt tokenizer not available; falling back to simple split.")
        return text.split()


def best_bleu_match(
    line: str,
    candidates: Sequence[str],
    threshold: float = BLEU_THRESHOLD_DEFAULT,
) -> Optional[str]:
    """
    Return the candidate with the highest sentence BLEU score for the given line
    if the score is >= threshold. Otherwise, return None.
    """
    if not line or not candidates:
        return None

    line_tokens = tokenize(line)
    if not line_tokens:
        return None

    best_q: Optional[str] = None
    best_score: float = 0.0
    smooth = SmoothingFunction().method1

    for q in candidates:
        if not q:
            continue
        ref_tokens = [tokenize(q)]
        try:
            score = sentence_bleu(ref_tokens, line_tokens, smoothing_function=smooth)
        except Exception:
            # If BLEU fails for some reason, skip candidate
            logger.exception("BLEU computation failed for candidate; skipping.")
            continue

        if score > best_score:
            best_score = score
            best_q = q

    return best_q if best_score >= threshold else None


def extract_by_bleu_and_sections(
    text: str,
    questions_json_input: Union[str, Sequence[Dict[str, Any]]],
    bleu_threshold: float = BLEU_THRESHOLD_DEFAULT,
) -> List[Dict[str, str]]:
    """
    Extract answers from `text` by matching question variants (from `questions_json_input`)
    against lines in the text using sentence-level BLEU. Returns a list of merged results:

    [
        {"question_id": <id>, "question_text": "<joined question texts>", "answer_text": "<joined answers>"},
        ...
    ]

    `questions_json_input` may be a JSON string or a list of dicts with keys:
      - question_id
      - questions (a list of variant strings)
    """
    # Normalize/parse questions input
    if isinstance(questions_json_input, str):
        try:
            questions_json = json.loads(questions_json_input)
        except json.JSONDecodeError:
            logger.exception("Failed to parse questions_json_input as JSON.")
            raise
    else:
        questions_json = questions_json_input

    if not isinstance(questions_json, Sequence):
        raise TypeError("questions_json_input must be a JSON string or a sequence of mappings.")

    raw_lines = [ln for ln in text.splitlines()]
    lines = [ln.strip() for ln in raw_lines]

    # Identify numbered section boundaries and ensure final boundary exists
    numbered_indices = [i for i, ln in enumerate(lines) if _NUMBERED_RE.match(ln)]
    if not numbered_indices or numbered_indices[-1] != len(lines):
        numbered_indices.append(len(lines))

    results: List[Dict[str, str]] = []

    # Iterate over each question section (expected structure described above)
    for section in questions_json:
        if not isinstance(section, dict):
            continue
        qid = section.get("question_id")
        candidates = section.get("questions", []) or []
        if not qid or not candidates:
            # skip incomplete entries
            continue

        matched_positions: List[tuple[int, str]] = []

        for idx, ln in enumerate(lines):
            if not ln or "http://" in ln or "https://" in ln:
                continue
            best = best_bleu_match(ln, candidates, threshold=bleu_threshold)
            if best:
                matched_positions.append((idx, best))

        if not matched_positions:
            continue

        matched_positions.sort(key=lambda x: x[0])
        all_boundaries = sorted(set([pos for pos, _ in matched_positions] + numbered_indices))

        for pos_idx, matched_q in matched_positions:
            # find the next boundary after the match position
            next_boundary = len(lines)
            for b in all_boundaries:
                if b > pos_idx:
                    next_boundary = b
                    break

            # Collect answer block lines between the matched line and the next boundary
            answer_block: List[str] = []
            for j in range(pos_idx + 1, next_boundary):
                # Use original raw_lines to preserve spacing, then strip leading/trailing whitespace
                line_text = raw_lines[j].strip()
                if not line_text or line_text.startswith("http"):
                    continue
                answer_block.append(line_text)

            if answer_block:
                results.append(
                    {
                        "question_id": qid,
                        "question_text": matched_q,
                        "answer_text": "\n".join(answer_block),
                    }
                )

    # Merge results by question_id: join question_texts and answer_texts
    merged: Dict[Any, Dict[str, Any]] = defaultdict(lambda: {"question_id": None, "question_text": [], "answer_text": []})

    for r in results:
        qid = r["question_id"]
        merged[qid]["question_id"] = qid
        merged[qid]["question_text"].append(r["question_text"])
        merged[qid]["answer_text"].append(r["answer_text"])

    merged_results: List[Dict[str, str]] = []
    for qid, content in merged.items():
        merged_results.append(
            {
                "question_id": content["question_id"],
                "question_text": " ".join(content["question_text"]),
                "answer_text": "\n".join(content["answer_text"]),
            }
        )

    return merged_results