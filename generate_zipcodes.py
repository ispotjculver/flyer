#!/usr/bin/env python3
"""Generate comprehensive US ZIP codes file"""

# Major US ZIP code ranges by state/region
zip_ranges = [
    # Northeast
    range(1001, 2791),   # MA, RI, NH, ME, VT
    range(3031, 3897),   # NH, VT
    range(4001, 4992),   # ME
    range(5001, 5907),   # VT
    range(6001, 6928),   # CT
    range(7001, 8989),   # NJ
    range(10001, 14975), # NY
    range(15001, 19640), # PA
    range(20001, 20799), # DC
    range(20812, 21930), # MD
    range(22001, 24658), # VA
    range(25001, 26886), # WV
    range(27006, 28909), # NC
    range(29001, 29948), # SC
    
    # Southeast
    range(30001, 39901), # GA
    range(32004, 34997), # FL
    range(35004, 36925), # AL
    range(37010, 38589), # TN
    range(38601, 39776), # MS
    range(40003, 42788), # KY
    range(43001, 45999), # OH
    range(46001, 47997), # IN
    range(48001, 49971), # MI
    
    # Midwest
    range(50001, 52809), # IA
    range(53001, 54990), # WI
    range(55001, 56763), # MN
    range(57001, 57799), # SD
    range(58001, 58856), # ND
    range(59001, 59937), # MT
    range(60001, 62999), # IL
    range(63001, 65899), # MO
    range(66002, 67954), # KS
    range(68001, 69367), # NE
    
    # Southwest
    range(70001, 71497), # LA
    range(71601, 72959), # AR
    range(73001, 74966), # OK
    range(75001, 79999), # TX
    range(80001, 81658), # CO
    range(82001, 83128), # WY
    range(83201, 83876), # ID
    range(84001, 84791), # UT
    range(85001, 86556), # AZ
    range(87001, 88441), # NM
    range(88901, 89883), # NV
    
    # West Coast
    range(90001, 96162), # CA
    range(97001, 97920), # OR
    range(98001, 99403), # WA
    
    # Alaska & Hawaii
    range(99501, 99950), # AK
    range(96701, 96898), # HI
]

def generate_zipcodes():
    zipcodes = set()
    
    # Generate from ranges
    for zip_range in zip_ranges:
        for zipcode in zip_range:
            # Format as 5-digit string
            zipcodes.add(f"{zipcode:05d}")
    
    # Add some specific ZIP codes that might be missed
    specific_zips = [
        "00501", "00544", "00601", "00602", "00603", "00604", "00605", "00606", "00610", "00611",
        "00612", "00613", "00614", "00615", "00616", "00617", "00622", "00623", "00624", "00627",
        "00628", "00631", "00633", "00634", "00635", "00636", "00637", "00638", "00639", "00641",
        "00646", "00647", "00648", "00649", "00650", "00651", "00652", "00653", "00654", "00655",
        "00656", "00657", "00658", "00659", "00660", "00661", "00662", "00663", "00664", "00665",
        "00666", "00667", "00668", "00669", "00670", "00671", "00672", "00673", "00674", "00675",
        "00676", "00677", "00678", "00679", "00680", "00681", "00682", "00683", "00684", "00685",
        "00686", "00687", "00688", "00689", "00690", "00691", "00692", "00693", "00694", "00695",
        "00696", "00697", "00698", "00699"
    ]
    
    for zipcode in specific_zips:
        zipcodes.add(zipcode)
    
    return sorted(list(zipcodes))

if __name__ == "__main__":
    zipcodes = generate_zipcodes()
    
    with open('zipcodes.txt', 'w') as f:
        for zipcode in zipcodes:
            f.write(f"{zipcode}\n")
    
    print(f"Generated {len(zipcodes)} ZIP codes")