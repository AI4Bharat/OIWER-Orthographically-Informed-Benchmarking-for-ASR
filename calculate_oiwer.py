import argparse
import json
from tqdm import tqdm
import os
import re
import csv
import jiwer

# Import shared OIWER core functions
from oiwer_core import oiwer, normalize_sentence, refine_sentence, lang_codes

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


def calculate_oiwer_for_jsonfile(file_path, variations_field_name, pred_field_name, language):
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
            _, _, _, _, errors, reference_words = oiwer(hypothesis, reference_lists, language)
            total_insertions += errors[0]
            total_deletions += errors[1]
            total_substitutions += errors[2]
            total_reference_words += reference_words

    total_errors = total_insertions + total_deletions + total_substitutions
    overall_oiwer = (total_errors / total_reference_words) if total_reference_words > 0 else 0

    data = {
        "oiwer": overall_oiwer,
        "oiwer_hits": total_reference_words - total_errors,
        "oiwer_subs": total_substitutions,
        "oiwer_dels": total_deletions,
        "oiwer_ins": total_insertions
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
    parser = argparse.ArgumentParser(description="Calculate OIWER for a JSONLines file.")
    parser.add_argument("file", help="Path to the JSONLines file.")
    parser.add_argument("output_file", help="Path to csv file that save the oiwer result")
    parser.add_argument("language", help="Name of the language in lowercase")
    parser.add_argument('model_name', type=str, help='Name of the model')
    parser.add_argument('dataset_name', type=str, help='Name of the dataset')
    args = parser.parse_args()

    wer_data = calculate_wer_for_jsonfile(args.file, "text", "pred_text", args.language, args.model_name, args.dataset_name)
    oiwer_llm_data = calculate_oiwer_for_jsonfile(args.file, "variations", "transcribed_text" ,args.language)
    
    # ############################# Writing to CSV ###############################
    csv_filename = args.output_file
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
    
        if not file_exists:
            writer.writerow([
                "model", "dataset", "language", "wer", "cer",
                "oiwer_llm", 
                "WER hits", "WER subs", "WER dels", "WER ins",
                "OIWER_LLM hits", "OIWER_LLM subs", "OIWER_LLM dels", "OIWER_LLM ins",
            ])

            

       
        writer.writerow([
             wer_data["model"], wer_data["dataset"], wer_data["language"], wer_data["wer"], wer_data["cer"],
             oiwer_llm_data["oiwer"],
             wer_data["wer_hits"], wer_data["wer_subs"], wer_data["wer_dels"], wer_data["wer_ins"],
             oiwer_llm_data["oiwer_hits"], oiwer_llm_data["oiwer_subs"], oiwer_llm_data["oiwer_dels"], oiwer_llm_data["oiwer_ins"],
        ])

    print(f"CSV file '{csv_filename}' has been created successfully!")
        
