import datetime

now = datetime.datetime.now()
current_date = now.strftime("%d/%m/%Y")

def generate_prompt_rule1_hdlc(lc_data, contract_data):
    contract_number_lc = lc_data.get("lc_contract_no", {}).get('value', "")
    contract_number_contract = contract_data.get(
        "contract_no", {}).get('value', "")

    system_prompt = """
You are an international trade document analyst with extensive experience in foreign trade contracts and Letter of Credit. Your task is to check if the CONTRACT NUMBER information on the Letter of Credit match the bank information of the original Contract.

Input: Extracted information from a foreign trade contract and Letter of Credit is as follows:
- CONTRACT NUMBER in Letter of Credit
- CONTRACT NUMBER in Contract

Overall rule: The CONTRACT NUMBER must match exactly (do not accept differences even by while space) between Letter of Credit and Contract. Response in json format, without markdown formating: {"explanation": ..., "case": "...", "is_compliance": true/false}

Detail condition:
- If the CONTRACT NUMBER absolutely match CONTRACT NUMBER in LC, return {"case": "1", "is_compliance": true}
- If the CONTRACT NUMBER different from CONTRACT NUMBER in LC or CONTRACT NUMBER is null, return {"case": "2", "is_compliance": false}

Return result in JSON format only: 
{"explanation": ..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- LC Contract Number: {contract_number_lc}
- Contract Document Number: {contract_number_contract}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule2_hdlc(lc_data, contract_data):
    lc_contract_date = lc_data.get('lc_contract_date', {}).get('value', '')
    contract_contract_date = contract_data.get('contract_date', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with extensive experience in foreign trade contracts and Letter of Credit. Your task is to check if the CONTRACT DATE information on the Letter of Credit match the bank information of the original Contract.

Input: Extracted information from a foreign trade contract and Letter of Credit is as follows:
- CONTRACT DATE (from contract) 
- LC CONTRACT DATE (from LC)

Overall rule: The CONTRACT DATE must match the LC CONTRACT DATE. Response in json format, without markdown formating: {"explanation": ..., "case": "...", "is_compliance": true/false}

Detail conditions:
- If the CONTRACT DATE is the same as LC CONTRACT DATE (even if the format differs but the meaning is the same), return {"case": "1", "is_compliance": true}
- If the CONTRACT DATE is different from LC CONTRACT DATE, return {"case": "2", "is_compliance": false}

Response in json format, without markdown formating: {"explanation": ..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT DATE: {contract_contract_date}
- LC CONTRACT DATE: {lc_contract_date}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule3_hdlc(lc_data, contract_data):
    lc_1st_swift_code = lc_data.get('advise_bank_swiftcode', {}).get('value', '')
    lc_1st_bank_name = lc_data.get('advise_bank', {}).get('value', '')
    lc_2nd_swift_code = lc_data.get('f57D_advise_through_bank', {}).get('value', '')
    lc_2nd_bank_name = lc_data.get('f57A_advise_through_bank', {}).get('value', '')

    contract_1st_swift_code = contract_data.get('advise_bank_swiftcode', {}).get('value', '')
    contract_1st_bank_name = contract_data.get('advise_bank', {}).get('value', '')
    contract_2nd_swift_code = contract_data.get('f57D_advise_through_bank', {}).get('value', '')
    contract_2nd_bank_name = contract_data.get('f57A_advise_through_bank', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with extensive experience in foreign trade contracts and Letter of Credit. Your task is to check if the bank information on the Letter of Credit (LC) match the bank information of the Contract.

Input: Bank information on the Letter of Credit and Contract
- LC 1ST ADVISING BANK
- LC 1ST ADVISING BANK SWIFT CODE
- LC 2ND ADVISING BANK
- LC 2ND ADVISING BANK SWIFT CODE

- CONTRACT 1ST ADVISING BANK
- CONTRACT 1ST ADVISING BANK SWIFT CODE
- CONTRACT 2ND ADVISING BANK
- CONTRACT 2ND ADVISING BANK SWIFT CODE

Overall rule: Check if the bank information on the Letter of Credit matches the bank information on the Contract. Response in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
Case 1: Only 1st advising bank information (SWIFT CODE + BANK NAME) on LC. Inturn compare SWIFT CODE and BANK NAME in Contract with LC. Overall: Accept the case where there is information on the LC but not on the contract, but vice versa, if both have it, it must match.
    + For SWIFT CODE and BANK NAME:
        * If both have same value: {"case": "1.1", "is_compliance": true}
        * If both have different values: {"case": "1.2", "is_compliance": false}
        * If Contract has but LC doesn't: {"case": "1.3", "is_compliance": false}
        * If LC has but Contract doesn't: {"case": "1.4", "is_compliance": true}
- If any step returns false, final result is warning: {"case": "1.5", "is_compliance": false}

Case 2: Has 1st (SWIFT CODE + BANK NAME) and 2nd (2ND SWIFT CODE +  2ND BANK NAME) advising bank information on LC. Overall: inturn compare 1st and 2nd bank information like Case 1
- Check 1st advising bank: Same rules as case 1
- Check 2nd advising bank: Same rules as case 1
- If all 1st advising bank and 2nd advising bank is satisfied, return {"case": "2.1", "is_compliance": true}.
- If any check returns false: {"case": "2.2", "is_compliance": false}

Case 3: Has 1st (SWIFT CODE + BANK NAME) advising bank + 2nd advising bank name only (2ND BANK NAME only). Overall: Compare 1st bank information like Case 1. With 2ND BANK NAME, the information of LC 2ND BANK NAME must be in set {1ST BANK NAME, 2ND BANK NAME}
- Check 1st advising bank: Same rules as case 1
- Check 2nd advising bank branch:
    + If set {Contract's 1st advising bank name and Contract's 2nd advising bank name} contains LC's 2nd advising bank name: {"case": "3.1", "is_compliance": true}
    + If both {Contract's 1st advising bank name and Contract's 2nd advising bank name} not contain LC's 2nd advising bank name: {"case": "3.2", "is_compliance": false}
- If any check returns false: {"case": "3.3", "is_compliance": false}

TH4: Has 1st (SWIFT CODE + BANK NAME) advising bank + 2nd advising bank swift code only (2ND ADVISING BANK SWIFT CODE). Overall: Accept the case where there is information on the LC but not on the contract, but vice versa, if both have it, it must match.
- Check 1st advising bank: Same rules as Case 1
- Check 2nd advising bank swift code:
    + If both have same value: {"case": "4.1", "is_compliance": true}
    + If both have different values: {"case": "4.2", "is_compliance": false}
    + If Contract has but LC doesn't: {"case": "4.3", "is_compliance": false}
    + If LC has but Contract doesn't: {"case": "4.4", "is_compliance": true}
- If any check returns false: {"case": "4.5", "is_compliance": false}

Note:
- Return the first case that matches the conditions.
- When compare bank name: Just match the bank name, no need to match the branch name. Example: DEUTSCHE BANK AG, HONG KONG BRANCH = DEUTSCHE BANK AG
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- LC 1ST ADVISING BANK: {lc_1st_bank_name}
- LC 1ST ADVISING BANK SWIFT CODE: {lc_1st_swift_code}
- LC 2ND ADVISING BANK: {lc_2nd_bank_name}
- LC 2ND ADVISING BANK SWIFT CODE: {lc_2nd_swift_code}

- CONTRACT 1ST ADVISING BANK: {contract_1st_bank_name}
- CONTRACT 1ST ADVISING BANK SWIFT CODE: {contract_1st_swift_code}
- CONTRACT 2ND ADVISING BANK: {contract_2nd_bank_name}
- CONTRACT 2ND ADVISING BANK SWIFT CODE: {contract_2nd_swift_code}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule4_hdlc(lc_data, contract_data):
    lc_expiry_date = lc_data.get('f31D_lc_expirydate', {}).get('value', '')
    contract_expiry_date = contract_data.get('f31D_lc_expirydate', {}).get('value', '')
    latest_shipment_date = contract_data.get('f44C_latest_date_of_ship', {}).get('value', '') or lc_data.get('f44C_latest_date_of_ship', {}).get('value', '')
    period_of_presentation = contract_data.get('f48_period_of_present', {}).get('value', '') or lc_data.get('f48_period_of_present', {}).get('value', '')
    lc_issuance_date = current_date

    system_prompt = """
You are an international trade document analyst with expertise in analyzing Letters of Credit and trade contracts. Your task is to evaluate the compliance of the DATE OF EXPIRY field in the Letter of Credit based on the contract.

Your input includes:
- DATE OF EXPIRY in LC
- DATE OF EXPIRY term in Contract  
- LATEST DATE OF SHIPMENT
- LC ISSUANCE DATE
- PERIOD OF PRESENTATION

Overall rule: DATE OF EXPIRY in LC must match the CALCULATED DATE OF EXPIRY based on Contract terms.

**Date Processing Rules:**
1. If LATEST DATE OF SHIPMENT contains only month/year (e.g., "May 2025", "2025.05"), interpret as the LAST DAY of that month (e.g., "31/05/2025")
2. Accept various date formats: DD/MM/YYYY, MM/DD/YYYY, YYYY.MM.DD, etc.
3. If PERIOD OF PRESENTATION contains text like "WITHIN X DAYS" or "X DAYS AFTER SHIPMENT", extract the number X

**Evaluation Cases:**

**Case 1 - Fixed Expiry Date in Contract:**
- If Contract DATE OF EXPIRY specifies a fixed date (e.g., "15/07/2025")
- CALCULATED DATE OF EXPIRY = Contract DATE OF EXPIRY
- Compare with LC expiry date
- Return: {"case": "1", "is_compliance": true/false}

**Case 2 - Relative Expiry Term in Contract:**
- If Contract specifies relative terms (e.g., "30 days after shipment", "xxx days after B/L date")
- If LATEST DATE OF SHIPMENT available: CALCULATED DATE OF EXPIRY = LATEST DATE OF SHIPMENT + relative days
- If LATEST DATE OF SHIPMENT not available: CALCULATED DATE OF EXPIRY = LC ISSUANCE DATE + relative days
- Return: {"case": "2", "is_compliance": true/false}

**Case 3 - No Expiry Term in Contract:**
- **Case 3.1.1**: Contract has no expiry term, LATEST SHIPMENT available, PERIOD OF PRESENTATION available
  - CALCULATED DATE OF EXPIRY = LATEST DATE OF SHIPMENT + PERIOD OF PRESENTATION days
  - Return: {"case": "3.1.1", "is_compliance": true/false}
  
- **Case 3.1.2**: Contract has no expiry term, LATEST SHIPMENT available, PERIOD OF PRESENTATION not available  
  - CALCULATED DATE OF EXPIRY = LATEST DATE OF SHIPMENT + 21 days
  - Return: {"case": "3.1.2", "is_compliance": true/false}
  
- **Case 3.2**: Contract has no expiry term, LATEST SHIPMENT not available
  - Cannot calculate expiry date
  - Return: {"case": "3.2", "is_compliance": false}

**Compliance Rules:**
- Dates match if they represent the same calendar date, regardless of format
- Use best effort to parse and interpret date formats
- If any calculation results in a date that matches LC expiry date, mark as compliant

Response format (JSON only, no markdown):
{"explanation": "detailed explanation of calculation and comparison", "case": "case_number", "is_compliance": true/false}
    """

    user_prompt = f"""
LC Expiry Date: {lc_expiry_date}
Contract Expiry Term: {contract_expiry_date}
Latest Shipment Date: {latest_shipment_date}
Period of Presentation: {period_of_presentation}
LC Issuance Date: {lc_issuance_date}

Please analyze the compliance according to the evaluation rules and return the result in JSON format.
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule5_hdlc(lc_data, contract_data):
    lc_place_of_expiry = lc_data.get('f31D_place_of_expiry', {}).get('value', '')
    contract_place_of_expiry = contract_data.get('f31D_place_of_expiry', {}).get('value', '')
    contract_bank = contract_data.get('advise_bank', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the PLACE OF EXPIRY field between the contract and the LC.

Inputs:
- LC PLACE OF EXPIRY
- CONRACT PLACE OF EXPIRY
- CONTRACT BANK

Overall rule: PLACE OF EXPIRY in LC must match the PLACE OF EXPIRY in Contract. If not, use the COUNTRY of the advising bank in the Contract to compare with PLACE OF EXPIRY in the LC. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If PLACE OF EXPIRY is specified in both Contract and LC:
    - If the values match. Return {"case": "1.1", "is_compliance": true}
    - If they do not match. Return {"case": "1.2", "is_compliance": false}

- Case "2": If PLACE OF EXPIRY is not specified in the Contract, use the COUNTRY of the advising bank in the Contract to compare with PLACE OF EXPIRY in the LC:
    - If they match. Return {"case": "2.1", "is_compliance": true}
    - If they do not match. Return {"case": "2.2", "is_compliance": false}

Note:
- Infer country of bank if country information is not available in the contract.
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- LC PLACE OF EXPIRY: {lc_place_of_expiry}
- CONTRACT PLACE OF EXPIRY: {contract_place_of_expiry}
- CONTRACT BANK: {contract_bank}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule6_hdlc(lc_data, contract_data):
    lc_applicant = lc_data.get('f50_applicant_name_address', {}).get('value', '')
    lc_applicant_addr_2 = lc_data.get('f47A_additional_condition', {}).get('metadata', {}).get('bct_47a_applicant_addr') or lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_buyer = contract_data.get('f50_applicant_name_address', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the APPLICANT'S NAME AND ADDRESS in the Letter of Credit (LC) matches the BUYER information in the contract.

Inputs:
- CONTRACT BUYER NAME AND ADDRESS 
- LC APPLICANT'S NAME AND ADDRESS 
- LC ADDITIONAL APPLICANT ADDRESSS 


Overall rule: APPLICANT'S NAME AND ADDRESS in LC must match the BUYER information in the contract. The APPLICANT ADDRESS in LC can appear in ADDITIONAL CONDITIONS. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If both LC and contract have the information and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have the information and they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has information but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has information but contract does not. Return {"case": "4", "is_compliance": true}


Note:
- APPLICANT'S address in LC can appear in ADDITIONAL CONDITIONS
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT BUYER NAME AND ADDRESS: {contract_buyer}
- LC APPLICANT'S NAME AND ADDRESS: {lc_applicant}
- LC ADDITIONAL APPLICANT ADDRESSS: {lc_applicant_addr_2}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule7_hdlc(lc_data, contract_data):
    lc_beneficiary = lc_data.get('f59_benefic_name_address', {}).get('value', '')
    lc_beneficiary_addr_2 = lc_data.get('f47A_additional_condition', {}).get('metadata', {}).get('bct_47a_ben_addr') or lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_seller = contract_data.get('f59_benefic_name_address', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the BENEFICIARY'S NAME AND ADDRESS in the Letter of Credit (LC) matches the SELLER information in the contract.

Inputs:
- CONTRACT SELLER NAME AND ADDRESS
- LC BENEFICIARY'S NAME AND ADDRESS
- LC ADDITIONAL BENEFICIARY'S ADDRESS

Overall rule: BENEFICIARY'S NAME AND ADDRESS in LC must match the SELLER information in the contract. The BENEFICIARY ADDRESS in LC can appear in ADDITIONAL CONDITIONS.
Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Rules:
- Case "1": If both LC and contract have the information and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have the information and they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has information but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has information but contract does not. Return {"case": "4", "is_compliance": true}

Note:
- BENEFICIARY address in LC can appear in ADDITIONAL CONDITIONS
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT SELLER NAME AND ADDRESS: {contract_seller}
- LC BENEFICIARY'S NAME AND ADDRESS: {lc_beneficiary}
- LC ADDITIONAL BENEFICIARY'S ADDRESS: {lc_beneficiary_addr_2}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule8_hdlc(lc_data, contract_data):
    lc_amount = lc_data.get('f32B_amount', {}).get('value', '') + ' ' + lc_data.get('f32B_currency_code', {}).get('value', '')
    contract_amount = contract_data.get('contract_amount', {}).get('value', '') + ' ' + contract_data.get('f32B_currency_code', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the AMOUNT in the Letter of Credit (LC) matches the AMOUNT in the contract.

Inputs:
- LC AMOUNT
- Contract AMOUNT

Overall rule: AMOUNT in LC must match the AMOUNT in the contract. Respond in JSON format, no markdown: {"case": "...", "is_compliance": true/false}

Detail conditions:
- Case 1: If LC AMOUNT and Contract Amount is equal, return {"case": "1", "is_compliance": true}
- Case 2: If LC AMOUNT and Contract Amount is not, return {"case": "2", "is_compliance": false}

Note:
- Currency of amount must match in all comparisons.
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- LC AMOUNT: {lc_amount}
- CONTRACT AMOUNT: {contract_amount}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule9_hdlc(lc_data, contract_data):
    lc_credit_tolerance = lc_data.get('f39A_credit_tolerance', {}).get('value', '')
    lc_debit_tolerance = lc_data.get('f39A_debit_tolerance', {}).get('value', '')
    contract_credit_tolerance = contract_data.get('f39A_credit_tolerance', {}).get('value', '')
    contract_debit_tolerance = contract_data.get('f39A_debit_tolerance', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the AMOUNT TOLERANCE in the Letter of Credit (LC) matches the tolerance specified in the contract.

Inputs:
- LC CREDIT AMOUNT TOLERANCE: Credit Tolerance (% over)
- LC DEBIT AMOUNT TOLERANCE: Debit Tolerance (% under)
- CONTRACT CREDIT AMOUNT TOLERANCE: Credit Tolerance (% over)
- CONTRACT DEBIT AMOUNT TOLERANCE: Debit Tolerance (% under)

Overall rule: AMOUNT TOLERANCE in LC must match the AMOUNT TOLERANCE in the contract. If not, check if the AMOUNT TOLERANCE in LC is within 10% of the AMOUNT TOLERANCE in the contract.
Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If both LC and contract specify tolerances. Check both CREDIT and DEBIT tolerances.
    - If LC = Contract. Return {"case": "1.1", "is_compliance": true}
    - If LC > Contract. Return {"case": "1.2", "is_compliance": false}
    - If LC < Contract. Return {"case": "1.3", "is_compliance": true}

- Case "2": If contract has values, LC has none or zero. Return {"case": "2", "is_compliance": true}

- Case "3": If contract has no value or zero, but LC has value. Check both CREDIT and DEBIT tolerances.
    - If LC tolerance (credit and debit) <= 10%. Return {"case": "3.1", "is_compliance": true}
    - Else. Return {"case": "3.2", "is_compliance": false}

- Case "4": If both contract and LC tolerances are empty or zero. Return {"case": "4", "is_compliance": true}

Note:
- By default, the unit of tolerance is percentage (%).
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- LC CREDIT AMOUNT TOLERANCE: {lc_credit_tolerance}
- LC DEBIT AMOUNT TOLERANCE: {lc_debit_tolerance}
- CONTRACT CREDIT AMOUNT TOLERANCE: {contract_credit_tolerance}
- CONTRACT DEBIT AMOUNT TOLERANCE: {contract_debit_tolerance}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule10_hdlc(lc_data, contract_data):
    lc_tenor = lc_data.get('tenor', {}).get('value', '')
    lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
    lc_documents_required = lc_data.get('f46A_documents_requires', {}).get('value', '')
    lc_reimbursing_bank = lc_data.get('reimbursing_bank', {}).get('value', '')
    contract_tenor = contract_data.get('tenor', {}).get('value', '')
    
    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit (LC) and trade contracts. Your task is to evaluate the compliance of the TENOR field between the contract and the LC according to updated rules.

**PRIORITY WARNING**: An LC is ONLY UPAS if REIMBURSING BANK field contains actual bank information. Empty REIMBURSING BANK = NOT UPAS, regardless of any UPAS language elsewhere.

Inputs:
- LC TENOR
- LC ADDITIONAL CONDITIONS  
- LC DOCUMENTS REQUIRED
- LC REIMBURSING BANK
- CONTRACT TENOR

**TENOR Compliance Rules:**

**TH1: TENOR between Contract and LC matches exactly** → Return {"case": "TH1", "is_compliance": true}
- This applies when both LC and Contract have TENOR values and they are semantically identical
- **Flexible Matching Rules:**
  - Ignore case differences (uppercase/lowercase)
  - Ignore leading "AT" if present in one but not the other
  - Normalize whitespace and punctuation
  - Handle common synonyms: "B/L" = "BL" = "BILL OF LADING"
  - Handle date variations: "ON BOARD DATE" = "ONBOARD DATE" = "DATE"
  - Examples of matches:
    * "AT 90 DAYS AFTER B/L ON BOARD DATE" ≈ "90 days after B/L on board date"
    * "60 DAYS AFTER SIGHT" ≈ "AT 60 DAYS AFTER SIGHT"
    * "AT SIGHT" ≈ "SIGHT"

**TH2: TENOR between Contract and LC does not match** → Check additional analysis:

**TH2.1: If LC is not UPAS** (LC tenor is "at sight/sight" OR **REIMBURSING BANK is empty/blank/null**):
- **IMPORTANT**: Even if ADDITIONAL CONDITIONS contains UPAS clauses, if REIMBURSING BANK is empty, the LC is NOT UPAS

**Non-UPAS Logic Sub-cases:**
- **TH2.1.1**: TENOR in both LC and Contract exist and match → {"case": "TH2.1.1", "is_compliance": true}
- **TH2.1.2**: TENOR in both LC and Contract exist but do not match → {"case": "TH2.1.2", "is_compliance": false}
- **TH2.1.3**: TENOR not in LC but exists in Contract → {"case": "TH2.1.3", "is_compliance": false}
- **TH2.1.4**: TENOR exists in LC but not in Contract:
  - **TH2.1.4.1**: If LC TENOR = "AT SIGHT" → {"case": "TH2.1.4.1", "is_compliance": true}
  - **TH2.1.4.2**: If LC TENOR ≠ "AT SIGHT" → {"case": "TH2.1.4.2", "is_compliance": false}

**TH2.2: If LC is UPAS** (LC tenor is usance AND **REIMBURSING BANK has actual bank details**):
**NOTE**: This section should NEVER be reached if REIMBURSING BANK is empty
Check ADDITIONAL CONDITIONS for UPAS clauses. Look for content containing:
- "IRRESPECTIVE OF THE TENOR OF THE L/C, PAYMENT IS AVAILABLE AT" 
- "NOTWITHSTANDING THE TENOR OF THE L/C"
- "Despite the tenor of LC being XXXXX"
- Payment timing instructions
- Interest cost allocation
- Reimbursement bank instructions

**Sub-cases for TH2.2:**
- **TH2.2.1**: ADDITIONAL CONDITIONS contains UPAS clause with payment timing matching CONTRACT TENOR → {"case": "TH2.2.1", "is_compliance": true}
- **TH2.2.2**: ADDITIONAL CONDITIONS contains UPAS clause but payment timing does NOT match CONTRACT TENOR → {"case": "TH2.2.2", "is_compliance": false}  
- **TH2.2.3**: ADDITIONAL CONDITIONS contains UPAS clause but no clear payment timing found → {"case": "TH2.2.3", "is_compliance": false}
- **TH2.2.4**: No UPAS clause found in ADDITIONAL CONDITIONS → {"case": "TH2.2.4", "is_compliance": false}

**Analysis Instructions:**
1. **First, normalize and compare TENOR values using flexible matching:**
   - Convert both to uppercase for comparison
   - Remove leading "AT" if present
   - Normalize spaces and punctuation
   - Apply synonym matching (B/L = BL = BILL OF LADING)
   - If semantically equivalent → return TH1
   
2. **If not matching after normalization, MANDATORY STEP - Check REIMBURSING BANK field FIRST:**
   
   **STEP 2A: REIMBURSING BANK Check (MUST BE DONE BEFORE ANY UPAS ANALYSIS)**
   - Examine LC REIMBURSING BANK field value
   - If REIMBURSING BANK is empty/blank/null/contains only labels → **STOP HERE** → LC is NOT UPAS
   - Apply TH2.1 sub-logic immediately, DO NOT proceed to UPAS analysis
   
   **STEP 2B: Only if REIMBURSING BANK has actual bank details**
   - AND LC tenor is usance → LC is UPAS → Continue to TH2.2
   - If LC tenor is "AT SIGHT" → LC is NOT UPAS → Apply TH2.1 sub-logic
   
3. **WARNING**: Do NOT classify as UPAS based on ADDITIONAL CONDITIONS content alone
4. **WARNING**: UPAS clauses in ADDITIONAL CONDITIONS are irrelevant if REIMBURSING BANK is empty
5. If confirmed UPAS, then analyze ADDITIONAL CONDITIONS for relevant clauses

**CRITICAL: UPAS Detection Criteria (BOTH conditions must be met):**
- LC TENOR contains usance terms (not "sight" or "at sight")  
- **AND REIMBURSING BANK field has actual bank name/details (NOT empty/blank/null)**

**ABSOLUTE RULE**: If REIMBURSING BANK is empty, blank, or null, the LC is **NEVER UPAS** regardless of:
- Any UPAS clauses in ADDITIONAL CONDITIONS
- Any "Despite the tenor" language
- Any payment instructions mentioning UPAS
- Any interest cost allocations

**DO NOT BE MISLED**: UPAS descriptions in text do not make an LC UPAS if REIMBURSING BANK is empty.

**Payment Timing Extraction:**
- Look for patterns like "AT SIGHT", "XXX DAYS FROM", "XXX DAYS AFTER"
- Common formats: "90 DAYS", "60 DAYS AFTER B/L DATE", "AT SIGHT"

**REIMBURSING BANK Field Check:**
- Empty values include: "", "CONTRACT TENOR:", blank lines, null
- Must contain actual bank name/details to be considered "has value"
- If field shows only labels without content, treat as empty

**TENOR Field Check:**
- Empty/null TENOR values include: "", null, blank lines, undefined
- "AT SIGHT" variations: "AT SIGHT", "SIGHT", "at sight", "sight"
- Must have actual tenor terms to be considered "exists"

**TENOR Normalization for Matching:**
- Remove case sensitivity: "AT 90 DAYS" = "at 90 days"
- Remove optional "AT" prefix: "AT 90 DAYS AFTER SIGHT" = "90 DAYS AFTER SIGHT"  
- Handle B/L variations: "B/L" = "BL" = "BILL OF LADING"
- Handle date variations: "ON BOARD DATE" = "ONBOARD DATE" = "DATE"
- Normalize spaces: "90  DAYS" = "90 DAYS"
- Focus on semantic meaning, not exact text match

Response in JSON format, without markdown formatting:
{"explanation": "Brief explanation MUST include: 1) REIMBURSING BANK status (empty/has value), 2) Whether LC is UPAS or not, 3) TENOR comparison after normalization, 4) Compliance analysis", "case": "case_code", "is_compliance": true/false}
    """

    user_prompt = f"""
LC TENOR: {lc_tenor}
**LC REIMBURSING BANK: {lc_reimbursing_bank}
LC ADDITIONAL CONDITIONS: {lc_additional_conditions}
LC DOCUMENTS REQUIRED: {lc_documents_required}
CONTRACT TENOR: {contract_tenor}

**REMINDER**: 
1. Apply flexible TENOR matching first (normalize case, remove optional "AT", handle synonyms)
2. Only if TENOR don't match semantically, then check REIMBURSING BANK for UPAS analysis

Please analyze the TENOR compliance according to the evaluation rules and return the result in JSON format.
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule11_hdlc(lc_data, contract_data):
    lc_partial_shipment = lc_data.get('partial_shipment', {}).get('value', '')
    lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_partial_shipment = contract_data.get('partial_shipment', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the PARTIAL SHIPMENT condition in the Letter of Credit (LC) matches the one in the contract.

Inputs:
- CONTRACT PARTIAL SHIPMENT
- LC PARTIAL SHIPMENT
- LC ADDITIONAL CONDITIONS (F47A)

Overall rule: PARTIAL SHIPMENT in LC must match the PARTIAL SHIPMENT in the contract. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If both LC and contract have values and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have values but they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": true}
- Case "5": If both LC and contract do not have values. Return {"case": "5", "is_compliance": false}

Note:
- The PARTIAL SHIPMENT in LC can appear in ADDITIONAL CONDITIONS (F47A).
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT PARTIAL SHIPMENT: {contract_partial_shipment}
- LC PARTIAL SHIPMENT: {lc_partial_shipment}
- LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule12_hdlc(lc_data, contract_data):
    lc_transhipment = lc_data.get('transhipment', {}).get('value', '')
    lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_transhipment = contract_data.get('transhipment', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the TRANSHIPMENT condition in the Letter of Credit (LC) matches the one in the contract.

Inputs:
- CONTRACT TRANSHIPMENT 
- LC TRANSHIPMENT
- LC ADDITIONAL CONDITIONS (F47A)

Overall rule: TRANSHIPMENT in LC must match the TRANSHIPMENT in the contract. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}


Detail conditions:
- Case "1": If both LC and contract have values and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have values but they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": true}
- Case "5": If both LC and contract do not have values. Return {"case": "5", "is_compliance": false}

Note:
- The TRANSHIPMENT in LC can appear in ADDITIONAL CONDITIONS (F47A).
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT TRANSHIPMENT: {contract_transhipment}
- LC TRANSHIPMENT: {lc_transhipment}
- LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule13_hdlc(lc_data, contract_data):
    lc_place_of_receipt = lc_data.get(
        'f44A_place_of_receipt', {}).get('value', '')
    lc_additional_conditions = lc_data.get(
        'f47A_additional_condition', {}).get('value', '')
    contract_place_of_receipt = contract_data.get(
        'f44A_place_of_receipt', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the PLACE OF RECEIPT/TAKING IN CHARGE condition in the Letter of Credit (LC) matches the one in the contract.

Inputs:
- CONTRACT PLACE OF RECEIPT/TAKING IN CHARGE
- LC PLACE OF RECEIPT/TAKING IN CHARGE
- LC ADDITIONAL CONDITIONS (F47A)

Overall rule: PLACE OF RECEIPT/TAKING IN CHARGE in LC must match the PLACE OF RECEIPT/TAKING IN CHARGE in the contract. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If both LC and contract have values and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have values but they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": true}
- Case "5": If both LC and contract do not have values. Return {"case": "5", "is_compliance": false}

Note:
- The PLACE OF RECEIPT/TAKING IN CHARGE in LC can appear in ADDITIONAL CONDITIONS (F47A).
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT PLACE OF RECEIPT/TAKING IN CHARGE: {contract_place_of_receipt}
- LC PLACE OF RECEIPT/TAKING IN CHARGE: {lc_place_of_receipt}
- LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule14_hdlc(lc_data, contract_data):
    lc_port_of_loading = lc_data.get('f44E_port_of_loading', {}).get('value', '') or lc_data.get('airport_of_departure', {}).get('value', '')
    lc_place_of_receipt = lc_data.get('f44A_place_of_receipt', {}).get('value', '')
    lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_port_of_loading = contract_data.get('port_of_loading', {}).get('value', '') or contract_data.get('airport_of_departure', {}).get('value', '')
    
    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the PORT OF LOADING / AIRPORT OF DEPARTURE condition in the Letter of Credit (LC) matches the one in the contract.

Inputs:
- CONTRACT PORT OF LOADING / AIRPORT OF DEPARTURE
- LC PORT OF LOADING / AIRPORT OF DEPARTURE
- LC PLACE OF RECEIPT/TAKING IN CHARGE
- LC ADDITIONAL CONDITIONS (F47A)

Overall rule: PORT OF LOADING / AIRPORT OF DEPARTURE in LC must match the PORT OF LOADING / AIRPORT OF DEPARTURE in the contract. If both LC and Contract have no value, only need to check the existance of LC PLACE OF RECEIPT/TAKING IN CHARGE
Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If both LC and contract have values and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have values but they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": true}
- Case "5": If both LC and contract do not have values, check existence of LC PLACE OF RECEIPT/TAKING IN CHARGE. (Only need to check the existance of LC PLACE OF RECEIPT/TAKING IN CHARGE)
    - If LC PLACE OF RECEIPT/TAKING IN CHARGE has value. Return {"case": "5", "is_compliance": true}
    - If LC PLACE OF RECEIPT/TAKING IN CHARGE does not have value. Return {"case": "6", "is_compliance": false}

Note:
- The PORT OF LOADING / AIRPORT OF DEPARTURE in LC can appear in ADDITIONAL CONDITIONS (F47A).
- When compare port: Any port is different from specific named port. Example: "Cai Lai Port" is diffrent from "Any port in Hochiminh City"
- Explain briefly. No need to point out the specific case, just explain why it true/false.
    
Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT PORT OF LOADING / AIRPORT OF DEPARTURE: {contract_port_of_loading}
- LC PORT OF LOADING / AIRPORT OF DEPARTURE: {lc_port_of_loading}
- LC PLACE OF RECEIPT/TAKING IN CHARGE: {lc_place_of_receipt}
- LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule15_hdlc(lc_data, contract_data):
    lc_port_of_discharge = lc_data.get('f44F_port_of_discharge', {}).get('value', '') or lc_data.get('airport_of_destination', {}).get('value', '')
    lc_final_destination = lc_data.get('final_destination', {}).get('value', '')
    lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_port_of_discharge = contract_data.get('port_of_discharge', {}).get('value', '') or contract_data.get('airport_of_destination', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the PORT OF DISCHARGE / AIRPORT OF DESTINATION condition in the Letter of Credit (LC) matches the one in the contract.

Inputs:
- CONTRACT PORT OF DISCHARGE / AIRPORT OF DESTINATION
- LC PORT OF DISCHARGE / AIRPORT OF DESTINATION
- LC FINAL DESTINATION
- LC ADDITIONAL CONDITIONS (F47A)

Overall rule: PORT OF DISCHARGE / AIRPORT OF DESTINATION in LC must match the PORT OF DISCHARGE / AIRPORT OF DESTINATION in the contract. If both LC and Contract have no value, only need to check the existance of LC FINAL DESTINATION.

Special case:
- If contract has information but LC does not. Check if the contract's buyer name and address is in the ADDITIONAL CONDITIONS of the LC. If so, return {"case": "3", "is_compliance": true}
- If LC has information but contract does not. Check if the LC's applicant name and address is in the ADDITIONAL CONDITIONS of the contract. If so, return {"case": "4", "is_compliance": true}

Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If both LC and contract have values and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have values but they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": true}
- Case "5": If both LC and contract do not have values, check existence of LC FINAL DESTINATION. (Only need to check the existance of LC FINAL DESTINATION)
    - If LC FINAL DESTINATION has value. Return {"case": "5", "is_compliance": true}
    - If LC FINAL DESTINATION does not have value. Return {"case": "6", "is_compliance": false}

Note:
- The PORT OF DISCHARGE / AIRPORT OF DESTINATION in LC can appear in ADDITIONAL CONDITIONS (F47A).
- When compare port: Any port is different from specific named port. Example: "Cai Lai Port" is diffrent from "Any port in Hochiminh City"
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT PORT OF DISCHARGE / AIRPORT OF DESTINATION: {contract_port_of_discharge}
- LC PORT OF DISCHARGE / AIRPORT OF DESTINATION: {lc_port_of_discharge}
- LC FINAL DESTINATION: {lc_final_destination}
- LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule16_hdlc(lc_data, contract_data):
    lc_final_destination = lc_data.get('final_destination', {}).get('value', '')
    lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_final_destination = contract_data.get('final_destination', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the FINAL DESTINATION / PLACE OF DELIVERY condition in the Letter of Credit (LC) matches the one in the contract.

Inputs:
- LC Final Destination / Place of Delivery
- LC ADDITIONAL CONDITIONS (F47A)
- CONTRACT FINAL DESTINATION / PLACE OF DELIVERY

Overall rule: FINAL DESTINATION / PLACE OF DELIVERY in LC must match the FINAL DESTINATION / PLACE OF DELIVERY in the contract. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If both LC and contract have values and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have values but they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": true}
- Case "5": If both LC and contract do not have values. Return {"case": "5", "is_compliance": false}

Note:
- The FINAL DESTINATION / PLACE OF DELIVERY in LC can appear in ADDITIONAL CONDITIONS (F47A).
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT FINAL DESTINATION / PLACE OF DELIVERY: {contract_final_destination}
- LC FINAL DESTINATION / PLACE OF DELIVERY: {lc_final_destination}
- LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule17_hdlc(lc_data, contract_data):
    lc_latest_shipment_date = lc_data.get('f44C_latest_date_of_ship', {}).get('value', '')
    lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_latest_shipment_date = contract_data.get('f44C_latest_date_of_ship', {}).get('value', '')
    contract_date = contract_data.get('contract_date', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the LATEST DATE OF SHIPMENT condition in the Letter of Credit (LC) matches the one in the contract.

Inputs:
- LC Latest Date of Shipment
- LC ADDITIONAL CONDITIONS (F47A)
- CONTRACT LATEST DATE OF SHIPMENT
- CONTRACT DATE

Overall rule: LATEST DATE OF SHIPMENT in LC must match the LATEST DATE OF SHIPMENT in the contract. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Determine the LATEST DATE OF SHIPMENT in the contract:
- CONTRACT LATEST DATE OF SHIPMENT is specific date, use this value
- CONTRACT LATEST DATE OF SHIPMENT like shipemnt period time (7 days, 10 days, 15 days, etc.), new CONTRACT LATEST DATE OF SHIPMENT = CONTRACT DATE + this period
- CONTRACT LATEST DATE OF SHIPMENT like a period of time (20-30/1/2025), the CONTRACT LATEST DATE OF SHIPMENT is last day of this period
- CONTRACT LATEST DATE OF SHIPMENT is not have value, consider it is null and compare with LC LATEST DATE OF SHIPMENT

Detail conditions:
- Case "1": If both LC and contract have values and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have values but they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": true}
- Case "5": If both LC and contract do not have values. Return {"case": "5", "is_compliance": false}

Note:
- The LATEST DATE OF SHIPMENT in LC can appear in ADDITIONAL CONDITIONS (F47A).
- Determine the LATEST DATE OF SHIPMENT in the contract before compare with LC LATEST DATE OF SHIPMENT
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}

Example:
Input 1:
- CONTRACT LATEST DATE OF SHIPMENT: April or Early May, 2025
- CONTRACT DATE: 31-Mar-25
- LC LATEST DATE OF SHIPMENT: 31/05/2025
Output 1:
{"explanation": "The LATEST DATE OF SHIPMENT in the contract is a period of time (April or Early May, 2025), so the CONTRACT LATEST DATE OF SHIPMENT = Early May, 2025. The LC LATEST DATE OF SHIPMENT is 31/05/2025, so they are different.", "case": "2", "is_compliance": false}

Input 2:
- CONTRACT LATEST DATE OF SHIPMENT: 31-Mar-25
- CONTRACT DATE: 31-Mar-25
- LC LATEST DATE OF SHIPMENT: 31/05/2025
Output 2:
{"explanation": "The LATEST DATE OF SHIPMENT in the contract is a specific date (31-Mar-25), so the CONTRACT LATEST DATE OF SHIPMENT = 31-Mar-25. The LC LATEST DATE OF SHIPMENT is 31/05/2025, so they are the same.", "case": "1", "is_compliance": true}

Input 3:
- CONTRACT LATEST DATE OF SHIPMENT: May, 2025
- CONTRACT DATE: 31-Mar-25
- LC LATEST DATE OF SHIPMENT: 31/05/2025
Output 3: 
{"explanation": "The LATEST DATE OF SHIPMENT in the contract is a period of time (May, 2025), so the CONTRACT LATEST DATE OF SHIPMENT = 31, May, 2025 (last day of this period). The LC LATEST DATE OF SHIPMENT is 31/05/2025, so they are the same.", "case": "1", "is_compliance": true}
    """

    user_prompt = f""" 
- CONTRACT LATEST DATE OF SHIPMENT: {contract_latest_shipment_date}
- CONTRACT DATE: {contract_date}
- LC LATEST DATE OF SHIPMENT: {lc_latest_shipment_date}
- LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message



def generate_prompt_rule18_hdlc(lc_data, contract_data):
        lc_shipment_period = lc_data.get('f44D_shipment_period', {}).get('value', '')
        lc_latest_shipment_date = lc_data.get('f44C_latest_date_of_ship', {}).get('value', '')
        lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
        contract_shipment_period = contract_data.get('f44D_shipment_period', {}).get('value', '')
 
        system_prompt = """
    You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the SHIPMENT PERIOD condition in the Letter of Credit (LC) matches the one in the contract.
 
    Inputs:
    - CONTRACT SHIPMENT PERIOD
    - LC SHIPMENT PERIOD
    - LC LATEST DATE OF SHIPMENT
    - LC ADDITIONAL CONDITIONS (F47A)
 
    Overall rule: SHIPMENT PERIOD in LC must match the SHIPMENT PERIOD in the contract. If both LC and Contract have no value, only need to check the existance of LC LATEST DATE OF SHIPMENT.
    Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}
 
    Detail conditions: First compare SHIPMENT PERIOD, only if both LC and contract do not have values for SHIPMENT PERIOD, then check the existence of LC LATEST DATE OF SHIPMENT.
    - Case "1": If both LC SHIPMENT PERIOD and CONTRACT SHIPMENT PERIOD have values and they are the same. Return {"case": "1", "is_compliance": true}
    - Case "2": If both LC SHIPMENT PERIOD and CONTRACT SHIPMENT PERIOD have values but they are different. Return {"case": "2", "is_compliance": false}
    - Case "3": If CONTRACT SHIPMENT PERIOD has value but LC SHIPMENT PERIOD does not. Return {"case": "3", "is_compliance": false}
    - Case "4": If LC SHIPMENT PERIOD has value but CONTRACT SHIPMENT PERIOD does not. Return {"case": "4", "is_compliance": true}
    - Case "5": If both LC SHIPMENT PERIOD and CONTRACT SHIPMENT PERIOD do not have values. Check existence of LC LATEST DATE OF SHIPMENT. (Only need to check the existance of LC LATEST DATE OF SHIPMENT)
        - If LC LATEST DATE OF SHIPMENT has value. Return {"case": "5.1", "is_compliance": true}
        - If LC LATEST DATE OF SHIPMENT does not have value. Return {"case": "5.2", "is_compliance": false}
 
    Note:
    - First compare SHIPMENT PERIOD, only if both LC and contract do not have values for SHIPMENT PERIOD, then check the existence of LC LATEST DATE OF SHIPMENT (only check the existence of LC LATEST DATE OF SHIPMENT, not the value)
    - Explain briefly. No need to point out the specific case, just explain why it true/false.
 
    Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
 
    Example:
    Input 1:
    - CONTRACT SHIPMENT PERIOD: 01 MAY 2025 - 31 MAY 2025 (BOTH DATES INCLUSIVE)
    - LC SHIPMENT PERIOD:
    - LC LATEST DATE OF SHIPMENT: 31/05/2025
    - LC ADDITIONAL CONDITIONS (F47A): 
 
    Output 1:
    {"explanation": "The SHIPMENT PERIOD in the contract is 01 MAY 2025 - 31 MAY 2025 (BOTH DATES INCLUSIVE), the LC SHIPMENT PERIOD is not have value", "case": "3", "is_compliance": false}
        """
 
        user_prompt = f"""
    - CONTRACT SHIPMENT PERIOD: {contract_shipment_period}
    - LC SHIPMENT PERIOD: {lc_shipment_period}
    - LC LATEST DATE OF SHIPMENT: {lc_latest_shipment_date}
    - LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
        """
 
        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
 
        return message

def generate_prompt_rule19_hdlc(lc_data, contract_data):
    lc_period_presentation = lc_data.get('f48_period_of_present', {}).get('value', '')
    lc_additional_conditions = lc_data.get('f47A_additional_condition', {}).get('value', '')
    contract_period_presentation = contract_data.get('f48_period_of_present', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the PERIOD OF PRESENTATION condition in the Letter of Credit (LC) matches the one in the contract.

Inputs:
- CONTRACT PERIOD OF PRESENTATION
- LC Period of Presentation
- LC ADDITIONAL CONDITIONS (F47A)

Overall rule: PERIOD OF PRESENTATION in LC must match the PERIOD OF PRESENTATION in the contract. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
- Case "1": If both LC and contract have values and they are the same. Return {"case": "1", "is_compliance": true}
- Case "2": If both LC and contract have values but they are different. Return {"case": "2", "is_compliance": false}
- Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": false}
- Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": true}

Note:
- The PERIOD OF PRESENTATION in LC can appear in ADDITIONAL CONDITIONS (F47A).
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- CONTRACT PERIOD OF PRESENTATION: {contract_period_presentation}
- LC PERIOD OF PRESENTATION: {lc_period_presentation}
- LC ADDITIONAL CONDITIONS (F47A): {lc_additional_conditions}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message

def generate_prompt_rule20_hdlc(lc_data, contract_data):
    lc_goods_service = lc_data.get('f45A_goods_services', {}).get('value', '')
    contract_goods_service = contract_data.get('f45A_goods_services', {}).get('value', '')
    goods_services_metadata = contract_data.get('f45A_goods_services', {}).get('metadata', {})
    contract_goods_service_detail = ""
    quality = goods_services_metadata.get('bct_45a_quality', '')
    origin = goods_services_metadata.get('bct_45a_origin', '')
    trade_term = contract_data.get('f45A_goods_services_trade_term', {}).get("value", "")
    incoterm = contract_data.get('f45A_goods_services_incoterm', {}).get("value", "")
    contract_goods_service_detail += f"\n**QUALITY**: {quality} \n **ORIGIN**: {origin} \n **TRADE TERM**: {trade_term} **Incoterms**: {incoterm}\n"

    if goods_services_metadata:
        commodity = goods_services_metadata.get('bct_45a_desc_goods', {})
        if commodity:
            for i, c in enumerate(commodity):
                quantity_value = c.get('bct_45a_quantity_value') + ' ' + c.get('bct_45a_quantity_unit')
                commodity_name = c.get('bct_45a_commodity', '')
                unit_price = c.get('bct_45a_uprice_amount') + ' ' + c.get('bct_45a_uprice_currency') + '/' + c.get('bct_45a_uprice_unit')
                total_amount = c.get('bct_45a_total_amount_value') + ' ' + c.get('bct_45a_total_amount_unit')
                stt = str(i+1)
                contract_goods_service_detail += f"{stt}. COMMODITY: {commodity_name}; QUANTITY: {quantity_value}; UNIT PRICE: {unit_price}; AMOUNT: {total_amount}\n"
        
            
    lc_amount = lc_data.get('f32B_amount', {}).get('value', '')
    contract_amount = contract_data.get('contract_amount', {}).get('value', '')

    rule_description = """
1. COMMODITY/GOODS: (Always required)
   Information on LC matches contract information

2. QUANTITY (Depends on contract)
   Information on LC matches contract information
   If LC amount is less than contract amount, LC quantity can be less than contract quantity

3. UNIT PRICE (Depends on contract)
   Information on LC matches contract information

4. TOTAL AMOUNT (Depends on contract)
   Information on LC matches contract information

5. TOLERANCE (Depends on contract)
   Information on LC matches contract information

6. QUALITY (Depends on contract)
   Information on LC matches contract information

7. TRADE TERM (Depends on contract)
   Information on LC matches contract information

8. INCOTERMS (Depends on contract)
   Information on LC matches contract information

9. ORIGIN (Depends on contract)
   Information on LC matches contract information

10. PACKING (Depends on contract)
    Information on LC matches (in meaning) contract information

11. HS CODE
    Information on LC matches contract information

12. Amount paid by LC (LC amount/amount paid by LC)
    Information on LC matches contract information

13. Specifications/model
    Information on LC matches contract information

14. Mill/Manufacturer/supplier/end user
    Information on LC matches contract information

15. Shipping mark/Marks and nos
    Information on LC matches contract information

16. Size/Dimensions
    Information on LC matches contract information

17. Contract number/date
    Information on LC matches contract information

+ Cross-check information on LC and Contract

Case 1: If both LC and contract specify the same information: T
Case 2: If both LC and contract specify but different information: F
Case 3: If contract has information but LC doesn't: T
Case 4: If LC has information but contract doesn't: F. Exception for Case 4: except for Incoterms (many contracts don't specify)
"""

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of various fields between the Letter of Credit (LC) and the contract.

Inputs: A description of GOODS/SERVICE in LC and contract that may contain following fields:
- COMMODITY/GOODS
- QUANTITY (if LC amount is less than contract amount, LC quantity can be less than contract quantity)
- UNIT PRICE
- TOTAL AMOUNT
- TOLERANCE
- QUALITY
- TRADE TERM
- INCOTERMS
- ORIGIN
- PACKING
- HS CODE
- AMOUNT
- SPECIFICATIONS/MODEL
- MILL/MANUFACTURER/SUPPLIER/END USER
- SHIPPING MARK/MARKS AND NOS
- SIZE/DIMENSIONS
- CONTRACT NUMBER
- CONTRACT DATE

IMPORTANT COMPARISON GUIDELINES:

1. FUZZY MATCHING FOR TEXT FIELDS: Apply fuzzy string matching for text-based fields to handle minor spelling errors, typos, and variations. Consider fields as matching if they have substantial similarity (>85% similarity) even with minor differences in:
   - Commodity/goods names
   - Origin/country names  
   - Manufacturer/supplier names
   - Specifications/models
   - Quality descriptions
   - Packing descriptions
   
   SPECIAL CHARACTER SUBSTITUTION HANDLING: Before applying fuzzy matching, normalize common OCR/typing errors by treating these character pairs as equivalent:
   - B ↔ 8 (e.g., "TRB115" matches "TR8115")
   - S ↔ 5 (e.g., "TR811S" matches "TR8115") 
   - O ↔ 0 (e.g., "CO2" matches "C02")
   - I ↔ 1 ↔ l (e.g., "TI1" matches "T11" matches "Tl1")
   - G ↔ 6 (e.g., "G6" matches "66")
   - Z ↔ 2 (e.g., "Z2" matches "22")
   - q ↔ 9 (e.g., "q9" matches "99")
   - Apply this normalization to product codes, model numbers, and specifications before comparison
   
2. AGGREGATED COMPARISON FOR QUANTITIES AND AMOUNTS: When comparing goods that may be split differently between LC and contract:
   - Compare TOTAL quantities across all items of the same commodity type
   - Compare TOTAL amounts across all items of the same commodity type
   - If the same goods are listed as 1 item in contract but split into multiple items in LC (or vice versa), aggregate the quantities and amounts before comparison
   - Consider compliant if aggregated totals match, even if individual line items differ

3. FLEXIBLE COMMODITY GROUPING: When the same commodity appears multiple times with different specifications:
   - Group by main commodity type first
   - Then compare aggregated quantities and amounts within each group
   - Allow for different ways of describing the same product

Overall rule: Compare each field between LC and contract. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
Case "1": If both LC and contract specify the same value for a field (including fuzzy matches). Return {"case": "1", "is_compliance": true}
Case "2": If both LC and contract specify different values for a field (after fuzzy matching and aggregation). Return {"case": "2", "is_compliance": false}
Case "3": If contract has value but LC does not, compliance is still guaranteed. Return {"case": "3", "is_compliance": true}
Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": false}

Special cases:
    - For QUANTITY: If LC amount is less than contract amount, LC quantity can be less than contract quantity. Use aggregated comparison.
    - For INCOTERMS: If the contract does not specify but the LC does, it is still followed. If both have the same value but different information, return {"case": "2", "is_compliance": false}
    - For COMMODITY/GOODS: Must always be present and match between LC and contract (use fuzzy matching)
    - For AMOUNTS: Use aggregated comparison when goods are split differently

Note:
    - Apply character normalization for common OCR/typing errors before fuzzy matching
    - Apply fuzzy matching tolerance for text fields to account for spelling variations
    - Use aggregated comparison for quantities and amounts when dealing with split items
    - Only provide specific explanation of the comparison for each field that is non-compliant. Otherwise, explain briefly
    - If multiple fields are non-compliant, list all non-compliant fields in the explanation
    - Mention when character normalization, fuzzy matching or aggregated comparison was applied

Response in json format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
    L/C Information:
        - LC GOODS/SERVICE: {lc_goods_service}
        - LC AMOUNT: {lc_amount}
    CONTRACT Information:
        - CONTRACT GOODS/SERVICE: {contract_goods_service}
        - Detailed information on EACH type of contract GOODS/SERVICE: {contract_goods_service_detail}
        - CONTRACT AMOUNT: {contract_amount}

Please apply fuzzy matching for text comparisons and aggregated comparison for quantities/amounts when evaluating compliance.
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule21_hdlc(lc_data, contract_data):
    lc_documents_required = lc_data.get('f46A_documents_requires', {}).get('value', '')
    contract_documents_required = contract_data.get('f46A_documents_requires', {}).get('value', '')

    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the DOCUMENTS REQUIRED condition between the Letter of Credit (LC) and the contract.

Inputs:
- LC DOCUMENTS REQUIRED
- CONTRACT DOCUMENTS REQUIRED

**Compliance Rules:**
1. **LC can require MORE documents than contract** = COMPLIANT (LC is more restrictive for security)
2. **Contract requires documents that LC does NOT have** = NON-COMPLIANT (LC fails to meet contract requirements)
3. **Both have same document types** = COMPLIANT 
4. **Both have documents but completely different sets** = NON-COMPLIANT

**Document Matching Logic:**
- Focus on CORE document types (Invoice, Bill of Lading, Packing List, Insurance, Certificate of Origin, etc.)
- LC specifications (copies, originals, endorsements, specific details) are enhancements, not different documents
- Example: "Commercial Invoice" in contract matches "Signed Commercial Invoice in 3 Originals" in LC

**Evaluation Cases:**

**Case 1**: Both LC and Contract require the same core document types
- All contract documents are covered in LC (LC may have additional details/requirements)
- Return: {"case": "1", "is_compliance": true}

**Case 2**: Both have documents but contract requires core documents that LC completely lacks
- Contract specifies documents that LC does not mention at all
- Return: {"case": "2", "is_compliance": false}

**Case 3**: Contract has specific document requirements but LC has no document requirements
- Contract specifies documents but LC DOCUMENTS REQUIRED is empty/null
- Return: {"case": "3", "is_compliance": false}

**Case 4**: LC has document requirements but Contract has no document requirements  
- LC specifies documents but CONTRACT DOCUMENTS REQUIRED is empty/null
- Return: {"case": "4", "is_compliance": true}

**Analysis Instructions:**
1. Extract core document types from both LC and Contract (ignore formatting details)
2. Check if all CONTRACT document types are present in LC document types
3. Additional LC documents beyond contract requirements are acceptable
4. Missing contract-required documents in LC = non-compliance

Response in JSON format, without markdown formatting:
{"explanation": "Brief explanation of document comparison and compliance result", "case": "case_number", "is_compliance": true/false}
    """

    user_prompt = f"""
LC DOCUMENTS REQUIRED: {lc_documents_required}
CONTRACT DOCUMENTS REQUIRED: {contract_documents_required}

Please analyze the document requirements compliance according to the evaluation rules.
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message