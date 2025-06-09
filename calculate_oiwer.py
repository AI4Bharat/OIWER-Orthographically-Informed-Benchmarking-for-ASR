import numpy as np
import argparse
import json
from tqdm import tqdm
import os
import string, re
import csv
import jiwer
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory

def normalize_sentence(sentence, lang_code):
    '''
    Perform NFC -> NFD normalization for a sentence and a given language
    sentence: string
    lang_code: language code in ISO format
    '''
    factory=IndicNormalizerFactory()
    normalizer=factory.get_normalizer(lang_code)
    sentence = sentence.translate(str.maketrans('', '', string.punctuation+"।۔'-"))
    normalized_sentence = normalizer.normalize(sentence)
    return normalized_sentence

lang_codes = {
    'assamese' :'as',
    'bengali' :'bn',
    'bodo' :'brx',
    'dogri' :'doi',
    'gujarati' :'gu',
    'hindi' :'hi',
    'kannada' :'kn',
    'kashmiri' :'ks',
    'konkani' :'kok',
    'maithili' :'mai',
    'malayalam' :'ml',
    'manipuri' :'mni',
    'marathi' :'mr',
    'nepali' :'ne',
    'odia' :'or',
    'punjabi' :'pa',
    'sanskrit' :'sa',
    'santali' :'sat',
    'sindhi' :'sd',
    'tamil' :'ta',
    'telugu' :'te',
    'urdu' :'ur'
}

def refine_sentence(sentence):
    translator = {
        '॥' : ' ',
        '۔' : ' ',
        '।' : ' ',
        '‘' : '',
        '–' : ' ',
        '’' : ' ',
        'ʼ' : '',
        '°' : ' ',
        '¬' : ' ',
        'ۭ': ' ',
        '۪': ' ',
        '‑': ' ',
        '—': ' ',
        '\u200b' : '',
        '\u200c' : '',
        '\u200d' : '',
        '´': '',
        "," : '',
        '\u200e': '',
        '\u200f': '',
        '“': '',
        '”': '',
    }
    translator.update({x:" " for x in (set(string.punctuation)-set(','))})
    ref_sent = str.translate(sentence,str.maketrans(translator))
    return ref_sent

def get_lang_code(input_lang):
    if input_lang == 'odia':
        inp_lang = 'ori'
    elif input_lang == 'punjabi':
        inp_lang = 'pan'
    elif input_lang == 'sanskrit':
        inp_lang = 'hin'
    else:
        inp_lang = input_lang[:3]
    return inp_lang


def mwer(hypothesis, reference_lists, input_language):
    """
    Calculate Minimum Word Error Rate (MWER) for a given hypothesis and aligned reference lists.

    Parameters:
    - hypothesis: list of strings (the hypothesis sentence)
    - reference_lists: list of lists of strings (aligned reference words with variations)

    Returns:
    - mwer: Minimum Word Error Rate as a percentage
    - aligned_h: hypothesis
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
    standardized_reference_lists = []
    for words in reference_lists:
        words = [refine_sentence(variation) for variation in words]
        if (iso_code in lang_codes.values()) and (iso_code not in ['ur', 'kok', 'mai', 'doi', 'sat', 'mni', 'brx', 'ks']):
            words = [normalize_sentence(variation, iso_code) for variation in words]
        words = [re.sub(' +', ' ', variation).strip() for variation in words]
        words = [re.sub('\t+', ' ', variation).strip() for variation in words]
        standardized_reference_lists.append(words)
    reference_list = standardized_reference_lists

    n = len(reference_lists) + 1  # rows (reference)
    m = len(hypothesis) + 1       # columns (hypothesis)

    # Initialize D matrix
    D = np.zeros((n, m), dtype=int)
    for i in range(1, n):
        D[i,0] = D[i-1,0] + min([len(variation.split()) for variation in reference_lists[i-1]]) 
    D[0, :] = range(m)  # cost of insertion

    # Backtrack matrix to store operations
    # B = np.zeros((n, m), dtype=[("del", bool), ("sub", bool), ("ins", bool), ("var_id", int)])
    B = np.zeros((n, m), dtype=[("del", bool), ("sub", bool), ("ins", bool), ("var_id", int)])


    B[1:, 0] = (1, 0, 0, -1)
    B[0, 1:] = (0, 0, 1, -1)
    
    # Fill the matrix
    for i, ref_variations in enumerate(reference_lists, start=1):
        for j, hyp_word in enumerate(hypothesis, start=1):
            deletion_cost = min([len(variation.split()) for variation in ref_variations]) 
            insertion_cost = 1
            # Check substitution against all variations
            min_substitution_cost = np.inf
            substitution = np.inf
            best_variation_idx = -1
            for var_idx, variation in enumerate(ref_variations):
                variation_words = variation.split()  # Split multi-word variations
                if j - len(variation_words) >= 0:
                    variation_substitution_cost = 0
                    for hyp_word, ref_word in zip(hypothesis[j - len(variation_words):j], variation_words):
                        variation_substitution_cost += int((hyp_word != ref_word))
                    if variation_substitution_cost < min_substitution_cost:
                        min_substitution_cost = min(min_substitution_cost, variation_substitution_cost)
                        substitution = D[i - 1, j - len(variation_words)] + variation_substitution_cost
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
            assert B[i,j][3] > -1, "There is a substitution, variation index cannot be -1"
            variation = reference_lists[i - 1][B[i,j][3]]
            variation_words = variation.split()
            for hyp_word, ref_word in reversed(list(zip(hypothesis[j - len(variation_words):j], variation_words))):
                aligned_r.append(ref_word)
                aligned_h.append(hyp_word)
                operations.extend(["c" if ref_word == hyp_word else "s"])
            j -= len(variation_words)
            i -= 1
        elif j > 0 and B[i,j][2]:  # Insertion
            aligned_r.append(" ")
            aligned_h.append(hypothesis[j - 1])
            operations.append("i")
            j -= 1
        elif i > 0 and B[i, j][0]:  # Deletion
            min_len_variation = np.argmin([len(variation.split()) for variation in reference_list[i-1]]) 
            aligned_r.append(reference_lists[i - 1][min_len_variation])  # Take the first reference variation
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

    total_errors = insertions + deletions + substitutions
    total_reference_words = len(reference_lists)

    mwer = (total_errors / total_reference_words) * 100 if total_reference_words > 0 else 0

    return mwer, aligned_h, aligned_r, operations, (insertions, deletions, substitutions), total_reference_words

def calculate_mwer_for_jsonfile(file_path, variations_field_name, pred_field_name, language):
    total_insertions = 0
    total_deletions = 0
    total_substitutions = 0
    total_reference_words = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in tqdm(enumerate(f), desc="Processing Sentences"):
            data = json.loads(line)
            hypothesis = data[pred_field_name]
            reference_lists = data[variations_field_name]
            # print("hypothesis", hypothesis)
            # print("references", reference_lists)
            _, _, _, _, errors, reference_words = mwer(hypothesis, reference_lists, language)
            total_insertions += errors[0]
            total_deletions += errors[1]
            total_substitutions += errors[2]
            total_reference_words += reference_words

    total_errors = total_insertions + total_deletions + total_substitutions
    overall_mwer = (total_errors / total_reference_words) if total_reference_words > 0 else 0

    data = {
        "mwer": overall_mwer,
        "mwer_hits": total_reference_words - total_errors,
        "mer_subs": total_substitutions,
        "mer_dels": total_deletions,
        "mer_ins": total_insertions
    }

    return data 

def calculate_wer_for_jsonfile(file_path, gt_fieldname, pred_fieldname, language, model_name, dataset_name):
    ground_truth_text = []
    predicted_text = []
    invalid_manifest = False
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)

            if pred_fieldname not in data:
                invalid_manifest = True
                break

            ground_truth_text.append(data[gt_fieldname])

            predicted_text.append(data[pred_fieldname])

    
    iso_code = lang_codes[language]
    # remove punctutations
    ground_truth_text = [refine_sentence(sent) for sent in ground_truth_text]
    predicted_text = [refine_sentence(sent) for sent in predicted_text]
    if iso_code in lang_codes.keys():
        ground_truth_text = [normalize_sentence(sent, iso_code) for sent in ground_truth_text]
        predicted_text = [normalize_sentence(sent, iso_code) for sent in predicted_text]
    # # remove extra spaces
    ground_truth_text = [re.sub(' +', ' ', sent).strip() for sent in ground_truth_text]
    predicted_text = [re.sub(' +', ' ', sent).strip() for sent in predicted_text]
    ground_truth_text = [re.sub('\t+', ' ', sent).strip() for sent in ground_truth_text]
    predicted_text = [re.sub('\t+', ' ', sent).strip() for sent in predicted_text]
    
    data = {}
    data['model'] = model_name
    data['dataset'] = dataset_name
    data['language'] = language
    data['cer'] = jiwer.cer(ground_truth_text, predicted_text)
    measures = jiwer.compute_measures(ground_truth_text, predicted_text)
    data['wer'] = measures['wer']
    data['wer_hits'] = measures['hits']
    data['wer_subs'] = measures['substitutions']
    data['wer_dels'] = measures['deletions']
    data['wer_ins'] = measures['insertions']
    return data
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate MWER for a JSONLines file.")
    parser.add_argument("file", help="Path to the JSONLines file.")
    parser.add_argument("output_file", help="Path to csv file that save the oiwer result")
    parser.add_argument("language", help="Name of the language in lowercase")
    parser.add_argument('model_name', type=str, help='Name of the model')
    parser.add_argument('dataset_name', type=str, help='Name of the dataset')
    args = parser.parse_args()

    wer_data = calculate_wer_for_jsonfile(args.file, "text", "pred_text", args.language, args.model_name, args.dataset_name)
    mwer_llm_data = calculate_mwer_for_jsonfile(args.file, "variations", "transcribed_text" ,args.language)
    
    # ############################# Writing to CSV ###############################
    csv_filename = args.output_file
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
    
        if not file_exists:
            writer.writerow([
                "model", "dataset", "language", "wer", "cer",
                "mwer_llm", 
                "WER hits", "WER subs", "WER dels", "WER ins",
                "MWER_LLM hits", "MWER_LLM subs", "MWER_LLM dels", "MWER_LLM ins",
            ])

            

       
        writer.writerow([
             wer_data["model"], wer_data["dataset"], wer_data["language"], wer_data["wer"], wer_data["cer"],
             mwer_llm_data["mwer"],
             wer_data["wer_hits"], wer_data["wer_subs"], wer_data["wer_dels"], wer_data["wer_ins"],
             mwer_llm_data["mwer_hits"], mwer_llm_data["mer_subs"], mwer_llm_data["mer_dels"], mwer_llm_data["mer_ins"],
        ])

print(f"CSV file '{csv_filename}' has been created successfully!")
        
