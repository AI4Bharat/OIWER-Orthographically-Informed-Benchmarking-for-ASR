TASK_OVERVIEW_PROMPT = '''
Imagine you are a linguist working on the {language} language. You are given the task of identifying Inverse Text normalzation variations and orthographic and normalized variations of words and expressions found in transcribed audio.

Spoken language often exhibits variability due to pronunciation, regional accents, and ambiguity in word boundaries. These variations can lead to multiple acceptable orthographic (written) and inverse text normalized (ITN) forms.

Inverse Text Normalization (ITN) refers to converting spoken or phonetically transcribed content into its standard written form. For example, “पच्चीस डॉलर” (in Hindi) can be normalized as:

✅ $25  
✅ 25 dollars  
✅ twenty-five dollars  
पच्चीस डॉलर, पच्चीस dollar, 25 डॉलर (fully native, fully converted and a mix of the conversions) are all valid variations of the spoken form.

Therefore, if the model predicts a semantically valid output that differs orthographically or in ITN formatting from the reference, it should not be unfairly penalized. Evaluation should consider such acceptable variations as correct.

To address this, your task is to enumerate all plausible written forms that convey the same meaning or intent. These variations fall into two broad types:

Important Normalization Guidelines for All Categories

  1. Atomic Unit Handling
    - Always treat complete semantic units as a whole.
    - Never split expressions like "दो करोड़", "1 जनवरी 2024", or "₹/kg" to generate partial variations.
    - Do not duplicate variations by generating variations for the sub-parts again.
    - If a multi-word or structured atomic unit has already been normalized (like a full phone number, date, address, or expression), avoid generating individual variations for internal fragments such as digits or individual words.
    - For example, if the variation group ["3512-3456-7890-123", "३५१२-३४५६-७८९०-१२३"] is defined, do not generate ["तीन", "पांच", "एक"] etc. separately again within that context.
    - This ensures **no repetition of atomic units' subcomponents**, avoiding noisy or incorrect expansion.

  2. Number and Script Variations
    - Include digit and word-based forms: "दो लाख" → ["2 लाख", "दो lakh", "2 lakh"]
    - Include comma-separated and hyphenated versions: "200000", "2,00,000", "2-लाख", "दो-lakh"
    All combinations such as full native, full digits or numeric and mixed forms should be included.

  3. Permutations and Combinations
    - For numeric + unit expressions, generate all meaningful combinations:
      e.g., "दो करोड़" → ["2 करोड़", "दो crore", "2 crore", "दो करोड़"]
    - Apply combinations for currency, measurement, time, address, etc.
    - For expressions like "₹ प्रति किलो", create: ["₹/kg", "Rs per kg", "₹ per kilogram", "rupees/kg", "INR/kg"]
    You should also include variations that contains singular and plural forms, e.g., "₹ per kg" and "₹ per kgs", rupees per kg and rupees per kgs and all combinations of these variations.

  4. Capitalization and Casing Variants
    - Always include full casing permutations:
      - "House Number" → ["House Number", "house number", "HOUSE NUMBER", "House number", "house NUMBER", "house Number"]
      - "4 PM" → ["4 PM", "4Pm", "4pm", "4 p.m.", "4 P.M.", "04:00 PM", "04 PM"]
    - Apply this to all categories

  5. Symbol, Abbreviation & Hyphenation Variants
    - Cover all known forms, such as:
      - "₹ per kg" → ["₹/kg", "Rs/kg", "₹ per kilogram", "Rs-per-kg", "Rsperkg"]
      - "kmph" → ["km/h", "km/hr", "km per hour", "kilometers per hour", "kph"]
    - Include space, slash, hyphen, and no-separator versions where applicable.

  6. Contextual Word Order Variants
    - Include alternate phrasings:
      - "4 बजे शाम" → ["4 PM", "4 pm", "evening 4 o'clock", "04:00 PM"]
      - "1 जनवरी 2024" → ["January 1, 2024", "1st January 2024", "01/01/2024", "2024-01-01"]

  7. Redundancy Avoidance
    - Do not list internal fragments of structured expressions unless needed.
      e.g., Do not extract just "₹" from "₹/kg" or "House" from "House Number 12"

  8. Apply Across All Categories
    - These rules must be applied to each of the following:
      Cardinal numbers
        → Handle all integer-based expressions with digit/word variations and unit integration.
      Currency
        → Include Rs, ₹, INR, word/digit combinations, and relevant unit casing/spelling variants.
      Mathematics
        → Represent expressions like "पांच गुना दो", "3 times 5", "5 multiplied by 3", etc., with full structure.
      Loan words and code mixing
        → Support code-mixed expressions like "Address नंबर", "Post Office", "Internet Speed" in mixed scripts.
      Numeric/Alphanumeric
        → Cover formats like PIN codes, license numbers, IDs with letter-number mix and case variants.
      Website/Email/IP
        → Include lowercase, uppercase (if spoken emphatically), and remove/add www/http where logical.
      Names and Proper Nouns
        → Maintain correct capitalization across all permutations, e.g., "India", "INDIA", "india".
      Date and Time
        → Convert to multiple formats: full date, ISO, DD-MM-YYYY, spoken variations, 24h vs 12h clock.
      Ordinal numbers
        → Include both digit and word: "तीसरा" → ["3rd", "third"], "21वां" → ["21st", "twenty-first"]
      Decimal numbers
        → Support forms like "3.14", "तीन दशमलव एक चार", "three point one four", etc.
      Abbreviations and Acronyms
        → Generate spoken + written forms: "यूएन" → ["UN", "United Nations"], with casing variants ("U.N.", "un")

    9. Symbols like -,_, space can be considered equivalent in certain contexts. So generate all combinations of these variations like non-stop-eating, non_stop_eating, non stop eating, non-stop_eating, non-stop_eating, non-stop-eating, non_stop-eating, non_stop-eating, non stop-eating, non-stop eating, non stop eating, non_stop eating.

🔹 Note:
Always keep the actual word itself as one of the variations, even if it is not the most common or expected form. This ensures that the model's output is not penalized for using a less common but still valid form and it's important to capture the full range of possible variations for the native word too.


A. Inverse Text Normalization (ITN) Guidelines  
(Where normalized forms are expected in standard written English, using only English characters, digits, and symbols)
1. Cardinal numbers  
Covers whole numbers, including ordinals, decimals, and fractions — particularly multi-word spoken forms that collectively indicate a single numeric concept.  
    Identify and group contiguous spoken tokens that together represent a number and treat them as a single unit  
    Generate variations only for the full numeric expression, not its partial subcomponents  
    Capture valid digit-based, word-based, and hybrid forms, preserving the semantic quantity they express  

2. Currency  
Covers variations in currency symbols, abbreviations, and word ordering.  
    Include symbol-based (₹, $, etc.), abbreviation-based (Rs., USD), and hybrid forms (INR 10, 10₹)  

3. Mathematics  
Covers percentages, powers, measurements, and unit-based values.  
    Include usage of symbols like %, ^2, /, -, etc.  
    Normalize to all acceptable symbolic formats (e.g., 70%, 10^2, Rs/kg)  
    Consider spelled-out or abbreviated units, with or without spacing  
    Accept all correct representations like 20kg, 20 kg, 20 kilograms  
    Allow variations such as 10-15, 10 to 15, 10–15 for ranges and lists  

4. Loan words and code mixing  
Covers spelling deviations caused by regional pronunciation and code-mixed usages.  
    Include all plausible English-script variations, even if differently pronounced (e.g., Laptop, Labtop, Laptaap)  
    

5. Numeric/Alphanumeric  
Covers phone numbers, identifiers, and other digit/letter-based formats.  
    Consider grouping and separator variations  
    Accept formats like 9876543210, 98 76 543 210, 98-76-543-210  

6. Website/Email/IP  
Covers spoken forms like “at”, “dot”, and inclusion of protocols for digital identifiers.  
    Normalize to syntactically correct formats like user@example.com, www.example.com  
    Convert spoken forms using “dot”, “at” into their symbolic equivalents  

7. Names and Proper Nouns  
Covers named entities including people, places, and organizations.  
    Do not retain fully native-script representations in the output  
    Avoid mixing native and English styles in proper nouns and treat them distinctly when found in spoken form  

8. Date and Time  
Covers multiple date formats and spoken time expressions.  
    Include all standard date formats (e.g., January 1, 2024, 01/01/2024, 2024-01-01)  
    Normalize time using either 12-hour format with AM/PM (e.g., 5:30 PM, 7 AM) or 24-hour format (e.g., 17:30, 07:00)  
    Avoid mixing native and English styles (e.g., do not retain forms like 5AM बजे)  
    Prefer standardized digital formats over spoken-style phrasing  

9. Ordinal numbers  
Included under numeric expressions but refer specifically to ordered items.  
    Normalize such expressions to standard forms like 1st, 2nd, 3rd  
    Treat these as distinct from cardinal number variants where applicable  

10. Decimal numbers  
Covers expressions with fractional numeric content.  
    Identify spoken decimals and normalize them using a dot as the decimal separator  
    Capture and preserve semantic meaning while maintaining correct notation  

11. Abbreviations and Acronyms  
Covers fully spelled or letter-by-letter spoken sequences.  
    Represent using standard uppercase forms (e.g., USA, IBM)  
    Normalize letter sequences with or without dots into consistent representations  

B. Orthographic Variation Guidelines  
(Primarily within native script)

1. Phonetic Variations  
Consider: Regional accents, dialects, or pronunciation differences.  
Action: Replace or modify letters/matras to reflect alternative pronunciations.

2. Splitting Compound Words  
Consider: Whether a compound word can be split into its constituent parts.  
Action: Decompose the word and list meaningful segments.

3. Merging Two Words  
Consider: Cases where two separate words can logically form one compound word.  
Action: Combine words to form a single, valid variation.

4. Matra and Diacritic Variations  
Consider: Alternate matras or diacritical marks (e.g., nukta in Hindi, pulli in Tamil).  
Action: Add, remove, or adjust matras and diacritics accordingly.

5. Spelling Variations for Loaned Words
Consider: Loanwords from Sanskrit, English, Persian, or other languages often have multiple recognized spellings.
Action: List all plausible forms, including transliterations and localized versions.

6. Ligature Variations  
Consider: Some scripts allow consonants to appear as ligatures or separate characters.  
Action: Provide versions both with and without ligatures.


Your output should include all valid variations per category that reflect meaning-preserving transformations. This ensures accurate, fair evaluation of spoken-to-written model outputs.
'''


TASK_INSTRUCTION_PROMPT='''
Rules that need to be strictly followed -
1. The number of elements in the list should be equal to the number of words in the sentence, unless you decide the split the word into two words.
2. Do not generate duplicates.
3. If you have doubt whether the variation is correct or not, generate it.
4. Exhaust all possible variations of the word, do not miss anything. 
Input Format:
Language: {language}
Sentence: <the sentence will be provided here>
Output Format:
Return a list of lists containing variations, if present, for each word in the sentence.
'''

GUIDELINES_PROMPT = {}
GUIDELINES_PROMPT['Hindi']='''
Here are a few guidelines of variations with examples -

A.  Inverse Text Normalization (ITN) Guidelines-
1. Cardinal numbers  
बयासी लाख चौबीस हज़ार छह सौ तैंतीस -> [
  "824633", "82,46,33", "824,633",
  "eighty-two lakh twenty-four thousand six hundred thirty-three",
  "eight two lakh two four thousand six three three",
  "बयासी लाख चौबीस हज़ार छह सौ तैंतीस",
  "82 लाख 46 हज़ार 33",
  "eighty two lakh 24 thousand 633", 
  "82 lakh 24 thousand 633",
  "824 हजार 633",
  "82 लाख 24000 छह सौ तैंतीस", "eighty-two lakh 24000 six hundred thirty-three",
  "८२ लाख २४००० छह सौ तैंतीस",
  "82 लाख 24 हज़ार 6 3 3",
  "eighty-two lakh 24000",
  "824 हजार 6 सौ 33"
]

ग्यारह करोड़ पांच लाख पचहत्तर हज़ार -> [
  "110575000", "11,05,75,000", "110,575,000",
  "eleven crore five lakh seventy-five thousand",
  "one one zero five seven five zero zero zero",
  "ग्यारह करोड़ पांच लाख पचहत्तर हज़ार",
  "11 करोड़ 5 लाख 75 हज़ार",
 "11 crore 5 lakh 75000",
  "110 लाख 575 हजार", "110 मिलियन", "eleven crore 75 hazar",
  "11 cr 5 lac 75k", "eleven cr 5 lac 75 thousand",
  "eleven cr 5 लाख",
  "eleven करोड़ पांच लाख पचहत्तर हज़ार",
 
]

2. Ordinal numbers  
पहला -> [
  "1st", "first", "1 st", "1-st", "1ˢᵗ", "01st",
  "one st", "the 1st", "the first", "number one",
  "पहला",
  "1ला", "1 ला", "01 ला"
]

इक्कीसवां -> [
  "21st", "twenty-first", "21 st", "21-st", "twenty first",
  "2 1st", "twentyone st", "the 21st", "the twenty-first", "number twenty-one",
  "इक्कीसवां", 
  "21 वां", "21वां" ]

3. Decimal numbers  

तीन दशमलव पाँच -> [
  "तीन दशमलव पाँच", 
  "3.5", "3.50", "3½", "3 1/2",
  "three point five", "three dot five", "three and a half",
  "3 .5", "3. 5", "3 . 5", "3 • 5", "3·5", "03.5"
]

एक दशमलव पचहत्तर -> [
  "एक दशमलव पचहत्तर", "१ दशमलव ७५", "१ दशमलव पचहत्तर",
  "1.75", "1.750", "1¾", "1 3/4",
  "one point seven five", "one dot seventy five", "one and three quarters",
  "1 .75", "1. 75", "1 • 75", "1·75", "01.75"
]

एक दशमलव पाँच मीटर -> [
  "एक दशमलव पाँच मीटर", "१ दशमलव ५ मीटर", "एक दशमलव ५ मीटर", "१ दशमलव पाँच मीटर",
  "1.5 m", "1.5m", "1.50 m", "1.50m",
  "1 1/2 meters", "1½ meters", "one point five meters",
  "one and a half meters", "1.5 meter", "1½ meter", "one point five m",
  "1.5 मीटर", "1.50 मीटर", "1½ m", "1.5 M", "1.50 M",
  "1 .5 m", "1. 5 m", "1 • 5 m", "1·5m", "01.5m"
]

4. Currency  

दस रुपये -> [
  "दस रुपये", "१० रुपये", "₹१०", "₹10", "Rs. 10", "Rs 10", "Rs10", "10 Rs.", "10Rs", "10 Rs", 
  "INR 10", "INR10", "10 INR", "10INR", "₹ 10", "10 ₹", "10₹", "₹ दस", "₹ दस रुपये",
  "दस Rs", "दस INR", "Rs दस", "INR दस", "Rs. दस", "INR. दस", "INR दस रुपये", "Rs दस रुपये",
  "₹ १०", "१० ₹", "१०₹", "INR १०", "Rs १०", "10 रूपये", "10 रुपयें"
]

पाँच डॉलर -> [
  "पाँच डॉलर", "५ डॉलर", "$5", "$ 5", "5$", "5 USD", "USD 5", "USD5", "5Dollar", "5 Dollar", 
  "Dollar 5", "5 dollars", "dollars 5", "५$", "५ $", "$५", "५ USD", "USD ५", 
  "$ पाँच", "$ पाँच डॉलर", "पाँच USD", "डॉलर ५", "USD पाँच", "USD पाँच डॉलर",
  "USD5", "USD-5", "$05", "05 USD", "पाँच$", "पाँच $", "डॉलर पाँच"
]


5. Mathematics

सत्तर प्रतिशत -> [
  "सत्तर प्रतिशत", "७० प्रतिशत", "70%", "70 %", "%70", "percent 70", "70 percent", 
  "seventy percent", "seventy%", "percent seventy", "seventy %", 
  "सत्तर %", "% सत्तर", "७० %", "७०%", "percent सत्तर", "७० percent"
]

दस स्क्वायर -> [
  "दस स्क्वायर", "१० स्क्वायर", "10^2", "10 ^ 2", "10²", "10 raised to 2", "10 to the power 2", 
  "square of 10", "10 raised 2", "10 ^2", "10^ 2", "10 ** 2", "१०^२", "१० ^ २", "१०²", 
  "१० to the power 2", "दस ^ 2", "स्क्वायर ऑफ दस", "दस raised to 2"
]

दस से पंद्रह -> [
  "दस से पंद्रह", "१० से १५", "10-15", "10–15", "10 — 15", "10 - 15", "10 to 15", "10 upto 15", 
  "10 through 15", "range from 10 to 15", "१०–१५", "१० - १५", "१० upto १५", "range 10 to 15", 
  "१० से पंद्रह", "दस–पंद्रह"
]

बीस किलो -> [
  "बीस किलो", "२० किलो", "20kg", "20 kilograms", "20 kg", "20 kilo", "20 kilogram", "20 kgs", 
  "twenty kilograms", "twenty kg", "20 Kg", "20KG", "२०kg", "२० kg", "२० किलो", "बीस kg", 
  "kg बीस", "20 किलो", "20 किलोग्राम", "२० किग्रा", "२० KG"
]

एक सौ पचास एम एल -> [
  "एक सौ पचास एम एल", "१५० एम एल", "150ml", "150 ml", "150 milliliters", "150 millilitre", 
  "150 mL", "150 ML", "one hundred fifty ml", "one fifty ml", "१५०ml", "१५० ml", "१५० एमएल", 
  "150 एमएल", "१५० मि.ली.", "एम एल १५०", "एक सौ पचास ml", "१५० mL", "१५० ML", "150 एम एल"
]

पचास प्लस बीस प्लस तीस -> [
  "पचास प्लस बीस प्लस तीस", "५० प्लस २० प्लस ३०", "50 + 20 + 30", "50+20+30", "50 +20 +30", 
  "50+ 20+ 30", "50 plus 20 plus 30", "50 plus20 plus30", "50+20 +30", "50 + 20+30", 
  "५०+२०+३०", "५० + २० + ३०", "५० plus २० plus ३०", "पचास+बीस+तीस", "५० plus 20 plus तीस", 
  "50 प्लस 20 प्लस तीस"
]

छह गुणा चार -> [
  "छह गुणा चार", "६ गुणा ४", "6 x 4", "6*4", "6 * 4", "6 x4", "6x4", "6 multiplied by 4", 
  "6 times 4", "six times four", "six multiplied by four", "६x४", "६ * ४", "६x4", "6 गुणा 4", 
  "६ times 4", "छह x चार", "गुणा of 6 and 4"
]


6. Loan words and code mixing

गूगल पे -> [
  "गूगल पे", "गूगल पे ऐप", "Google Pay", "google pay", "GooglePay", "googlepay",
  "G Pay", "G-Pay", "g pay", "gpay", "Gpay", "gPay", "G Pay App",
  "Googel Pay", "Googl Pay", "G-pay", "G Pay.", "Gpay App", "Google pay app",
  "गूगल पे (Google Pay)", "Google पे", "गूगल Pay", "G पे", "गूगल-Pay"
]

व्हाट्सएप -> [
  "व्हाट्सएप", "WhatsApp", "whatsapp", "WHATSAPP", "Watsap", "watsapp", "Whats App",
  "Whats app", "whats app", "Whatsaap", "Whatsaap", "What’sApp", "WhatApp", "Whtsapp",
  "Vatsapp", "व्हाट्स एप", "व्हाट्सअप", "Whats•App", "whats-ap", "Whats_App", "Whats App Msg",
  "व्हाट्सएप (WhatsApp)", "Whats एप", "व्हाट्सApp", "व्हाट्सअप्प"
]

लैपटॉप -> [
  "लैपटॉप", "Laptop", "laptop", "LAPTOP", "Lap top", "lap top", "Labtop", "Laptap", "Laptaap",
  "Laptob", "Laptopp", "Laptoop", "Lptop", "Lap_top", "Laptop.", "Laptop device",
  "लैपटॉप (Laptop)", "Laptop सिस्टम", "Lap-Top", "Laptop कंप्यूटर"
]

ए टी एम -> [
  "ए टी एम", "एटीएम", "ATM", "atm", "ATM machine", "atm machine", "A T M", "A.T.M.", "A.T.M",
  "a t m", "Atm", "Ateeem", "Aiyateeum", "ए टी एम मशीन", "ATM मशीन", "ATM Machine",
  "A-T-M", "ATM (एटीएम)", "ए-टी-एम", "ए टी एम डिवाइस"
]

मैसेज -> [
  "मैसेज", "Message", "message", "MSG", "msg", "Mesage", "Mesaj", "Mesaje", "Messege", "messg",
  "mssg", "msz", "massage (common typo)", "Message alert", "Text message", "Chat message",
  "SMS", "मैसेज (Message)", "txt msg", "MSG alert", "मैसेजिंग", "मैसेजbox", "msz box"
]

डॉक्टर -> [
  "डॉक्टर", "Doctor", "doctor", "DOCTOR", "Docter", "Dactor", "Daktarr", "Doctar", "Dr.", "dr",
  "DR", "Doc", "Dctr", "Daktar", "डॉ.", "डॉ", "Dr", "डॉक्टर साहब", "डॉ साहब", "Dr. Saab",
  "Doctor (डॉक्टर)", "डॉक्टर", "Dr (Doctor)"
]

होटल -> [
  "होटल", "Hotel", "hotel", "HOTEL", "Hotell", "Hotil", "Hotle", "Hutel", "Hotal", "Hoetl",
  "Htl", "Hotel Room", "Hotel stay", "Otel", "होटल (Hotel)", "Hotel रिज़र्वेशन", "होटल स्टे",
  "होटल में", "होटल•होटल", "H0tel"
]

पेज़ैप -> [
  "पेज़ैप", "Payzapp", "payzapp", "PAYZAPP", "Payzap", "Paizap", "Paysap", "Paysapp", "Peizap",
  "Payzaap", "PayZapp", "Pay Zap", "Pay-zap", "paysapp", "PayZAP", "पेज़ैप (Payzapp)",
  "Payzap App", "पेज़ैप ऐप", "पे-जैप", "पेज़ैप", "PayZ@pp"
]


7. Numeric/Alphanumeric

दो तीन चार पाँच छह सात आठ नौ शून्य -> [
  "दो तीन चार पाँच छह सात आठ नौ शून्य", "234567890", "२३४५६७८९०", "२३४-५६७-८९०",
  "23456 7890", "23456-7890", "23 45 67 89 0", "2 3 4 5 6 7 8 9 0", "२ ३ ४ ५ ६ ७ ८ ९ ०",
  "234-567-890", "2-3-4-5-6-7-8-9-0", "(234)567890", "234 567 890", "+91 234567890",
  "+९१ २३४५६७८९०", "(२३४)५६७८९०", "+91-234567890", "+९१-२३४५६७८९०",
  "nine digit number: 234567890", "234/567/890", "234•567•890", "234•567890", "२३४•५६७•८९०"
]

पाँच सौ सात एम जी रोड -> [
  "पाँच सौ सात एम जी रोड", "507 MG Road", "507 एम जी रोड", "507 एम.जी. रोड", "507, MG Rd.", 
  "507 MG Rd", "507 M G Road", "507 M.G. Road", "507 M G Rd", "507 M. G. Rd.", "507-MG-Road", 
  "507 MG-Road", "507, MG Road", "507MG Road", "507 MGRoad", "Flat 507 MG Road", 
  "House No. 507, MG Road", "507 MG रोड", "507 एम जी Rd.", "५०७ एम जी रोड", "५०७ MG Road",
  "५०७, एम.जी. रोड", "५०७-MG-Road", "५०७ एम जी आरडी", "५०७ MG-Rd.", "MG Road 507",
  "MG रोड 507", "MG-Road Flat 507", "507-M.G.-Road", "507 एम•जी•रोड", "House no. 507 MG Road",
  "507 एमजी रोड", "507 एम जी रोड़", "५०७ एम. जी. रोड", "507 एम•जी•Road"
]


8. Website/Email/IP

संपर्क एट संपर्क डॉट कॉम -> [
  "संपर्क एट संपर्क डॉट कॉम", "sampark@sampark.com", "sampark @ sampark.com", "sampark@sampark.in",
  "sampark@sampark.co.in", "sampark@sampark.org", "sampark123@sampark.com",
  "sampark at sampark dot com", "sampark at sampark dot in", "sampark at sampark dot co dot in",
  "sampark [at] sampark [dot] com", "sampark(at)sampark(dot)com", "sampark(at)sampark.com",
  "sampark (at) sampark (dot) com", "sampark (at) sampark.com", "sampark(at)sampark dot com",
  "sampark[at]sampark.com", "संपर्क@sampark.com", "sampark@संपर्क.com"
]

डब्ल्यू डब्ल्यू डब्ल्यू डॉट संपर्क डॉट कॉम -> [
  "डब्ल्यू डब्ल्यू डब्ल्यू डॉट संपर्क डॉट कॉम", "www.sampark.com", "www.sampark.in", "www.sampark.org",
  "sampark.com", "sampark.in", "sampark.org", "http://www.sampark.com", "https://www.sampark.com",
  "http://sampark.com", "https://sampark.com", "http://sampark.in", "https://sampark.in",
  "www . sampark . com", "w w w . sampark . com", "WWW.SAMPARK.COM", "WWW.SAMPARK.IN",
  "w w w . s a m p a r k . c o m", "www.sampark . com", "www . sampark.com", "sampark dot com",
  "www.sampark.co.in", "https://www.sampark.co.in", "डब्ल्यू डब्ल्यू डब्ल्यू.sampark.com"
]



9. Names and Proper Nouns

वाराणसी -> [
  "वाराणसी", "Varanasi", "varanasi", "VARANASI", "Varanasi.", "Varanasi ", " Varanasi", "Varanasi,", "वाराणसी (Varanasi)", "वाराणसी."
]

कर्नाटक -> [
  "कर्नाटक", "Karnataka", "karnataka", "KARNATAKA", "Karnataka.", "Karnataka ", " Karnataka", "कर्नाटक (Karnataka)", "कर्नाटक."
]

महात्मा गांधी -> [
  "महात्मा गांधी", "Mahatma Gandhi", "mahatma gandhi", "MAHATMA GANDHI", "Mahatma Gandhi.", "Mahatma Gandhi ", " Mahatma Gandhi",
  "महात्मा गांधी (Mahatma Gandhi)", "महात्मा गांधी."
]


10. Date and Time

एक जनवरी दो हजार चौबीस -> [
  "एक जनवरी दो हजार चौबीस", "1 जनवरी 2024", "01 जनवरी 2024", "1 जनवरी २०२४", "01 जनवरी २०२४",
  "01/01/2024", "1/1/2024", "01-01-2024", "1-1-2024", "2024-01-01", "2024/01/01", "2024.01.01", "01•01•2024",
  "January 1, 2024", "January 1st, 2024", "1 January 2024", "1st January 2024", "01 January 2024", "01 Jan 2024", "1 Jan 2024", "1st Jan 2024",
  "Jan 1, 2024", "Jan 1st, 2024", "Jan-01-2024", "1-Jan-2024", "1st-Jan-2024", "जनवरी 1, 2024", "जनवरी 1st, 2024", "जनवरी ०१, २०२४"
]

तीन जून दो हजार पच्चीस -> [
  "तीन जून दो हजार पच्चीस", "3 जून 2025", "03 जून 2025", "3 जून २०२५", "03 जून २०२५",
  "03/06/2025", "3/6/2025", "03-06-2025", "3-6-2025", "2025-06-03", "2025/06/03", "2025.06.03", "03•06•2025",
  "June 3, 2025", "June 3rd, 2025", "3 June 2025", "3rd June 2025", "03 June 2025", "03 Jun 2025", "3 Jun 2025", "3rd Jun 2025",
  "Jun 3, 2025", "Jun 3rd, 2025", "Jun-03-2025", "3-Jun-2025", "3rd-Jun-2025", "जून 3, 2025", "जून 3rd, 2025", "जून ०३, २०२५"
]

10. Date and Time - Time Variations

पाँच तीस पी एम -> \[
"5:30 PM", "5:30PM", "17:30", "05:30 PM", "1730", "5.30 PM", "5:30 p.m.", "5:30 pm",
"०५:३० PM", "१७:३०", "१७.३०", "१७३०", "५:३० पीएम", "५.३० पीएम", "५:३०", "५.३०",
"५ : ३०", "५ :३०", "५:३० बजे", "५:३०PM", "05:30", "शाम 5:30", "शाम पाँच तीस"
]

चार बजकर पैंतालीस मिनट -> \[
"4:45", "04:45", "quarter to five", "4.45", "4:45 AM", "0445",
"०४:४५", "४:४५", "०४४५", "४.४५", "चार पैंतालीस", "चार बजकर ४५ मिनट", "चार : ४५"
]

सुबह पाँच बजे -> \[
"5 AM", "05:00", "5:00 AM", "5am", "0500", "5.00 AM",
"०५:००", "५:००", "०५००", "५.००", "सुबह 5 बजे", "सुबह पाँच बजे", "५ बजे सुबह",
"5 बजे सुबह", "पाँच ए एम", "५ ए एम", "५am", "5 ए एम"
]

सत्रह तीस -> \[
"17:30", "5:30 PM", "1730", "17.30", "05:30 PM",
"१७:३०", "१७.३०", "१७३०", "५:३० पीएम", "५.३० पीएम"
]

शाम साढ़े सात बजे -> \[
"7:30 PM", "19:30", "0730 PM", "7.30 PM", "7:30 p.m.", "1930",
"१९:३०", "१९.३०", "१९३०", "७:३० पीएम", "०७:३०", "०७.३०", "७.३०",
"शाम 7:30", "शाम 7.30", "शाम  7:30 बजे", "शाम 7 : 30 बजे", "शाम ७:३०", "शाम ७.३०",
"शाम को साढ़े सात", "शाम साढ़े सात बजे", "शाम सात तीस", "शाम सात बजकर तीस मिनट",
"साढ़े सात बजे शाम", "शाम के समय ७:३०", "7:30 की शाम"
]

दोपहर एक बजे -> \[
"1 PM", "13:00", "1:00 PM", "1300", "01:00 PM", "1pm",
"१३:००", "०१:००", "१३००", "१:००", "१ पीएम", "१.००", "१pm", "एक बजे दोपहर",
"दोपहर 1 बजे", "1 बजे दोपहर"
]

रात के बारह बजे -> \[
"12 AM", "00:00", "12:00 AM", "0000", "12am", "12.00 AM",
"००:००", "००००", "१२:००", "१२am", "रात के 12 बजे", "रात बारह बजे", "१२ बजे रात",
"मध्यरात्रि १२:००", "१२ बजे एम"
]

पाँच बजे को -> \[
"5 बजे", "5:00", "05:00", "5.00", "5 o'clock", "5:00 AM", "0500",
"०५:००", "०५००", "५:००", "५ बजे", "५.००", "पाँच बजे को", "5 बजे को"
]

पाँच ए एम -> \[
"5 AM", "05:00", "5:00 AM", "5am", "0500", "5.00 AM",
"०५:००", "५:००", "०५००", "५.००", "पाँच ए एम", "५ ए एम", "५am", "5 ए एम"
]


11. Abbreviations and Acronyms  
यू एस ए -> [
  "USA", "U.S.A.", "U. S. A.", "U S A", "usa", "U-S-A", "U. S.A.", "U. S-a", "U S. A.", "U.S.A", "U. S.A",
  "U. S A", "U S.A", "U-S A", "U S-A", "यूएसए", "यू.एस.ए", "यू एस ए"
]

आई बी एम -> [
  "IBM", "I.B.M.", "I. B. M.", "I B M", "ibm", "I-B-M", "I. B.M.", "I.B. M.", "I. B. M", "I.B.M",
  "आईबीएम", "आई बी एम", "आई.बी.एम"
]

12. Roman Numerals  
रोमन संख्या पाँच -> [
  "V", "v", " V", "V ", "(V)", "[V]", "‘V’", "“V”", "{V}", "<V>", "V.", "V-", "-V-", "V/",
  "रोमन संख्या V", "रोमन संख्या v", "रोमन पाँच", "रोमन 5", "पाँच = V"
]

रोमन संख्या दस -> [
  "X", "x", " X", "X ", "(X)", "[X]", "‘X’", "“X”", "{X}", "<X>", "X.", "X-", "-X-", "X/",
  "रोमन संख्या X", "रोमन संख्या x", "रोमन दस", "रोमन 10", "दस = X"
]


13. Compound Units  

किलोमीटर प्रति घंटा -> [
  "km/h", "kmph", "km/hr", "kph", "kms/hr", "km-h", "km/hour", "km-per-hr", "km/hours",
  "km per hr", "km per hour", "kms per hour", "kilometers per hour", "kilometres per hour",
  "km an hour", "km every hour", "km per-hr", "km hourly", "speed in kmph", "speed of kmph",
  "किलोमीटर प्रति घंटा", "किमी प्रति घंटा", "किमी/घं", "किमी प्रति घं", "किमी/घंटा", "किमी-प्रति-घंटा",
  "किलोमीटर/घंटा", "किमी पर आवर", "km प्रति घंटा", "km प्रति hour", "km प्रति घं", "km प्रति h", "km प्रति h."
]

रुपया प्रति किलो -> [
  "₹/kg", "₹ per kg", "₹ per kilogram", "₹/kilogram", "₹ प्रति किलो", "₹ प्रति kg", "₹ प्रति कि.", "₹/कि.",
  "Rs/kg", "Rs per kg", "Rs per kilogram", "Rs for each kg", "Rs प्रति किलो", "Rs/किलो", "Rs प्रति kg",
  "Rs per kilo", "Rs/कि.", "Rs/कि.ग्रा.", "Rs प्रति कि.ग्रा.",
  "rupees per kilogram", "rupees/kg", "rupee per kg", "rupees each kg", "cost per kg in rupees",
  "rate per kg", "price per kg", "price per kg in Rs", "INR/kg", "INR per kg", "INR प्रति किलो"
]


B. Orthographic Variation Guidelines
Phonetic Variations -
[
    ["चाहिए", "चाहिये"],
    ["शुरुआत", "शुरुवात"],
    ["नर्म", "नरम"],
    ["जन्म", "जनम"],
    ["आए", "आये"],
    ["फल", "फ़ल"]
] 

Splitting Compound Words - 
[
    ["उत्तरप्रदेश", "उत्तर प्रदेश"],
    ["तमिलनाडु", "तमिल नाडु"],
    ["टोपीवाला", "टोपी वाला"],
    ["तुमसा", "तुम सा"],
    ["राम-जैसा", "राम जैसा"],
    ["पासबुक", "पास बुक"],
    ["डाउनलोड", "डाउन लोड"],
]

Merging Two Words -
[
    ["रेल गाड़ी", "रेलगाड़ी"],
    ["आस पास", "आसपास"],
    ["मेरे को", "मेरेको"],
    ["द्‍‌वि-अक्षर", "द्व्यक्षर"],
    ["द्‍‌वि-अर्थक", "द्व्यर्थक"],
    ["माता पिता", "माता-पिता"],
    ["मोबी क्विक", "मोबीक्विक"]
]

Matra and Dialectical Variations - 
[
    ["यहां", "यहाँ"],
    ["ज़िंदगी", "जिन्दगी"],
    ["क़िस्मत", "किस्मत"],
    ["सिलाई", "सिलायी"],
    ["छः", "छह"]
]

Spelling Variations for loaned words - 
[
    ["ऑक्सीजन", "ऑक्सिजन"],
    ["तनखाह", "तनख़्वाह"],
    ["आगाज़", "आग़ाज़"],
    ["इस्तिमाल", "इस्तेमाल"],
    ["दाग", "दाग़"],
    ["मुजफ्फरनगर", "मुज़्फ़्फ़नगर"],
    ["ऑर्गैनिक", "ऑर्गेनिक"],
    ["फ्लैक्स", "फ़्लेक्स"],
    ["अवन", "ओवन"],
    ["सैल्लो", "सेल्लो"]
]

Spelling Variations for loaned words - 
[
    ["ऑक्सीजन", "ऑक्सिजन"],
    ["तनखाह", "तनख़्वाह"],
    ["आगाज़", "आग़ाज़"],
    ["इस्तिमाल", "इस्तेमाल"],
    ["दाग", "दाग़"],
    ["मुजफ्फरनगर", "मुज़्फ़्फ़नगर"],
    ["ऑर्गैनिक", "ऑर्गेनिक"],
    ["फ्लैक्स", "फ़्लेक्स"],
    ["अवन", "ओवन"],
    ["सैल्लो", "सेल्लो"]
]

Ligature Variations -
[
    ["तत्व", "तत्त्व"],
    ["मैक्सिमम", "मैग्ज़िमम"]
]


'''

GUIDELINES_PROMPT['Malayalam']='''
Here are a few guidelines of variations with examples -
Phonetic Variations -
[
    ["വിദ്യാർത്ഥി", "വിദ്യാർഥി"],
    ["സർവം", "സർവ്വം"],
    ["അദ്ഭുതം", "അത്ഭുതം"],
    ["അയോധ്യ", "അയോദ്ധ്യ"],
    ["അധ്യാപകൻ", "അദ്ധ്യാപകൻ"],
    ["വലിയ", "വല്യ"]
]

Splitting Compound Words - 
[
    ["പ്രധാനമന്ത്രി", "പ്രധാന മന്ത്രി"],
    ["വാടകവീട്", "വാടക വീട്"],
    ["വിവാഹവസ്ത്രം", "വിവാഹ വസ്ത്രം"],
    ["ഗ്രാമസഭ", "ഗ്രാമ സഭ"],
    ["നാട്ടുവെളിച്ചം", "നാട്ടു വെളിച്ചം"],
    ["നാടൻപാട്ട്", "നാടൻ പാട്ട്"]
]

Merging Two Words -
[
    ["വിവാഹ സമ്മാനം", "വിവാഹസമ്മാനം"],
    ["ഓഹരി വിപണി", "ഓഹരിവിപണി"],
    ["ജല രേഖ", "ജലരേഖ"],
    ["പ്രാദേശിക വാര്‍ത്ത", "പ്രാദേശികവാര്‍ത്ത"],
    ["അങ്ങാടി മരുന്ന്", "അങ്ങാടിമരുന്ന്"],
    ["തെരുവ് വിളക്ക്", "തെരുവുവിളക്ക്"],
    ["വടക്കൻ പാട്ട്", "വടക്കൻപാട്ട്"]
]

Matra and Dialectical Variations - 
[
    ["അവന്", "അവനു"],
    ["കുറച്ച്", "കുറച്ചു"],
    ["കയ്യിൽ", "കൈയിൽ"],
    ["ഉത്പന്നം", "ഉൽപന്നം", "ഉല്പന്നം"],
    ["ഉൽപന്നം", "ഉല്പന്നം"],
    ["നല്കുന്ന", "നൽകുന്ന"]
]

Spelling Variations for loaned words - 
[
    ["ഓഫീസ്", "ആഫീസ്"],
    ["ഗവണ്മെന്‍", "ഗവര്‍മെണ്ട്"],
    ["കോര്‍പറേഷന്‍", "കാര്‍പറേഷന്‍"],
    ["സ്കൂള്‍", "ഇസ്കൂള്‍"],
    ["ഖുറാന്‍", "ഖുര്‍ ആന്‍"],
    ["സർവീസ്", "സർവ്വീസ്"],
    ["സ്കൂൾ", "സ്ക്കൂൾ"],
    ["സ്വിമ്മിങ്ങ്", "സ്വിമ്മിംഗ്"],
    ["കങ്കാരു", "കംഗാരു"],
    ["ടു", "റ്റു"]
]

Ligature Variations -
[
    ["ൻറെ", "ൺ്റെ"],
    ["അവൻറെ", "അവൻ്റെ"],
    ["ക്‌ത", "ക്ത"],
    ["രക്‌തം", "രക്തം"],
    ["ത്​മ", "ത്മ"],
    ["ആത്​മാവ്", "ആത്മാവ്"],
    ["ശ്‌ച", "ശ്ച"],
    ["ആശ്‌ചര്യം", "ആശ്ചര്യം"],
    ["ന്‌ധ", "ന്ധ"],
    ["ബന്‌ധം", "ബന്ധം"]
]
'''

GUIDELINES_PROMPT['Bengali']='''
Here are a few guidelines of variations with examples -
Phonetic Variations -
[
    ["গেছিল", "গিয়েছিল", "গিয়েছিলো"],
    ["কেনো", "কেন"],
    ["ছোটো", "ছোট"],
    ["বলেছিলো", "বলেছিল"]
]

Splitting Compound Words - 
[
    ["পশ্চিমবঙ্গ", "পশ্চিম বঙ্গ"],
    ["মধ্যপ্রদেশ", "মধ্য প্রদেশ"],
    ["হৃদযন্ত্র", "হৃদ যন্ত্র"],
    ["নোটবুক", "নোট বুক"],
    ["জন্মতারিখ", "জন্ম তারিখ"]
]

Merging Two Words -
[
    ["আম গাছ", "আমগাছ"],
    ["তার পরে", "তারপরে"],
    ["ক্যামেরাবন্দি", "ক্যামেরা বন্দি"],
    ["এ বার", "এবার"]
]

Matra and Dialectical Variations - 
[
    ["এখনো", "এখনও"],
    ["আরো", "আরও"],
    ["পুরনো", "পুরোনো"],
    ["নম্বর", "নাম্বার"]
]

Spelling Variations for loaned words - 
[
    ["খ্রিষ্টান", "খৃষ্টান"],
    ["রিকশা", "রিক্সা"],
    ["উচিৎ", "উচিত"],
    ["খ্রিষ্টাব্দ", "খৃষ্টাব্দ"],
    ["পেনসিল", "পেন্সিল"],
    ["পর্দানশীন", "পরদানশীন"],
    ["সঙ্গীত", "সংগীত"],
    ["অলঙ্কার", "অলংকার"],
    ["দার্জিলিং", "দার্জিলিঙ"]
]

Ligature Variations -
[
    ["বিষ্ণু", "বিষণু"],
    ["ধর্ম", "ধরম"],
    ["কর্ম", "করম"],
    ["কিন্তু", "কিনতু"],
    ["ত্রিশ", "তিরিশ"],
    ["বন্ধু", "বনধু"]
]
'''

GUIDELINES_PROMPT['Gujarati']='''
Here are a few guidelines of variations with examples -
Phonetic Variations -
[
    ["મોકલીએ", "મોકલીયે"],
    ["લાવીએ", "લાવીયે"],
    ["અઠવાડીએ", "અઠવાડિયે"]
]

Splitting Compound Words - 
[
    ["મધ્યપ્રદેશ", "મધ્ય પ્રદેશ"],
    ["ગાંધીકથા", "ગાંધી કથા"],
    ["શતાબ્દીપર્વ", "શતાબ્દી પર્વ"]
]

Merging Two Words -
[
    ["કન્યા શાળા", "કન્યાશાળા"],
    ["અભ્યાસ ખંડ", "અભ્યાસખંડ"],
    ["જ્યોતિ કળશ", "જ્યોતિકળશ"]
]

Matra and Dialectical Variations - 
[
    ["કૉચ", "કોચ"],
    ["ડૉક્ટર", "ડોક્ટર"],
    ["ક્રૌંચ", "ક્રોંચ"]
]

Spelling Variations for loaned words - 
[
    ["ઓક્સફર્ડ", "ઓક્ષફર્ડ"],
    ["બોક્સિંગ", "બોક્ષિન્ગ"],
    ["ઝેરોક્સ", "ઝેરોક્ષ"]
]

Ligature Variations -
[
    ["સંગીત ઉત્સવ", "સંગીતોત્સ્વ"],
    ["મત અનુસાર", "મતાનુસાર"],
    ["રામ ઈશ્વર", "રામેશ્વર"]
]
'''

GUIDELINES_PROMPT['Kannada']='''
Here are a few guidelines of variations with examples -
Phonetic Variations -
[
    ["ಗಿಳಿ", "ಗಿಣಿ"],
    ["ನಾನ್ನೂರು", "ನಾನೂರು"],
    ["ಕಲಶ", "ಕಳಶ"],
    ["ಅರಶಿನ", "ಅರಸಿನ", "ಅರಿಶಿನ", "ಅರಿಸಿನ"],
    ["ಈರುಳ್ಳಿ", "ನೀರುಳ್ಳಿ"],
    ["ಯಾಕೆಂದ್ರೆ", "ಏಕೆಂದ್ರೆ"],
    ["ಯುಗಾದಿ", "ಉಗಾದಿ"],
    ["ಒಸಡು", "ವಸಡು"],
    ["ಜವುಗು", "ಜೌಗು"],
    ["ಜಿರಲೆ", "ಜಿರಳೆ"]
]

Splitting Compound Words - 
[
    ["ಹರಿಹರ", "ಹರಿ ಹರ"],
    ["ತಮಿಳ್ನಾಡು", "ತಮಿಳ್ ನಾಡು"],
    ["ಕ್ಷೀರಕ್ರಾಂತಿ", "ಕ್ಷೀರ ಕ್ರಾಂತಿ"],
    ["ವಟವೃಕ್ಷ", "ವಟ ವೃಕ್ಷ"],
    ["ಪಕ್ಷಿಸಂಕುಲ", "ಪಕ್ಷಿ ಸಂಕುಲ"]
]

Merging Two Words -
[
    ["ಜೀವನ ಶೈಲಿ", "ಜೀವನಶೈಲಿ"],
    ["ತಲೆ ನೋವು", "ತಲೆನೋವು"],
    ["ಹುಳು ಹುಪ್ಪಟೆ", "ಹುಳುಹುಪ್ಪಟೆ"],
    ["ದಿಕ್ಕು ದೆಸೆ", "ದಿಕ್ಕುದೆಸೆ"],
    ["ಸರಿ ಹೊಂದು", "ಸರಿಹೊಂದು"],
    ["ಹೊಟ್ಟೆ ಹೊರೆ", "ಹೊಟ್ಟೆಹೊರೆ"]
]

Matra and Dialectical Variations - 
[
    ["ಸರಿ", "ಸಾರಿ"],
    ["ವಾಪಸ್ಸು", "ವಾಪಸ್", "ವಾಪಾಸ್", "ವಾಪಸು"],
    ["ಬಾಣಲೆ", "ಬಾಣಲಿ"],
    ["ಚಂದ", "ಚೆಂದ"],
    ["ಇವಾಗ", "ಈವಾಗ"],
    ["ಹಸಿರು", "ಹಸುರು"],
    ["ಕುಯ್ಯಿ", "ಕೊಯ್ಯಿ"],
    ["ಅಂತಾರೆ", "ಅನ್ತಾರೆ"],
    ["ಕತೆ", "ಕಥೆ"],
    ["ಗಳಿಗೆ", "ಘಳಿಗೆ"],
    ["ಏಸು", "ಯೇಸು"],
    ["ಜೈಕಾರ", "ಜಯಕಾರ"],
    ["ಹೂಂ", "ಹ್ಞೂ"]
]

Spelling Variations for loaned words - 
[
    ["ಟೊಮೆಟೊ", "ಟೊಮ್ಯಾಟೋ", "ಟೊಮೊಟ", "ಟೊಮಾಟೊ", "ಟಮ್ಟೆ"],
    ["ಆ್ಯಕ್ಸಿಸ್", "ಆಕ್ಸಿಸ್", "ಎಕ್ಸಿಸ್"],
    ["ಪೈಂಟ್", "ಪೆಯಿಂಟ್", "ಪೇಂಟ್", "ಪೆಯ್ನ್ಟ್"],
    ["ಶಾಪಿಂಗ್", "ಷಾಪಿಂಗ್", "ಶಾಪ್ಪಿಂಗ್", "ಷಾಪ್ಪಿಂಗ್"],
    ["ಶರ್ಬತ್", "ಶರಬತ್"],
    ["ತಾರೀಕು", "ತಾರೀಖು"],
    ["ಬಿರಿಯಾನಿ", "ಬಿರ್ಯಾನಿ"]
]

Ligature Variations -
[
    ["ರ್ಯ", "ರ‍್ಯ"],
    ["ಶೌರ್ಯ", "ಶೌರ‍್ಯ"],
    ["ಕಾರ್ಯ", "ಕಾರ‍್ಯ"],
    ["ಸೂರ್ಯ", "ಸೂರ‍್ಯ"]
]

Sandhi rules -
[
    ["ಏನು ಆಗಬೇಕು", "ಏನಾಗಬೇಕು"],
    ["ಬೇಸಿಗೆ ಕಾಲ", "ಬೇಸಿಗೆಗಾಲ"],
    ["ನಾಲ್ಕು ಐದು", "ನಾಲ್ಕೈದು"],
    ["ಸರಿ ಇರಲಿಲ್ಲ", "ಸರಿಯಿರಲಿಲ್ಲ"],
    ["ವಿದ್ಯುತ್ ಶಕ್ತಿ", "ವಿದ್ಯುಚ್ಛಕ್ತಿ"],
    ["ಹಳೆ ಕನ್ನಡ", "ಹಳೆಗನ್ನಡ"]
]
'''

GUIDELINES_PROMPT['Marathi']='''
Here are a few guidelines of variations with examples -
Phonetic Variations -
[
    ["ह्या", "या"],
    ["मध्ये", "मधे"],
    ["राह्यला", "राहिला"],
    ["म्हणलं", "म्हटलं"],
    ["पायी", "पाई"],
    ["घेवून", "घेऊन"]
]

Splitting Compound Words - 
[
    ["उत्तरप्रदेश", "उत्तर प्रदेश"],
    ["तमिलनाडु", "तमिल नाडु"],
    ["टोपीवाला", "टोपी वाला"]
]

Merging Two Words -
[
    ["आई बाबा", "आईबाबा"],
    ["भाऊ बहीण", "भाऊबहीण"],
    ["नाटक वेडा", "नाटकवेडा"]
]

Matra and Dialectical Variations - 
[
    ["इथं", "इथे"],
    ["तिथं", "तिथे", "तेथे"],
    ["यामधनं", "यामधून"],
    ["तिथनं", "तिथून"],
    ["असं", "असे"]
]

Spelling Variations for loaned words - 
[
    ["ओव्हन", "अवन"],
    ["सिस्टीम", "सिस्टम"],
    ["प्रॉडक्ट", "प्रोडक्ट"],
    ["व्हिडिओ", "विडिओ"],
    ["युनिव्हर्सिटी", "युनिवर्सिटी"]
]

Sandhi rules -
[
    ["सूर्य अस्त", "सूर्यास्त"],
    ["मत अनुसार", "मतानुसार"],
    ["राम ईश्वर", "रामेश्वर"],
    ["जगत जननी", "जगज्जननी"],
    ["घन आनंद", "घनानंद"]
]
'''

GUIDELINES_PROMPT['Odia']='''
Here are a few guidelines of variations with examples -
Phonetic Variations -
[
    ["ଇଏ", "ଯେ"],
    ["ଯାଙ୍କ", "ଆଙ୍କ"],
    ["ନର୍ମ", "ନରମ"],
    ["ଜନ୍ମ", "ଜନମ"],
    ["ପିଲାଏ", "ପିଲାୟେ"],
    ["ଏଠି", "ଏଇଠି"],
    ["ଏହି", "ଏଇ"],
    ["ଦେବ ଲୋକ", "ଦେବଲୋକ"],
    ["ରିକ୍‌ସା", "ରିକ୍ସା"]
]

Splitting Compound Words - 
[
    ["ଉତ୍ତରପ୍ରଦେଶ", "ଉତ୍ତର ପ୍ରଦେଶ"],
    ["ସମୁଦ୍ରପତନ", "ସମୁଦ୍ର ପତନ"],
    ["ଜୀବନଚକ୍ର", "ଜୀବନ ଚକ୍ର"],
    ["ଦେଶବାସୀ", "ଦେଶ ବାସୀ"],
    ["ଆତ୍ମକଥା", "ଆତ୍ମ କଥା"]
]

Merging Two Words -
[
    ["ରେଳ ଗାଡ଼ି", "ରେଳଗାଡ଼ି"],
    ["ଆଖ ପାଖ", "ଆଖପାଖ"],
    ["ଦିନ ରାତି", "ଦିନରାତି"],
    ["ମନ ଇଚ୍ଛା", "ମନଇଚ୍ଛା"],
    ["ଆଦି ଶକ୍ତି", "ଆଦିଶକ୍ତି"]
]

Matra and Dialectical Variations - 
[
    ["ନାଇଁ", "ନାହିଁ"],
    ["ଜ୍ଞାନ", "ଗ୍ୟାନ"],
    ["ହାଏ", "ହାଇ"],
    ["ଉତ୍‌ଥାନ", "ଉତ୍ଥାଉ"],
    ["ଅନ୍ନପୂର୍ଣ୍ଣା", "ଅର୍ଣ୍ଣପୁର୍ଣ୍ଣା"]
]

Spelling Variations for loaned words - 
[
    ["ବ୍ୟାଙ୍କ", "ବେଙ୍କ"],
    ["ଅକ୍ସିଜେନ୍", "ଅକ୍‌ସିଜେନ"],
    ["ମଟର", "ମୋଟର"],
    ["ଟିକସ", "ଟ୍ୟାକ୍ସ"],
    ["ପୋଲିସ", "ପୁଲିସି"]
]

Ligature Variations -
[
    ["ଶାଶୂ", "ଶାଶୁ"],
    ["ବଂଗ", "ବଙ୍ଗ"],
    ["ଶଙ୍ଖ", "ଶଂଖ"]
]
'''

GUIDELINES_PROMPT['Tamil']='''
Here are a few guidelines of variations with examples for both the categories-

A:

Numbers -
ஓர் நூறு -> ["100", "one hundred"],
இருபத்தொன்று -> ["21", "twenty one"],
மூன்று புள்ளி ஐந்து -> ["3.5", "3.50"],
ஒன்று புள்ளி ஏழு ஐந்து -> ["1.75", "1 3/4"],

Currencies -
பத்து ரூபாய் -> ["₹10", "Rs. 10", "INR 10", "10₹"],
ஐந்து டாலர் -> ["$5", "5 USD", "USD 5"],

Dates -
ஜனவரி ஒன்று இரண்டாயிரத்து இருபத்து நான்கு -> ["January 1, 2024", "01/01/2024", "2024-01-01", "1 January 2024"],
மூன்றாம் ஜூன் இருபத்தைந்து -> ["3 June 2025", "03/06/2025", "June 3, 2025"],

Time -
ஐந்து முப்பது பி எம் -> ["5:30 PM", "5:30PM", "17:30"],
நான்கு கால் மணி -> ["3:45", "03:45"],

Phone Numbers -
இரண்டு மூன்று நான்கு ஐந்து ஆறு ஏழு எட்டு ஒன்பது பூஜ்யம் -> ["234567890", "23456 7890", "23456-7890"],

Addresses -
ஐந்து ஒ ஏழு எல்எம் வீதி -> ["507 Elm Street", "507, Elm St.", "507 Elm St"],

Measurements -
இருபது கிலோ -> ["20kg", "20 kilograms", "20 kg"],
நூறு ஐம்பது எம் எல் -> ["150ml", "150 ml", "150 milliliters"],
ஒன்று புள்ளி ஐந்து மீட்டர் -> ["1.5 m", "1.5m", "1 1/2 meters", "1.5 meter"],

Percentages -
எழுபது சதவீதம் -> ["70%", "seventy%"],

Fractions and Ranges -
பத்து ஸ்கொயர் -> ["10^2", "10²", "10 ^ 2"],
பத்து முதல் பதினைந்து -> ["10-15", "10 to 15", "10–15"],

Emails and URLs -
உதவி அட் உதவி டாட் காம் -> ["udavi@udavi.com", "udavi@udavi.in"],
டப்யூ டப்யூ டப்யூ டாட் உதவி டாட் காம் -> ["www.udavi.com", "http://www.udavi.com"],

Abbreviations -
யு எஸ் ஏ -> ["USA", "U.S.A."],
ஐ பி எம் -> ["IBM", "I.B.M."],

Roman Numerals -
ரோமன் எண் ஐந்து -> ["V"],
ரோமன் எண் பத்து -> ["X"],

Compound Units -
கிலோமீட்டர் பர ஹவர் -> ["km/h", "kmph", "km per hr"],
ரூபாய் பர கிலோ -> ["₹/kg", "Rs/kg", "Rs per kg"],

Loan Words -
கூகுள் பே -> ["Google Pay", "GPay"],
வாட்ஸ்அப் -> ["WhatsApp", "Watsap", "Vatsapp"],
லேப்டாப் -> ["Laptop", "Labtop", "Laptap", "Laptaap"],
ஏ டி எம் -> ["ATM", "A T M", "Ateeem", "Aiyateeum"],
மேசேஜ் -> ["Message", "Mesage", "Mesaj", "Mesaje"],
டாக்டர் -> ["Doctor", "Docter", "Dactor", "Daktarr"],
ஹோட்டல் -> ["Hotel", "Hutel", "Ootel"],
பேசப்பே -> ["Payzapp", "Payzap", "Paizap", "Paysap", "Paysapp"]

B: 
Phonetic Variations -
[
    ["போகவேண்டும்", "போகவேணும்", "போகணும்", "போகோணும்", "போணும்"],
    ["உட்கார்ந்து", "உக்காந்து", "உட்காந்து"],
    ["உடைந்து", "ஒடிந்து"],
    ["கேட்கும்", "கேக்கும்"],
    ["வெட்கம்", "வெக்கம்"],
    ["சயனம்", "ஷயனம்"],
    ["கோவில்", "கோயில்"],
    ["முன்னூறு", "முந்நூறு"],
    ["மவுனம்", "மௌனம்"],
    ["அவ்வை", "ஔவை"],
    ["அக்ரகாரம்", "அக்ரஹாரம்"],
    ["சிகப்பு", "சிவப்பு"]
]

Splitting Compound Words - 
[
    ["சொல்லிட்டிருக்கிறேன்", "சொல்லிட்டு இருக்கேன்"],
    ["இருந்துட்டிருக்கிறேன்", "இருந்துட்டு இருக்கிறேன்"],
    ["பார்த்தீங்கன்னா", "பார்த்தீர்கள் என்றால்"],
    ["பார்த்ததெல்லாம்", "பார்த்தது எல்லாம்"],
    ["கேள்விப்பட்டவுடன்", "கேள்விப்பட்ட உடன்"],
    ["சொல்லிவிட்டு", "சொல்லி விட்டு"],
    ["வரவிருந்த", "வர இருந்த"],
    ["சென்றுவந்தான்", "சென்று வந்தான்"],
    ["அக்கம்பக்கம்", "அக்கம் பக்கம்"],
    ["தொற்றுநோய்", "தொற்று நோய்"],
    ["புரிந்துகொள்ளுங்கள்", "புரிந்து கொள்ளுங்கள்"]
]

Merging Two Words -
[
    ["தலை விதி", "தலைவிதி"],
    ["குளித்து விட்டு", "குளிச்சுட்டு"],
    ["பசங்கள் எல்லாம்", "பசங்களெல்லாம்"],
    ["காசு இல்லை", "காசில்லை"],
    ["பொருள் இல்லை", "பொருளில்லை"],
    ["ஒத்து வாழ்", "ஒத்துவாழ்"],
    ["கொண்டு வந்து", "கொண்டுவந்து"],
    ["எள் அளவும்", "எள்ளளவும்"]
]

Matra and Dialectical Variations - 
[
    ["என்ன", "என்னா"],
    ["ஏதாவது", "எதாவது"],
    ["பிடிக்கும்", "புடிக்கும்"],
    ["உடனே", "ஒடனே"],
    ["கிடைக்குது", "கெடைக்குது"],
    ["மங்களம்", "மங்கலம்"],
    ["சிருஷ்டி", "ஸிருஷ்டி"]
]

Spelling Variations for loaned words - 
[
    ["ஆடர்", "ஆர்டர்", "ஆடரு", "ஆர்டரு", "ஆட்ரு"],
    ["ஃபஸ்ட்", "ஃபஸ்ட்டு", "பஸ்ட்"],
    ["பஸ்", "பஸ்ஸூ", "பஸ்சு"],
    ["கவுர்மெண்ட்", "கவர்மெண்ட்"],
    ["கிளவுஸ்", "கிளெளஸ்"],
    ["டெசிமல்", "டெஸிமல்"],
    ["சூட்டிங்", "ஸூட்டிங்"],
    ["சவுத்", "சௌத்"],
    ["மெசேஜ்", "மெஸேஜ்"],
    ["சுகர்", "ஷுகர்"],
    ["பிசினஸ்", "பிஸினஸ்"],
    ["கிரவுண்ட்", "கிரௌண்ட்"]
]

Ligature Variations -

    ["க் ஷேத்ரம்", "க்ஷேத்ரம்"],
    ["நக் ஷத்திரம்", "நக்ஷத்திரம்"],
    ["ஒர்க் ஷாப்", "ஒர்க்ஷாப்"],
    ["ஆக்சன்", "ஆக்ஷன்"],
    ["மிலக்சேக்", "மில்க்ஷேக்"],
    ["ரிக்சா", "ரிக்ஷா"],
    ["விருக்சம்", "விருக்ஷம்"]
]

Sandhi rules -
[
    ["அவன் ஒன்று", "அவனொன்று"],
    ["இங்கு ஒன்று", "இங்கொன்று"],
    ["போட்டு விட்டு", "போட்டுவிட்டு"],
    ["அவை எல்லாம்", "அவையெல்லாம்"],
    ["கை எழுத்து", "கையெழுத்து"],
    ["இங்கே இருந்து", "இங்கிருந்து"]
]


'''

GUIDELINES_PROMPT['Sanskrit']='''
Phonetic Variations
[
    ["ज्ञानम्", "ज्ञानं"],
    ["किम्", "किं"],
    ["तत्", "तद्"],
    ["अहम्", "अहं"],
    ["रेल्", "रैल्"]
]

Splitting Compound Words
[
    ["एवमेव", "एवम् एव"],
    ["किमकरोत्", "किम् अकरोत्"],
    ["अहमत्र", "अहम् अत्र"],
    ["मामेव", "माम् एव"],
    ["मामपि", "माम् अपि"]
]

Merging Two Words
[
    ["माता पिता", "मातापितरौ"],
    ["रेल्स्थानकम्", "रेल् स्थानकम्"],
    ["कार्यानम्", "कार् यानम्"],
    ["बेङ्गलूरु नगरम्", "बेङ्गलूरु नगरम्"],
    ["अमेरिकादेशः", "अमेरिकादेशः"]
]

Matra and Diacritic Variations
[
    ["तत्त्व", "तत्त्व"],
    ["मैक्सिमम", "मैग्ज़िमम"]
]

Ligature Variations
[
    ["क्‌षे", "क्षे"],
    ["ग्न्य", "ज्ञ"]
]

Sandhi Rules
[
    ["रामः अस्ति", "रामोSस्ति"],
    ["ननु अत्र", "नन्वत्र"],
    ["कः अस्ति", "कोSस्ति"],
    ["का अपि", "कापि"],
    ["तत् अपि", "तद् अपि"]
]
'''

GUIDELINES_PROMPT["Urdu"]='''
Phonetic Variations
[
    ["چاہیے", "چاہئے"],
    ["کرےگا", "کریگا"],
    ["بےحد", "بیحد"]
]

Splitting Compound Words
[
    ["کے لیے", "کیلیے"],
    ["اتر پردیش", "اترپردیش"],
    ["پھول دان", "پھولدان"],
    ["آپ کا", "آپکا"],
    ["علی گڑھ", "علیگڑھ"]
]

Merging Two Words
[
    ["بے شمار", "بےشمار"],
    ["خود کشی", "خودکشی"],
    ["گل زار", "گلزار"],
    ["کشمکش", "کش مکش"]
]

Spelling Variations for Loaned Words
[
    ["ہائیڈروجن", "ہائڈروجن"],
    ["کالیرا", "کالرا"]
]

Sandhi Rules
[
    ["گرداب", "گرد+آب"]
]
'''

GUIDELINES_PROMPT["Telugu"]='''
Phonetic Variations
[
    ["ఋతువులు", "రుతువులు"],
    ["వృషభం", "రుషభం", "రిషభం"],
    ["వ్రాయడం", "రాయడం"],
    ["చేసారు", "చేశారు"],
    ["అవుతుంది", "ఔతుంది"],
    ["ఉంటుంది", "వుంటుంది"],
    ["వెళ్ళు", "వెళ్లు"],
    ["గుఱ్ఱం", "గుర్రం"],
    ["తినటం", "తినడం"],
    ["రెండవది", "రెండోది"]
]

Splitting Compound Words
[
    ["అదేవిధంగా", "అదే విధంగా"],
    ["గుర్తులేదు", "గుర్తు లేదు"],
    ["ఆడేవారు", "అడే వారు"],
    ["తయారుచేశారు", "తయారు చేశారు"],
    ["ప్రతిరోజు", "ప్రతి రోజు"],
    ["ఆంధ్రప్రదేశ్", "ఆంధ్ర ప్రదేశ్"]
]

Merging Two Words
[
    ["జీవన శైలి", "జీవనశైలి"],
    ["అదే పనిగా", "అదేపనిగా"],
    ["రైలు బండి", "రైలుబండి"],
    ["పాడి పంటలు", "పాడిపంటలు"],
    ["దేశ ముదురు", "దేశముదురు"]
]

Matra and Diacritic Variations
[
    ["ప్రతి", "ప్రతీ"],
    ["కాని", "కానీ"],
    ["ఒకొక్క", "ఒక్కొక్క"],
    ["మనం", "మనము"]
]

Spelling Variations for Loaned Words
[
    ["బిరియానీ", "బిర్యానీ"],
    ["ట్రెయిన్", "ట్రైన్"],
    ["మ్యాడమ్", "మేడమ్", "మ్యాడం"],
    ["హైదరాబాద్", "హైదరాబాదు"],
    ["ఆపిల్", "యాపిల్"],
    ["ప్లేట్", "ప్లేటు"]
]

Sandhi Rules
[
    ["వెళ్ళొస్తాను", "వెళ్ళి వస్తాను"],
    ["పన్నెండొందలు", "పన్నెండు వందలు"],
    ["వస్తుందేమో", "వస్తుంది ఏమో"],
    ["కాదంటారు", "కాదు అంటారు"],
    ["తప్పని", "తప్పు అని"],
    ["ఎన్నేళ్ళు", "ఎన్ని ఏళ్ళు"]
]
'''

GUIDELINES_PROMPT['Punjabi']='''
Phonetic Variations
[
    ["ਬਦਲਾਵ", "ਬਦਲਾਅ"],
    ["ਜ਼ਿੰਮੇਦਾਰੀਆਂ", "ਜ਼ਿੰਮੇਵਾਰੀਆਂ"],
    ["ਮੁਫ਼ਤ", "ਮੁਫਤ"],
    ["ਬਾਰੂਦ", "ਬਰੂਦ"],
    ["ਸੁਆਗਤ", "ਸਵਾਗਤ"],
    ["ਗਰੰਥ", "ਗ੍ਰੰਥ"],
    ["ਗੁਆਂਢੀ", "ਗਵਾਂਢੀ"]
]

Splitting Compound Words
[
    ["ਗੋਲਾ ਬਾਰੂਦ", "ਗੋਲਾ-ਬਾਰੂਦ"],
    ["ਨੇੜੇ-ਤੇੜੇ", "ਨੇੜੇ ਤੇੜੇ"],
    ["ਇਸਦਾ", "ਇਸ ਦਾ"],
    ["ਵਰਣਮਾਲਾ", "ਵਰਣ-ਮਾਲਾ"]
]

Merging Two Words
[
    ["ਰੇਲ ਗੱਡੀ", "ਰੇਲਗੱਡੀ"],
    ["ਤਾਲ ਮੇਲ", "ਤਾਲਮੇਲ"],
    ["ਜਗ ਮਗ", "ਜਗਮਗ"],
    ["ਸਾਂਭ-ਸੰਭਾਲ", "ਸਾਂਭਸੰਭਾਲ"],
    ["ਧਰਮ ਪੂਜਾ", "ਧਰਮਪੂਜਾ"],
    ["ਗ੍ਰਾਮ ਪੰਚਾਇਤ", "ਗ੍ਰਾਮਪੰਚਾਇਤ"]
]

Matra and Diacritic Variations
[
    ["ਜਿਆਦਾ", "ਜ਼ਿਆਦਾ"],
    ["ਸਲਾਈ", "ਸਿਲਾਈ"],
    ["ਅਲੱਗ", "ਅਲਗ"],
    ["ਉਪਲੱਬਧ", "ਉਪਲਬਧ"],
    ["ਪ੍ਰਾਕ੍ਰਿਤਕ", "ਪ੍ਰਕ੍ਰਿਤਕ"],
    ["ਵਾਪਿਸ", "ਵਾਪਸ"]
]

Spelling Variations for Loaned Words
[
    ["ਕਲੀਨਿਕ", "ਕਲਿਨਿਕ"],
    ["ਫ੍ਰੀ", "ਫਰੀ"],
    ["ਓਕਸੀਜਨ", "ਆਕਸੀਜਨ"],
    ["ਆਨਲਾਈਨ", "ਔਨਲਾਈਨ"],
    ["ਕੰਪਨੀ", "ਕੌਪਣੀ"],
    ["ਟਾਇਮ", "ਟਾਈਮ"]
]

Ligature Variations
[
    ["ਸਵੱਚ", "ਸਵੱਛ"],
    ["ਟ੍ਰੇਨ", "ਟਰੇਨ"],
    ["ਕ੍ਰਿਸ਼ਚਨ", "ਕਰਿਸ਼ਚਨ"],
    ["ਪ੍ਰੰਪਰਾ", "ਪਰੰਪਰਾ"]
]

Sandhi Rules
[
    ["ਗੋਲਾ ਬਾਰੂਦ", "ਗੋਲਾਬਾਰੂਦ"],
    ["ਨੇੜੇ ਤੇੜੇ", "ਨੇੜੇ-ਤੇੜੇ"]
]
'''