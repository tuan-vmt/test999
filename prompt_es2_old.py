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


Overall rule: DATE OF EXPIRY in LC must match the REFINE DATE OF EXPIRY term in Contract. REFINE DATE OF EXPIRY term in Contract may depend on the other information.  Respond in JSON format, without markdown formatting: {"explanation": "...", "case": "...", "is_compliance": true/false}

Evaluation rules:

Case "1": 
- If the DATE OF EXPIRY in Contract specifies a **fixed expiry date**, REFINE DATE OF EXPIRY term in Contract = DATE OF EXPIRY. 
- Then comapre if Contract REFINE DATE OF EXPIRY matches the LC expiry date. Return {"case": "1", "is_compliance": true/false}
Case "2"
- If the contract specifies expiry using a **relative term** (e.g., "30 days after shipment"), compute the REFINE DATE OF EXPIRY term in Contract by:
    + If LATEST DATE OF SHIPMENT has value: REFINE DATE OF EXPIRY = LATEST DATE OF SHIPMENT + DATE OF EXPIRY term in Contract
    + If LATEST DATE OF SHIPMENT has no value: REFINE DATE OF EXPIRY = LC ISSUANCE DATE + DATE OF EXPIRY term in Contract
    + Then comapre if REFINE DATE OF EXPIRY matches the LC expiry date. Return {"case": "2", "is_compliance": true/false}
Case "3"
- Case "3.1": If the contract does **not mention expiry**, but LATEST DATE OF SHIPMENT is available:
    - If PERIOD OF PRESENTATION is also available. Return DATE OF EXPIRY = LATEST DATE OF SHIPMENT + PERIOD OF PRESENTATION. Return case "3.1.1"
    - If PERIOD OF PRESENTATION is not available. Return DATE OF EXPIRY = LATEST DATE OF SHIPMENT + 21 days. Return case "3.1.2"
- Case "3.2": If DATE OF EXPIRY is not in the contract, and LATEST DATE OF SHIPMENT is also not available. Return {"case": "3.2", "is_compliance": false}

Note:
- Match even if date formats differ but the dates mean the same.
- Use best estimate based on available fields.

Response in json format, without markdown formating: {"explanation": ..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
LC Expiry Date: {lc_expiry_date}
Contract Expiry Term: {contract_expiry_date}
Latest Shipment Date: {latest_shipment_date}
Period of Presentation: {period_of_presentation}
LC Issuance Date: {lc_issuance_date}
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
You are an international trade document analyst with expertise in Letters of Credit (LC) and trade contracts. Your task is to evaluate the compliance of the TENOR field between the contract and the LC.

Inputs:
- LC TENOR
- LC ADDITIONAL CONDITIONS
- LC DOCUMENTS REQUIRED
- LC REIMBURSING BANK
- CONTRACT TENOR

Overall rule: Evaluate if the LC is UPAS (Usance Payment at Sight) and check tenor compliance accordingly. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:

Case "1": If LC is not UPAS (either tenor is sight/at sight OR reimbursing bank is empty):
    - If LC TENOR matches CONTRACT TENOR: Return {"case": "1.1", "is_compliance": true}
    - If LC TENOR does not match CONTRACT TENOR: Return {"case": "1.2", "is_compliance": false}

Case "2": If LC is UPAS (tenor is not sight/at sight AND reimbursing bank has value):
    - Case "2.1": If LC TENOR matches CONTRACT TENOR: Return {"case": "2.1", "is_compliance": true}
    - Case "2.2": If LC TENOR does not match CONTRACT TENOR:
        Check ADDITIONAL CONDITIONS for UPAS clause containing:
        - Payment timing matching contract tenor
        - Interest costs for applicant
        - Reimbursement instructions
        If found:
            - If payment timing matches contract tenor: Return {"case": "2.2.1", "is_compliance": true}
            - If payment timing does not match contract tenor: Return {"case": "2.2.2", "is_compliance": false}
            - If no payment timing found: Return {"case": "2.2.3", "is_compliance": false}

Note:
- UPAS clauses typically contain phrases like "IRRESPECTIVE OF THE TENOR", "NOTWITHSTANDING THE TENOR", "Despite the tenor"
- Payment timing must match the contract tenor exactly
- Explain briefly. No need to point out the specific case, just explain why it true/false.

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- LC TENOR: {lc_tenor}
- LC ADDITIONAL CONDITIONS: {lc_additional_conditions}
- LC DOCUMENTS REQUIRED: {lc_documents_required}
- LC REIMBURSING BANK: {lc_reimbursing_bank}
- CONTRACT TENOR: {contract_tenor}
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
        - If LC LATEST DATE OF SHIPMENT has value. Return {"case": "5", "is_compliance": true}
        - If LC LATEST DATE OF SHIPMENT does not have value. Return {"case": "6", "is_compliance": false}

    Note:
    - First compare SHIPMENT PERIOD, only if both LC and contract do not have values for SHIPMENT PERIOD, then check the existence of LC LATEST DATE OF SHIPMENT (only check the existence of LC LATEST DATE OF SHIPMENT, not the value)
    - Explain briefly. No need to point out the specific case, just explain why it true/false.

    Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}

    Example:
    Input 1:
    - CONTRACT SHIPMENT PERIOD: 01 MAY 2025 - 31 MAY 2025 (BOTH DATES INCLUSIVE)
    - LC SHIPMENT PERIOD: 
    - CONTRACT LATEST DATE OF SHIPMENT: 31 MAY 2025
    - LC LATEST DATE OF SHIPMENT: 31/05/2025

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

    lc_amount = lc_data.get('f32B_amount', {}).get('value', '')
    contract_amount = contract_data.get('contract_amount', {}).get('value', '')

    rule_description = """
1. COMMODITY/ GOODS: (Luôn có)

Thông tin trên đơn khớp với thông tin trên hợp đồng
2. QUANTITY (Tùy hơp đồng)

Thông tin trên đơn khớp với thông tin trên hợp đồng
Trường hợp trị giá LC nhỏ hơn trị giá hợp đồng thì quantity trên đơn sẽ nhỏ hơn quantity trên hợp đồng
3. UNIT PRICE (Tùy hơp đồng)

Thông tin trên đơn khớp với thông tin trên hợp đồng
4. TOTAL AMOUNT (Tùy hơp đồng)

Thông tin trên đơn khớp với thông tin trên hợp đồng
5. TOLERANCE (Tùy hơp đồng)

Thông tin trên đơn khớp với thông tin trên hợp đồng
6. QUALITY (Tùy hơp đồng)

Thông tin trên đơn khớp  với thông tin trên hợp đồng
7. TRADE TERM (Tùy hơp đồng)

Thông tin trên đơn khớp với thông tin trên hợp đồng
8.  INCOTERMS (Tùy hơp đồng)

Thông tin trên đơn khớp với thông tin trên hợp đồng
9.  ORIGIN (Tùy hơp đồng)

Thông tin trên đơn khớp với thông tin trên hợp đồng
10. PACKING (Tùy hơp đồng)

Thông tin trên đơn khớp (ý nghĩa) với thông tin trên hợp đồng
11. HS code

Thông tin trên đơn khớp với thông tin trên hợp đồng
12.  Trị giá thanh toán bằng LC (LC amount/ amount paid by LC)

Thông tin trên đơn khớp với thông tin trên hợp đồng
13.  Specifications/model

Thông tin trên đơn khớp với thông tin trên hợp đồng
14. Mill/Manufacturer/supplier/end user:

Thông tin trên đơn khớp với thông tin trên hợp đồng
15. Shipping mark/ Marks and nos

Thông tin trên đơn khớp với thông tin trên hợp đồng
16.  Size/ Dimensions

Thông tin trên đơn khớp với thông tin trên hợp đồng
17. Contract number/date

Thông tin trên đơn khớp với thông tin trên hợp đồng
+ Đối chiếu thông tin trên LC và HĐ

TH1: Nếu LC và hợp đồng đều quy định và giống nhau: T,
TH2: Nếu LC và hợp đồng đều quy định nhưng khác nhau: F
TH3: Nếu HĐ có thông tin LC không có thông tin: T,
TH4: Nếu LC có thông tin HĐ không có thông tin: F. Ngoại lệ cho TH 4: ngoại trừ Incoterms (nhiều HĐ không quy định)
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

Overall rule: Compare each field between LC and contract. Respond in JSON format, without markdown formatting: {"explanation":..., "case": "...", "is_compliance": true/false}

Detail conditions:
Case "1": If both LC and contract specify the same value for a field. Return {"case": "1", "is_compliance": true}
Case "2": If both LC and contract specify different values for a field. Return {"case": "2", "is_compliance": false}
Case "3": If contract has value but LC does not. Return {"case": "3", "is_compliance": true}
Case "4": If LC has value but contract does not. Return {"case": "4", "is_compliance": false}

Special cases:
- For QUANTITY: If LC amount is less than contract amount, LC quantity can be less than contract quantity
- For INCOTERMS: If contract does not specify but LC does, it is still compliant
- For COMMODITY/GOODS: Must always be present and match between LC and contract

Note:
- Only provide specific explanation of the comparison for each field that is non-compliant. Otherwise, explain briefly. No need to point out the specific case, just explain why it true/false
- If multiple fields are non-compliant, list all non-compliant fields in the explanation

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- LC GOODS/SERVICE: {lc_goods_service}
- CONTRACT GOODS/SERVICE: {contract_goods_service}
- LC AMOUNT: {lc_amount}
- CONTRACT AMOUNT: {contract_amount}
    """


    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message


def generate_prompt_rule21_hdlc(lc_data, contract_data):
    lc_documents_required = lc_data.get('f46A_documents_requires', {}).get('value', '')
    contract_documents_required = contract_data.get('f46A_documents_requires', {}).get('value', '')

    Rule = """Đối chiếu danh sách chứng từ được liệt kê trong 2 văn bản, nếu đơn có chứng từ này nhưng hợp đồng không có → thỏa mãn, nếu hợp đồng có đơn
không có → cảnh báo, nếu cả 2 đều có giống nhau → thỏa mãn, nếu cả 2 đều có nhưng khác nhau → cảnh báo
TH1: Nếu LC và hợp đồng đều quy định và giống nhau: T,
TH2: Nếu LC và hợp đồng đều quy định nhưng khác nhau: F
TH3: Nếu HĐ có thông tin LC không có thông tin: T,
TH4: Nếu LC có thông tin HĐ không có thông tin: F"""
    system_prompt = """
You are an international trade document analyst with expertise in Letters of Credit and trade contracts. Your task is to evaluate the compliance of the DOCUMENTS REQUIRED condition in the Letter of Credit (LC) matches the one in the contract. The DOCUMENTS REQUIRED is often contains list of documents that are required to be presented to the bank.

Inputs:
- LC DOCUMENTS REQUIRED
- CONTRACT DOCUMENTS REQUIRED

Overall rule: Compare the list of documents listed in LC DOCUMENTS REQUIRED with CONTRACT DOCUMENTS REQUIRED. If the LC DOCUMENTS REQUIRED has this document but the CONTRACT DOCUMENTS REQUIRED does not have it, it is still satisfy. If the CONTRACT DOCUMENTS REQUIRED has this document but the LC DOCUMENTS REQUIRED does not have it, it is not satisfy. If both have the same documents, it is satisfy. If both have documents but they are different, it is not satisfy.

Detail conditions:  
Case "1": If both LC DOCUMENTS REQUIRED and CONTRACT DOCUMENTS REQUIRED have the same documents. Return {"case": "1", "is_compliance": true}
Case "2": If both LC DOCUMENTS REQUIRED and CONTRACT DOCUMENTS REQUIRED have documents but they are different. Return {"case": "2", "is_compliance": false}
Case "3": If CONTRACT DOCUMENTS REQUIRED has document but LC DOCUMENTS REQUIRED does not. Return {"case": "3", "is_compliance": true}
Case "4": If LC DOCUMENTS REQUIRED has document but CONTRACT DOCUMENTS REQUIRED does not. Return {"case": "4", "is_compliance": false}

Note:
- Explain briefly. No need to point out the specific case, just explain why it true/false.
- Point out the document that is different in the list (if any)

Response in json format, without markdown formating: {"explanation":..., "case": "...", "is_compliance": true/false}
    """

    user_prompt = f"""
- LC DOCUMENTS REQUIRED: {lc_documents_required}
- CONTRACT DOCUMENTS REQUIRED: {contract_documents_required}
    """

    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return message
