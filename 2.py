import json

# Raw input string
input_str = """323$ABBank - Ngân hàng An Bình$ABBank - An Binh Bank$^307$ACB - Ngân hàng Á Châu$ACB - Asia Commercial Bank$^602$ANZ - Ngân hàng ANZ VN$ANZ Bank Vietnam$^204$Agribank - Ngân hàng NN và PTNT VN$Agribank - Vietnam Bank for Agriculture and Rural Development$^202$BIDV - Ngân hàng ĐT và PT VN$BIDV - Bank for Investment and Development of Vietnam$^614$BNP - PARIBAS$BNP - PARIBAS$^313$BacABank - Ngân hàng Bắc Á$BacABank - North Asia Bank$^615$Bank of Communications$Bank of Communications$^359$BaoVietBank - Ngân hàng Bảo Việt$BaoVietBank - BaoViet Bank$^339$CBBank - Ngân hàng Xây dựng$CBBank - Vietnam Construction Bank$^611$China Construction Bank Corp$China Construction Bank Corp$^654$Citibank N.A CN TP HCM$Ngan hang Citibank N.A CN TP HCM$^605$Citibank VN$Citibank Vietnam$^808$Công ty Tài chính JACCS$Cong ty Tai chinh JACCS$^304$DongABank - Ngân hàng Đông Á$DongABank - DongA Bank$^658$Esun Bank CN Đồng Nai$NH NH TNHH E.SUN CN Dong Nai$^305$Eximbank - Ngân hàng Xuất nhập khẩu$Eximbank - Vietnam Export Import Bank$^630$First Commercial Bank$NH First Commercial Bank$^608$First Commercial Bank Hà Nội$First Commercial Bank Ha Noi$^320$GPBank - Ngân hàng Dầu khí toàn cầu$GPBank - GP Bank$^321$HDBank - Ngân hàng Phát triển TPHCM$HDBank - HD Bank$^617$HSBC Bank VN$HSBC Bank Vietnam$^656$Hana Bank CN TP Hồ Chí Minh$Hana Bank CN TP Hồ Chí Minh$^649$ICBC - Ngân Hàng Công Thương Trung Quốc $Industrial and Commer Bank of China$^502$IVB - Ngân hàng Indovina$IVB - Indovina Bank$^353$KienLongBank - Ngân hàng Kiên Long$KienLongBank - Kien Long Bank$^357$LienvietPostbank - Ngân hàng Bưu điện Liên Việt$LienvietPostbank - Lien Viet Post Bank$^311$MB - Ngân hàng Quân Đội$MB - MB Bank$^302$MaritimeBank - Ngân hàng Hàng Hải$MaritimeBank - Maritime Bank$^352$NCB - Ngân hàng Quốc Dân$NCB - National Citizen Bank$^601$NH BPCEIOM CN TPHCM$NH BPCEIOM CN TPHCM$^653$NH MUFG - CN Hà Nội$MUFG Bank Hanoi$^655$NH Taipei Fubon CN Binh Duong$NH Taipei Fubon CN Binh Duong$^651$NHTM Taipei Fubon CN TP HCM$NHTM Taipei Fubon CN TP HCM$^324$NHTMCP Việt Hoa$NHTMCP Viet Hoa$^315$NHTMCP Vũng tàu$NHTMCP Vung tau$^306$NamABank - Ngân hàng Nam Á$NamABank - Nam A Bank$^652$Ngân Hàng Công Nghiệp Hàn Quốc CN Hà Nội$NH Cong nghiep Han Quoc CN Ha Noi$^657$Ngân hàng BNP Paribas$Ngân hàng BNP Paribas$^333$OCB - Ngân hàng Phương Đông$OCB - Orient Commercial Bank$^319$OceanBank - Ngân hàng Đại Dương$OceanBank - Ocean Bank$^341$PGBank - Ngân hàng Xăng dầu Petrolimex$PGBank - Petrolimex Group Bank$^360$PVcomBank – Ngân hàng Đại chúng Việt Nam $PVcomBank – Vietnam Public Bank $^334$SCB - Ngân hàng Sài Gòn$SCB - Saigon Commercial Bank$^303$Sacombank - Ngân hàng Sài Gòn Thương Tín$Sacombank - Sacom Bank$^308$Saigonbank - Ngân hàng Sài Gòn Công thương$Saigonbank - Saigon bank for industry and trade$^317$SeABank - Ngân hàng Đông Nam Á$SeABank - Southeast Asia Bank$^358$TPB - Ngân hàng Tiên Phong$TPBank - Tienphong Bank$^310$Techcombank - Ngân hàng Kỹ Thương$Techcombank - Technological and Commercial Bank$^645$The Hongkong and shanghai Banking Corporation Limited$NH The Hongkong and Shanghai$^606$The Shanghai C S Bank CNĐồng Nai$The Shanghai C S Bank CN Dong Nai$^600$The Siam Commercial Bank$NH THE SIAM COMMERCIAL BANK$^208$VDB - Ngân hàng Phát triển Việt Nam$NH Phat trien Viet Nam$^314$VIB - Ngân hàng Quốc Tế$VIB - Vietnam International Bank$^309$VPBank - Ngân hàng Việt Nam Thịnh Vượng$VPBank - Vietnam Prosperity Bank$^505$VRB - Ngân hàng liên doanh Việt Nga$VRB - Vietnam Russia Bank$^355$VietABank - Ngân hàng Việt Á$VietABank - Viet A Bank$^356$VietBank - Ngân hàng Việt Nam Thương Tín$NH TMCP Viet Nam Thuong Tin$^203$Vietcombank - Ngân hàng Ngoại thương$Vietcombank - Bank for Foreign trade of Vietnam$^201$Vietinbank - Ngân hàng Công thương$VietinBank - Vietin Bank$^663$Woori Bank VN$NGAN HANG WOORI VIET NAM$^612$Bangkok Bank VN$Bangkok Bank Vietnam$^620$Bank Of China - CN Tp."""

banks_list = []

# Split the input string by '^'
entries = input_str.split('$^')
print(entries)

# Iterate over the entries
for entry in entries:
    # Split each entry by '$'
    parts = entry.split('$')
    if len(parts) == 3:
        bank_code, bank_name_1, bank_name_2 = parts
        # Extract the CIF code from the bank_code part
        bank_cif = bank_code.strip()
        # Create a dictionary for each bank
        bank_dict = {
            "bank_cif": bank_cif,
            "bank_short_name": bank_name_1.strip(),
            "bank_name": bank_name_2.strip()
        }
        # Add the dictionary to the list
        banks_list.append(bank_dict)

# Convert the list to JSON
json_output = json.dumps(banks_list, indent=4, ensure_ascii=False)

# Save to JSON file
with open('banks_shb.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)

print("JSON file 'banks.json' has been created.")
