"""
Core OIWER (Optimal Interchangeable Word Error Rate) implementation.
This module contains the shared oiwer function used by all OIWER calculation scripts.

The OIWER algorithm:
1. Splits phrase-level variations into word-level where possible
2. Uses dynamic programming to find optimal alignment
3. Prioritizes maximum matches over minimum edits when choosing variations
4. Counts reference words based on maximum word count among variations
"""

import numpy as np
import string
import re
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory

lang_codes = {
    'assamese': 'as',
    'bengali': 'bn',
    'bodo': 'brx',
    'dogri': 'doi',
    'gujarati': 'gu',
    'hindi': 'hi',
    'kannada': 'kn',
    'kashmiri': 'ks',
    'konkani': 'kok',
    'maithili': 'mai',
    'malayalam': 'ml',
    'manipuri': 'mni',
    'marathi': 'mr',
    'nepali': 'ne',
    'odia': 'or',
    'punjabi': 'pa',
    'sanskrit': 'sa',
    'santali': 'sat',
    'sindhi': 'sd',
    'tamil': 'ta',
    'telugu': 'te',
    'urdu': 'ur'
}


def normalize_sentence(sentence, lang_code):
    '''
    Perform NFC -> NFD normalization for a sentence and a given language
    sentence: string
    lang_code: language code in ISO format
    '''
    factory = IndicNormalizerFactory()
    normalizer = factory.get_normalizer(lang_code)
    sentence = sentence.translate(str.maketrans('', '', string.punctuation + "।۔'-"))
    normalized_sentence = normalizer.normalize(sentence)
    return normalized_sentence


def split_phrase_to_word_variations(phrase_variations):
    """
    Convert phrase-level variations to word-level variations intelligently.
    
    Args:
        phrase_variations: List of phrase variations, e.g.,
            ["हाँ तो इसका मतलब", "हाँ तो इस का मतलब", "हां तो इसका मतलब"]
            or ["दस हजार छह सौ इक्कीस", "10621"]
    
    Returns:
        List of word-level variation lists, e.g.,
            [["हाँ", "हां"], ["तो"], ["इसका"], ["मतलब"]]
            or [["दस हजार छह सौ इक्कीस", "10621"]]  (kept as phrase if not splittable)
    
    Logic:
        - Splits when all variations have the same number of words
        - Keeps phrase-level when variations have different word counts (will be handled by 3D DP)
        - Keeps phrase-level when any variation is a single word
    """
    if not phrase_variations:
        return []
    
    # Split each variation into words
    split_variations = [var.split() for var in phrase_variations]
    word_counts = [len(words) for words in split_variations]
    
    # Check if any variation is a single word - keep as phrase-level
    if min(word_counts) == 1:
        return [phrase_variations]
    
    # Check if all variations have the same number of words
    if len(set(word_counts)) > 1:
        # Different word counts - keep as phrase-level for 3D DP to handle
        return [phrase_variations]
    
    # All variations have the same number of words - split into word-level
    num_words = word_counts[0]
    word_level_variations = []
    
    for word_idx in range(num_words):
        # Collect all variations for this word position
        word_variations = []
        for var_words in split_variations:
            word = var_words[word_idx]
            if word not in word_variations:
                word_variations.append(word)
        word_level_variations.append(word_variations)
    
    return word_level_variations


def convert_text_list_to_word_level(text_list):
    """
    Convert a text_list with phrase-level variations to word-level variations.
    
    Args:
        text_list: List of phrase-level variation lists
    
    Returns:
        List of word-level variation lists
    
    Example:
        Input:  [["हाँ तो इसका", "हां तो इसका"], ["मतलब"]]
        Output: [["हाँ", "हां"], ["तो"], ["इसका"], ["मतलब"]]
        
        Input:  [["दस हजार छह सौ", "10621"]]
        Output: [["दस हजार छह सौ", "10621"]]  (kept as phrase due to word count mismatch)
        
        Input:  [["हाँ तो इसका मतलब", "हाँ तो इस का मतलब"]]  (4 vs 5 words)
        Output: [["हाँ"], ["तो"], ["इसका", "इस का"], ["मतलब"]]  (handles ±1 word difference)
    """
    result = []
    
    for phrase_variations in text_list:
        word_level = split_phrase_to_word_variations(phrase_variations)
        result.extend(word_level)
    
    return result


def refine_sentence(sentence):
    """Remove punctuation and special characters from sentence"""
    # Characters to replace (all must be single characters for str.maketrans)
    replacements = {
        '\u0965': ' ',  # ॥
        '\u0964': ' ',  # ।
        '\u06d4': ' ',  # ۔
        '\u2018': '',   # '
        '\u2013': ' ',  # –
        '\u2019': ' ',  # '
        '\u02bc': '',   # ʼ
        '\u00b0': ' ',  # °
        '\u00ac': ' ',  # ¬
        '\u06ed': ' ',  # ۭ
        '\u06ea': ' ',  # ۪
        '\u2011': ' ',  # ‑
        '\u2014': ' ',  # —
        '\u200b': '',   # zero width space
        '\u200c': '',   # zero width non-joiner
        '\u200d': '',   # zero width joiner
        '\u00b4': '',   # ´
        ',': '',
        '\u200e': '',   # left-to-right mark
        '\u200f': '',   # right-to-left mark
        '\u201c': '',   # "
        '\u201d': '',   # "
    }
    
    # Add standard punctuation marks
    for char in string.punctuation:
        if char not in replacements:
            replacements[char] = ' '
    
    # Create translation table
    translation_table = str.maketrans(replacements)
    ref_sent = sentence.translate(translation_table)
    
    return ref_sent


def oiwer(hypothesis, reference_lists, input_language):
    """
    Calculate Oracle-Informed Word Error Rate (OIWER) for a given hypothesis and aligned reference lists.

    Parameters:
    - hypothesis: string (the hypothesis sentence)
    - reference_lists: list of lists of strings (aligned reference words with variations)
    - input_language: string (language name in lowercase)

    Returns:
    - oiwer: Oracle-Informed Word Error Rate as a percentage
    - aligned_h: hypothesis words after alignment
    - aligned_r: List of aligned reference words (minimum error alignment)
    - operations: List of operations (i, d, s, c)
    - errors: Tuple of (insertions, deletions, substitutions)
    - total_reference_words: Total number of reference words
    """
    
    # Normalize hypothesis
    iso_code = lang_codes[input_language]
    hypothesis = refine_sentence(hypothesis)
    if (iso_code in lang_codes.values()) and (iso_code not in ['ur', 'kok', 'mai', 'doi', 'sat', 'mni', 'brx', 'ks']):
        hypothesis = normalize_sentence(hypothesis, iso_code)
    hypothesis = re.sub(' +', ' ', hypothesis).strip()
    hypothesis = re.sub('\t+', ' ', hypothesis).strip()
    hypothesis = hypothesis.split()
    
    # Normalize reference lists
    standardized_reference_lists = []
    for words in reference_lists:
        words = [refine_sentence(variation) for variation in words]
        if (iso_code in lang_codes.values()) and (iso_code not in ['ur', 'kok', 'mai', 'doi', 'sat', 'mni', 'brx', 'ks']):
            words = [normalize_sentence(variation, iso_code) for variation in words]
        words = [re.sub(' +', ' ', variation).strip() for variation in words]
        words = [re.sub('\t+', ' ', variation).strip() for variation in words]
        standardized_reference_lists.append(words)
    reference_list = standardized_reference_lists
    
    # Pre-expand multi-word phrase variations into word-level for DP
    # For each phrase with multiple words, select the best-matching variation and expand it
    expanded_reference_list = []
    for ref_variations in reference_list:
        # Check if this is a multi-word phrase variation (any variation has >1 word)
        is_phrase = any(len(var.split()) > 1 for var in ref_variations)
        
        if is_phrase:
            # Select the best matching variation based on hypothesis
            best_var = None
            best_score = -1
            
            for var in ref_variations:
                var_words = var.split()
                # Score based on how many hypothesis words match this variation
                score = sum(1 for hw in hypothesis if hw in var_words)
                if score > best_score:
                    best_score = score
                    best_var = var
            
            # Expand the best variation into word-level items
            best_var_words = best_var.split()
            for word in best_var_words:
                expanded_reference_list.append([word])
        else:
            # Already word-level, keep as is
            expanded_reference_list.append(ref_variations)
    
    # Use the expanded list for DP
    reference_lists = expanded_reference_list
    reference_list = expanded_reference_list

    n = len(reference_lists) + 1  # rows (reference)
    m = len(hypothesis) + 1       # columns (hypothesis)

    # Initialize D matrix
    D = np.zeros((n, m), dtype=int)
    for i in range(1, n):
        # After expansion, each reference item should be a single word
        D[i, 0] = D[i-1, 0] + 1
    D[0, :] = range(m)  # cost of insertion

    # Backtrack matrix to store operations
    B = np.zeros((n, m), dtype=[("del", bool), ("sub", bool), ("ins", bool), ("var_id", int)])

    B[1:, 0] = (1, 0, 0, -1)
    B[0, 1:] = (0, 0, 1, -1)
    
    # Fill the matrix
    for i, ref_variations in enumerate(reference_lists, start=1):
        for j, hyp_word in enumerate(hypothesis, start=1):
            # After expansion, everything should be word-level (single word)
            deletion_cost = 1
            insertion_cost = 1
            
            # Check substitution/match against all variations
            substitution = np.inf
            best_variation_idx = -1
            
            for var_idx, variation in enumerate(ref_variations):
                # Each variation should now be a single word after expansion
                if variation == hypothesis[j - 1]:
                    # Match
                    cost = D[i - 1, j - 1]
                else:
                    # Substitution
                    cost = D[i - 1, j - 1] + 1
                
                if cost < substitution:
                    substitution = cost
                    best_variation_idx = var_idx

            deletion = D[i - 1, j] + deletion_cost 
            insertion = D[i, j - 1] + insertion_cost

            min_cost = min(deletion, insertion, substitution)
            D[i, j] = min_cost

            B[i, j] = (
                deletion == min_cost,
                substitution == min_cost,
                insertion == min_cost,
                best_variation_idx
            )

    # Perform backtracking
    aligned_r = []
    aligned_h = []
    operations = []

    i, j = len(reference_lists), len(hypothesis)
    while i > 0 or j > 0:
        if i > 0 and j > 0 and B[i, j][1]:  # Substitution or Match
            assert B[i, j][3] > -1, "There is a substitution, variation index cannot be -1"
            ref_word = reference_lists[i - 1][B[i, j][3]]
            hyp_word = hypothesis[j - 1]
            aligned_r.append(ref_word)
            aligned_h.append(hyp_word)
            operations.append("c" if ref_word == hyp_word else "s")
            j -= 1
            i -= 1
        elif j > 0 and B[i, j][2]:  # Insertion
            aligned_r.append(" ")
            aligned_h.append(hypothesis[j - 1])
            operations.append("i")
            j -= 1
        elif i > 0 and B[i, j][0]:  # Deletion
            # Since we've pre-expanded phrases, deletions are now word-level
            # Just take the first variation (they should all be single words now)
            deleted_word = reference_lists[i - 1][0]
            aligned_r.append(deleted_word)
            aligned_h.append(" ")
            operations.append("d")
            i -= 1
        
    # Reverse the alignments as they are constructed backwards
    aligned_r.reverse()
    aligned_h.reverse()
    operations.reverse()

    # Compute error metrics
    insertions = operations.count("i")
    deletions = operations.count("d")
    substitutions = operations.count("s")
    correct = operations.count("c")

    # Count reference words - after expansion, each position is a single word
    total_reference_words = len(reference_list)

    total_errors = insertions + deletions + substitutions

    oiwer_score = (total_errors / total_reference_words) * 100 if total_reference_words > 0 else 0

    return oiwer_score, aligned_h, aligned_r, operations, (insertions, deletions, substitutions), total_reference_words
