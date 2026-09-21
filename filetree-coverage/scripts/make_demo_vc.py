#!/usr/bin/env python3
"""
Builds a small fictional venture-financing document set (Halcyon Robotics,
Inc., an invented Delaware company: Seed 2022, Series A 2023, Series B 2025)
so the chronology skill can be exercised. Everything is invented.

The set contains the traps a chronology has to get right: amendments that
layer on a base agreement, restatements that supersede the base and its
amendments, an unsigned draft of a later restatement, a document filed in the
wrong round's folder, a certificate of amendment beside a restated charter,
SAFEs that converted at the priced round, and a side letter that modifies a
restated agreement for one investor only.

Run:  python make_demo_vc.py ./demo_vc
"""
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "demo_vc")
FILES = {}

CO = "Halcyon Robotics, Inc."
BOILER = {
    "law": "This Agreement shall be governed by and construed in accordance with the General Corporation Law of the State of Delaware as to matters within the scope thereof, and as to all other matters shall be governed by and construed in accordance with the internal laws of the State of Delaware.",
    "counterparts": "This Agreement may be executed in two or more counterparts, each of which shall be deemed an original, but all of which together shall constitute one and the same instrument. Counterparts may be delivered via electronic mail (including PDF or any electronic signature complying with the U.S. federal ESIGN Act of 2000) and any counterpart so delivered shall be deemed to have been duly and validly delivered.",
    "entire": "This Agreement (including the Exhibits hereto), and the other Transaction Agreements constitute the full and entire understanding and agreement between the parties with respect to the subject matter hereof, and any other written or oral agreement relating to the subject matter hereof existing between the parties is expressly canceled.",
}


def signed(*names):
    lines = ["IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.", "", f"{CO.upper()}", "", "By: /s/ Dana Okafor", "Name: Dana Okafor", "Title: Chief Executive Officer", ""]
    for n in names:
        lines += [n.upper(), "", "By: /s/ " + n.split(" ")[0] + " Signatory", "Name:", "Title: Managing Director", ""]
    return "\n".join(lines)


def unsigned(*names):
    lines = ["IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.", "", f"{CO.upper()}", "", "By: ______________________", "Name: Dana Okafor", "Title: Chief Executive Officer", ""]
    for n in names:
        lines += [n.upper(), "", "By: ______________________", "Name: [●]", "Title: [●]", ""]
    return "\n".join(lines)


def doc(path, *paras):
    FILES[path] = "\n\n".join(paras)


# ---------------------------------------------------------------- 01 Charter
doc("01 Charter and Bylaws/1.01 Certificate of Incorporation (2021-03-15).txt",
    f"CERTIFICATE OF INCORPORATION OF {CO.upper()}",
    "FIRST: The name of the corporation is Halcyon Robotics, Inc. (the \"Corporation\").",
    "FOURTH: The total number of shares of stock which the Corporation shall have authority to issue is 10,000,000 shares of Common Stock, par value $0.0001 per share.",
    "Filed with the Secretary of State of the State of Delaware on March 15, 2021.",
    "/s/ Dana Okafor, Incorporator")
doc("01 Charter and Bylaws/1.02 Certificate of Amendment to Certificate of Incorporation (2022-06-30).txt",
    f"CERTIFICATE OF AMENDMENT TO THE CERTIFICATE OF INCORPORATION OF {CO.upper()}",
    "Halcyon Robotics, Inc., a corporation organized and existing under the General Corporation Law of the State of Delaware, does hereby certify:",
    "FIRST: That Article FOURTH of the Certificate of Incorporation is hereby amended and restated in its entirety to read as follows: \"FOURTH: The total number of shares of stock which the Corporation shall have authority to issue is 15,000,000 shares of Common Stock, par value $0.0001 per share.\"",
    "SECOND: That the foregoing amendment was duly adopted in accordance with Section 242 of the General Corporation Law of the State of Delaware.",
    "IN WITNESS WHEREOF, the Corporation has caused this Certificate of Amendment to be executed by its duly authorized officer on June 30, 2022.",
    "By: /s/ Dana Okafor, Chief Executive Officer")
doc("01 Charter and Bylaws/1.03 Amended and Restated Certificate of Incorporation (2023-05-12).txt",
    f"AMENDED AND RESTATED CERTIFICATE OF INCORPORATION OF {CO.upper()}",
    "Halcyon Robotics, Inc., a corporation organized and existing under the laws of the State of Delaware, does hereby certify that: the original Certificate of Incorporation was filed with the Secretary of State on March 15, 2021, as amended by a Certificate of Amendment filed June 30, 2022; and this Amended and Restated Certificate of Incorporation, which restates and integrates and further amends the provisions of the Certificate of Incorporation, was duly adopted in accordance with Sections 242 and 245 of the General Corporation Law.",
    "FOURTH: The total number of shares of all classes of stock which the Corporation shall have authority to issue is 32,000,000 shares, consisting of 25,000,000 shares of Common Stock, par value $0.0001 per share, and 7,000,000 shares of Preferred Stock, par value $0.0001 per share, all of which are designated Series A Preferred Stock. The Series A Original Issue Price is $1.4286 per share.",
    "ARTICLE IV, Section 3.3 Protective Provisions. At any time when at least 1,000,000 shares of Preferred Stock are outstanding, the Corporation shall not, without the written consent of the holders of a majority of the outstanding Preferred Stock (the \"Requisite Holders\"), (a) liquidate, dissolve or wind up; (b) amend this Certificate of Incorporation in a manner adverse to the Preferred Stock; (c) create any senior or pari passu security; (d) incur indebtedness in excess of $2,000,000.",
    "This Amended and Restated Certificate of Incorporation shall be effective upon filing with the Secretary of State of the State of Delaware on May 12, 2023.",
    "By: /s/ Dana Okafor, Chief Executive Officer")
doc("01 Charter and Bylaws/1.04 Second Amended and Restated Certificate of Incorporation (2025-02-20).txt",
    f"SECOND AMENDED AND RESTATED CERTIFICATE OF INCORPORATION OF {CO.upper()}",
    "Halcyon Robotics, Inc. does hereby certify that: the original Certificate of Incorporation was filed on March 15, 2021 and was amended and restated on May 12, 2023 (the \"Prior Charter\"); and this Second Amended and Restated Certificate of Incorporation restates and integrates and further amends the Prior Charter and was duly adopted in accordance with Sections 242 and 245 of the General Corporation Law.",
    "FOURTH: The total number of shares of all classes of stock which the Corporation shall have authority to issue is 58,000,000 shares, consisting of 40,000,000 shares of Common Stock and 18,000,000 shares of Preferred Stock, of which 7,000,000 shares are designated Series A Preferred Stock and 11,000,000 shares are designated Series B Preferred Stock. The Series B Original Issue Price is $3.6364 per share.",
    "ARTICLE IV, Section 3.3 Protective Provisions. At any time when at least 2,000,000 shares of Preferred Stock are outstanding, the Corporation shall not, without the written consent of the holders of at least 60% of the outstanding Preferred Stock, voting together as a single class on an as-converted basis, which must include the holders of a majority of the Series B Preferred Stock (the \"Requisite Holders\"), (a) liquidate, dissolve or wind up; (b) amend this Certificate of Incorporation; (c) create any senior or pari passu security; (d) incur indebtedness in excess of $5,000,000; (e) increase the size of the Board above seven.",
    "Effective upon filing with the Secretary of State of the State of Delaware on February 20, 2025.",
    "By: /s/ Dana Okafor, Chief Executive Officer")
doc("01 Charter and Bylaws/1.05 Bylaws (2021-03-15).txt",
    f"BYLAWS OF {CO.upper()}", "Adopted March 15, 2021.",
    "Article III, Section 2. The number of directors shall be three.", "Article VIII. These Bylaws may be amended by the Board or the stockholders.")
doc("01 Charter and Bylaws/1.06 Amended and Restated Bylaws (2023-05-12).txt",
    f"AMENDED AND RESTATED BYLAWS OF {CO.upper()}", "Adopted and effective May 12, 2023. These Amended and Restated Bylaws amend and restate the Bylaws of the Corporation adopted March 15, 2021 in their entirety.",
    "Article III, Section 2. The number of directors shall be five.", "Article VIII. These Bylaws may be amended by the Board or the stockholders, subject to the Voting Agreement.")

# ---------------------------------------------------------------- 02 Seed
doc("02 Seed Financing (2022)/2.01 SAFE - Ridgecrest Ventures (2022-07-08).txt",
    f"{CO.upper()} — SAFE (Simple Agreement for Future Equity) — Post-Money Valuation Cap",
    "THIS CERTIFIES THAT in exchange for the payment by Ridgecrest Ventures LLC (the \"Investor\") of $1,000,000 (the \"Purchase Amount\") on or about July 8, 2022, Halcyon Robotics, Inc. (the \"Company\") issues to the Investor the right to certain shares of the Company's Capital Stock, subject to the terms described below. The Post-Money Valuation Cap is $12,000,000.",
    "1. Events. (a) Equity Financing. If there is an Equity Financing before the termination of this Safe, on the initial closing of such Equity Financing, this Safe will automatically convert into the greater of (1) the number of shares of Standard Preferred Stock equal to the Purchase Amount divided by the lowest price per share of the Standard Preferred Stock; or (2) the number of shares of Safe Preferred Stock equal to the Purchase Amount divided by the Safe Price.",
    "5. Termination. This Safe will automatically terminate (without relieving the Company of any obligations arising from a prior breach of or non-compliance with this Safe) immediately following the earliest to occur of: (i) the issuance of Capital Stock to the Investor pursuant to the automatic conversion of this Safe under Section 1(a); or (ii) the payment, or setting aside for payment, of amounts due the Investor pursuant to Section 1(b) or Section 1(c).",
    signed("Ridgecrest Ventures LLC"))
doc("02 Seed Financing (2022)/2.02 SAFE - Meridian Angels (2022-07-08).txt",
    f"{CO.upper()} — SAFE (Simple Agreement for Future Equity) — Post-Money Valuation Cap",
    "THIS CERTIFIES THAT in exchange for the payment by Meridian Angels LP of $500,000 on or about July 8, 2022, the Company issues to the Investor the right to certain shares of Capital Stock. The Post-Money Valuation Cap is $12,000,000.",
    "5. Termination. This Safe will automatically terminate immediately following the issuance of Capital Stock to the Investor pursuant to the automatic conversion of this Safe under Section 1(a).",
    signed("Meridian Angels LP"))
doc("02 Seed Financing (2022)/2.03 Board Consent Approving SAFEs (2022-07-01).txt",
    f"ACTION BY UNANIMOUS WRITTEN CONSENT OF THE BOARD OF DIRECTORS OF {CO.upper()}",
    "The undersigned, being all of the members of the Board of Directors, hereby adopt the following resolutions by written consent as of July 1, 2022: RESOLVED, that the Company is authorized to issue Simple Agreements for Future Equity in an aggregate amount of up to $2,000,000 with a post-money valuation cap of $12,000,000.",
    "/s/ Dana Okafor    /s/ Priya Venkataraman    /s/ Tomasz Wrona")

# ---------------------------------------------------------------- 03 Series A
doc("03 Series A Financing (2023)/3.01 Series A Preferred Stock Purchase Agreement (2023-05-12).txt",
    f"SERIES A PREFERRED STOCK PURCHASE AGREEMENT",
    f"THIS SERIES A PREFERRED STOCK PURCHASE AGREEMENT (this \"Agreement\") is made as of May 12, 2023 by and among {CO} (the \"Company\") and the investors listed on Exhibit A (the \"Purchasers\"), led by Cobalt Growth Partners II, L.P.",
    "1.1 Sale and Issuance of Series A Preferred Stock. The Company shall sell and the Purchasers shall purchase an aggregate of 5,600,000 shares of Series A Preferred Stock at a purchase price of $1.4286 per share, for aggregate proceeds of $8,000,000. The SAFEs issued in July 2022 shall convert into Series A Preferred Stock at the Initial Closing in accordance with their terms.",
    "2. Representations and Warranties of the Company. The Company hereby represents and warrants to each Purchaser that, except as set forth on the Disclosure Schedule, the statements in this Section 2 are true and correct as of the date of the Initial Closing.",
    "5.1 Conditions to Closing. Each of the Investors' Rights Agreement, the Right of First Refusal and Co-Sale Agreement and the Voting Agreement shall have been executed and delivered by the parties thereto, and the Restated Certificate shall have been filed with the Secretary of State of the State of Delaware.",
    BOILER["entire"], BOILER["law"], BOILER["counterparts"], signed("Cobalt Growth Partners II, L.P.", "Ridgecrest Ventures LLC"))
doc("03 Series A Financing (2023)/3.02 Investors' Rights Agreement (2023-05-12).txt",
    "INVESTORS' RIGHTS AGREEMENT",
    f"THIS INVESTORS' RIGHTS AGREEMENT (this \"Agreement\") is made and entered into as of May 12, 2023, by and among {CO} (the \"Company\"), each of the investors listed on Schedule A (the \"Investors\") and the holders of Common Stock listed on Schedule B (the \"Key Holders\").",
    "RECITALS. WHEREAS, the Investors are parties to that certain Series A Preferred Stock Purchase Agreement of even date herewith (the \"Purchase Agreement\"), and it is a condition to the closing thereunder that the parties enter into this Agreement.",
    "2.1 Demand Registration. If at any time after the earlier of (i) five years after the date of this Agreement or (ii) 180 days after the effective date of the registration statement for the IPO, the Company receives a request from Holders of at least 40% of the Registrable Securities then outstanding, the Company shall file a Form S-1 registration statement.",
    "3.1 Delivery of Financial Statements. The Company shall deliver to each Major Investor (a holder of at least 500,000 shares of Registrable Securities) annual audited financial statements within 120 days after year end and quarterly unaudited statements within 45 days after quarter end.",
    "4.1 Right of First Offer. Subject to the terms of this Section 4, the Company hereby grants to each Major Investor a right of first offer with respect to future sales by the Company of its Shares.",
    "6.6 Amendments and Waivers. This Agreement may be amended, modified or terminated, and the observance of any term may be waived, only with the written consent of the Company and the holders of at least a majority of the Registrable Securities then outstanding.",
    "6.13 Termination. The rights under Section 2 shall terminate upon a Deemed Liquidation Event or five years after the IPO. The covenants in Section 3 shall terminate upon the IPO.",
    BOILER["entire"], BOILER["law"], BOILER["counterparts"], signed("Cobalt Growth Partners II, L.P.", "Ridgecrest Ventures LLC", "Meridian Angels LP"))
doc("03 Series A Financing (2023)/3.03 Right of First Refusal and Co-Sale Agreement (2023-05-12).txt",
    "RIGHT OF FIRST REFUSAL AND CO-SALE AGREEMENT",
    f"THIS RIGHT OF FIRST REFUSAL AND CO-SALE AGREEMENT (this \"Agreement\") is made as of May 12, 2023, by and among {CO}, the Investors listed on Schedule A and the Key Holders listed on Schedule B.",
    "2.1 Right of First Refusal. Each Key Holder hereby unconditionally and irrevocably grants to the Company a Right of First Refusal to purchase all or any portion of Transfer Stock that such Key Holder may propose to transfer, and to the Investors a Secondary Refusal Right.",
    "6.8 Amendment. This Agreement may be amended only with the written consent of the Company, the Key Holders holding a majority of the Common Stock held by all Key Holders, and Investors holding a majority of the Preferred Stock held by all Investors.",
    BOILER["law"], BOILER["counterparts"], signed("Cobalt Growth Partners II, L.P.", "Ridgecrest Ventures LLC"))
doc("03 Series A Financing (2023)/3.04 Voting Agreement (2023-05-12).txt",
    "VOTING AGREEMENT",
    f"THIS VOTING AGREEMENT (this \"Agreement\") is made and entered into as of May 12, 2023, by and among {CO}, the Investors listed on Schedule A and the Key Holders listed on Schedule B.",
    "1.2 Board Composition. Each Stockholder agrees to vote all Shares so as to elect: (a) one director designated by Cobalt Growth Partners II, L.P. (the \"Series A Director\"); (b) two directors designated by the Key Holders holding a majority of the Common Stock, one of whom shall be the then-serving Chief Executive Officer; (c) one director designated by Ridgecrest Ventures LLC; and (d) one independent director mutually acceptable to the other directors. The size of the Board shall be five.",
    "3. Drag-Along Right. Each Stockholder agrees that if the Board, the holders of a majority of the Preferred Stock and the holders of a majority of the Common Stock held by Key Holders approve a Sale of the Company, each Stockholder shall vote for and raise no objections to such Sale.",
    "7.8 Amendment. This Agreement may be amended only by a written instrument executed by the Company, the Key Holders holding a majority of the Common Stock held by Key Holders, and Investors holding a majority of the Preferred Stock.",
    BOILER["law"], BOILER["counterparts"], signed("Cobalt Growth Partners II, L.P.", "Ridgecrest Ventures LLC"))
doc("03 Series A Financing (2023)/3.05 Stockholder Consent Approving Series A (2023-05-10).txt",
    f"ACTION BY WRITTEN CONSENT OF THE STOCKHOLDERS OF {CO.upper()}",
    "The undersigned stockholders, holding a majority of the outstanding Common Stock, hereby consent as of May 10, 2023 to the adoption of the Amended and Restated Certificate of Incorporation and the Series A financing on the terms presented.",
    "/s/ Dana Okafor    /s/ Priya Venkataraman")
doc("03 Series A Financing (2023)/3.06 Amendment No. 1 to Voting Agreement (2024-03-04).txt",
    "AMENDMENT NO. 1 TO VOTING AGREEMENT",
    f"THIS AMENDMENT NO. 1 (this \"Amendment\") to that certain Voting Agreement dated as of May 12, 2023 (the \"Voting Agreement\"), by and among {CO} and the other parties thereto, is made as of March 4, 2024.",
    "1. Amendment of Section 1.2. Section 1.2(c) of the Voting Agreement is hereby amended and restated in its entirety to read: \"(c) one director designated by Ridgecrest Ventures LLC, provided that such right shall terminate at such time as Ridgecrest Ventures LLC holds fewer than 350,000 shares of Preferred Stock.\"",
    "2. Effect of Amendment. Except as expressly amended hereby, the Voting Agreement shall remain in full force and effect. This Amendment and the Voting Agreement shall be read together as one instrument.",
    BOILER["counterparts"], signed("Cobalt Growth Partners II, L.P.", "Ridgecrest Ventures LLC"))
# a Series B document filed in the Series A folder (misfiled)
doc("03 Series A Financing (2023)/3.07 Amended and Restated Right of First Refusal and Co-Sale Agreement (2025-02-20).txt",
    "AMENDED AND RESTATED RIGHT OF FIRST REFUSAL AND CO-SALE AGREEMENT",
    f"THIS AMENDED AND RESTATED RIGHT OF FIRST REFUSAL AND CO-SALE AGREEMENT (this \"Agreement\") is made as of February 20, 2025, by and among {CO}, the Investors listed on Schedule A and the Key Holders listed on Schedule B.",
    "RECITALS. WHEREAS, the Company, certain of the Investors and the Key Holders are parties to that certain Right of First Refusal and Co-Sale Agreement dated as of May 12, 2023 (the \"Prior Agreement\"); and WHEREAS, the parties desire to amend and restate the Prior Agreement in its entirety as set forth herein, and this Agreement shall supersede the Prior Agreement in its entirety.",
    "2.1 Right of First Refusal. Each Key Holder grants to the Company a Right of First Refusal, and to the Investors a Secondary Refusal Right, with respect to Transfer Stock. Transfers of up to 10% of a Key Holder's holdings per year to a bona fide secondary purchaser approved by the Board are Exempted Transfers.",
    BOILER["law"], BOILER["counterparts"], signed("Cobalt Growth Partners II, L.P.", "Northwind Capital Fund IV, L.P.", "Ridgecrest Ventures LLC"))

# ---------------------------------------------------------------- 04 Series B
doc("04 Series B Financing (2025)/4.01 Series B Preferred Stock Purchase Agreement (2025-02-20).txt",
    "SERIES B PREFERRED STOCK PURCHASE AGREEMENT",
    f"THIS SERIES B PREFERRED STOCK PURCHASE AGREEMENT (this \"Agreement\") is made as of February 20, 2025 by and among {CO} and the Purchasers listed on Exhibit A, led by Northwind Capital Fund IV, L.P.",
    "1.1 Sale and Issuance. The Company shall sell an aggregate of 8,250,000 shares of Series B Preferred Stock at $3.6364 per share, for aggregate proceeds of $30,000,000, at the Initial Closing, and up to 2,750,000 additional shares at one or more Additional Closings within 90 days.",
    "5.1 Conditions to Closing. The Amended and Restated Investors' Rights Agreement, the Amended and Restated Right of First Refusal and Co-Sale Agreement and the Amended and Restated Voting Agreement shall have been executed, and the Second Amended and Restated Certificate of Incorporation shall have been filed.",
    BOILER["entire"], BOILER["law"], BOILER["counterparts"], signed("Northwind Capital Fund IV, L.P.", "Cobalt Growth Partners II, L.P."))
doc("04 Series B Financing (2025)/4.02 Amended and Restated Investors' Rights Agreement (2025-02-20).txt",
    "AMENDED AND RESTATED INVESTORS' RIGHTS AGREEMENT",
    f"THIS AMENDED AND RESTATED INVESTORS' RIGHTS AGREEMENT (this \"Agreement\") is made and entered into as of February 20, 2025, by and among {CO}, the Investors listed on Schedule A and the Key Holders listed on Schedule B.",
    "RECITALS. WHEREAS, the Company, certain of the Investors and the Key Holders are parties to that certain Investors' Rights Agreement dated as of May 12, 2023 (the \"Prior Agreement\"); WHEREAS, the Prior Agreement may be amended with the consent of the Company and the holders of a majority of the Registrable Securities, and the undersigned constitute such holders; and WHEREAS, the parties desire to amend and restate the Prior Agreement in its entirety, and this Agreement amends, restates and supersedes the Prior Agreement in its entirety.",
    "2.1 Demand Registration. If at any time after the earlier of (i) four years after the date of this Agreement or (ii) 180 days after the IPO, Holders of at least 30% of the Registrable Securities request registration, the Company shall file a Form S-1.",
    "3.1 Delivery of Financial Statements. Major Investor means a holder of at least 1,000,000 shares of Registrable Securities. Annual audited statements within 90 days; quarterly within 45 days; an annual budget 30 days before year end.",
    "4.1 Right of First Offer. The Company grants each Major Investor a right of first offer on New Securities, with a pro rata share based on Preferred Stock held, and an over-allotment right.",
    "6.6 Amendments and Waivers. This Agreement may be amended only with the written consent of the Company and the holders of at least 60% of the Registrable Securities then outstanding, which must include Northwind Capital Fund IV, L.P. for so long as it holds at least 2,000,000 shares.",
    BOILER["entire"], BOILER["law"], BOILER["counterparts"], signed("Northwind Capital Fund IV, L.P.", "Cobalt Growth Partners II, L.P.", "Ridgecrest Ventures LLC"))
doc("04 Series B Financing (2025)/4.03 Amended and Restated Voting Agreement (2025-02-20).txt",
    "AMENDED AND RESTATED VOTING AGREEMENT",
    f"THIS AMENDED AND RESTATED VOTING AGREEMENT (this \"Agreement\") is made as of February 20, 2025, by and among {CO}, the Investors and the Key Holders.",
    "RECITALS. WHEREAS, the parties are parties to that certain Voting Agreement dated as of May 12, 2023, as amended by Amendment No. 1 thereto dated as of March 4, 2024 (as so amended, the \"Prior Agreement\"); and WHEREAS, the parties desire to amend and restate the Prior Agreement in its entirety as set forth herein.",
    "1.2 Board Composition. The size of the Board shall be seven: (a) one Series A Director designated by Cobalt Growth Partners II, L.P.; (b) one Series B Director designated by Northwind Capital Fund IV, L.P.; (c) two Key Holder directors, one of whom shall be the CEO; (d) one director designated by Ridgecrest Ventures LLC for so long as it holds at least 350,000 shares of Preferred Stock; and (e) two independent directors.",
    "3. Drag-Along Right. A Sale of the Company approved by the Board, the holders of at least 60% of the Preferred Stock (including a majority of the Series B Preferred Stock) and the Key Holders holding a majority of the Common Stock held by Key Holders shall bind all Stockholders.",
    BOILER["law"], BOILER["counterparts"], signed("Northwind Capital Fund IV, L.P.", "Cobalt Growth Partners II, L.P.", "Ridgecrest Ventures LLC"))
doc("04 Series B Financing (2025)/4.04 Side Letter - Northwind Capital (2025-02-20).txt",
    "SIDE LETTER",
    f"February 20, 2025. Northwind Capital Fund IV, L.P. Re: Series B Preferred Stock financing of {CO}. In connection with the Amended and Restated Investors' Rights Agreement of even date herewith (the \"IRA\"), the Company agrees with Northwind as follows: (1) Notwithstanding Section 3.1 of the IRA, the Company shall deliver monthly management accounts to Northwind within 20 days after month end. (2) Northwind shall have the right to designate one non-voting observer to the Board. (3) This letter shall terminate when Northwind holds fewer than 1,000,000 shares of Preferred Stock. This letter does not amend the IRA as to any other party.",
    signed("Northwind Capital Fund IV, L.P."))
doc("04 Series B Financing (2025)/4.05 Management Rights Letter - Northwind Capital (2025-02-20).txt",
    "MANAGEMENT RIGHTS LETTER",
    f"February 20, 2025. This letter will confirm our agreement that pursuant to and effective as of your purchase of Series B Preferred Stock of {CO}, Northwind Capital Fund IV, L.P. shall be entitled to consult with and advise management on significant business issues and to examine the books and records of the Company. These rights shall terminate upon the IPO or a Deemed Liquidation Event.",
    signed())
doc("04 Series B Financing (2025)/4.06 Amendment No. 1 to Amended and Restated Investors' Rights Agreement (2026-01-15).txt",
    "AMENDMENT NO. 1 TO AMENDED AND RESTATED INVESTORS' RIGHTS AGREEMENT",
    f"THIS AMENDMENT NO. 1 (this \"Amendment\") to that certain Amended and Restated Investors' Rights Agreement dated as of February 20, 2025 (the \"IRA\"), by and among {CO} and the other parties thereto, is made as of January 15, 2026.",
    "1. Amendment of Section 3.1. Section 3.1 of the IRA is hereby amended to replace \"within 90 days\" with \"within 120 days\".",
    "2. Amendment of Section 4.1. Section 4.1 of the IRA is hereby amended to add at the end: \"The right of first offer shall not apply to the issuance of up to 1,500,000 shares of Common Stock under the 2021 Stock Plan, as amended.\"",
    "3. Effect. Except as expressly amended hereby, the IRA remains in full force and effect and is hereby ratified and confirmed.",
    BOILER["counterparts"], signed("Northwind Capital Fund IV, L.P.", "Cobalt Growth Partners II, L.P."))
doc("04 Series B Financing (2025)/4.07 Second Amended and Restated Investors' Rights Agreement (DRAFT 2026-08-01).txt",
    "SECOND AMENDED AND RESTATED INVESTORS' RIGHTS AGREEMENT",
    "DRAFT — FOR DISCUSSION PURPOSES ONLY — August 1, 2026",
    f"THIS SECOND AMENDED AND RESTATED INVESTORS' RIGHTS AGREEMENT (this \"Agreement\") is made and entered into as of [●], 2026, by and among {CO}, the Investors listed on Schedule A and the Key Holders listed on Schedule B.",
    "RECITALS. WHEREAS, the parties are parties to that certain Amended and Restated Investors' Rights Agreement dated as of February 20, 2025, as amended by Amendment No. 1 thereto dated as of January 15, 2026 (the \"Prior Agreement\"); and WHEREAS, in connection with the proposed Series C financing, the parties desire to amend and restate the Prior Agreement in its entirety.",
    "2.1 Demand Registration. [Series C terms to come.]",
    unsigned("Northwind Capital Fund IV, L.P.", "[SERIES C LEAD]"))

# ---------------------------------------------------------------- 05 Equity plan
doc("05 Equity Compensation/5.01 2021 Stock Plan (2021-04-01).txt",
    f"{CO.upper()} 2021 STOCK PLAN", "Adopted by the Board on April 1, 2021; approved by the stockholders on April 1, 2021.",
    "3. Shares Subject to the Plan. Subject to adjustment, the maximum aggregate number of Shares that may be issued under the Plan is 1,500,000 Shares.",
    "14. Amendment and Termination. The Board may at any time amend, alter, suspend or terminate the Plan, subject to stockholder approval where required.")
doc("05 Equity Compensation/5.02 Amendment No. 1 to 2021 Stock Plan (2023-05-12).txt",
    f"AMENDMENT NO. 1 TO THE {CO.upper()} 2021 STOCK PLAN",
    "Effective May 12, 2023, Section 3 of the 2021 Stock Plan is amended to increase the maximum aggregate number of Shares issuable under the Plan from 1,500,000 to 3,200,000 Shares. Except as set forth herein, the Plan remains in full force and effect. Approved by the Board on May 1, 2023 and the stockholders on May 10, 2023.")
doc("05 Equity Compensation/5.03 Amendment No. 2 to 2021 Stock Plan (2025-02-20).txt",
    f"AMENDMENT NO. 2 TO THE {CO.upper()} 2021 STOCK PLAN",
    "Effective February 20, 2025, Section 3 of the 2021 Stock Plan, as amended, is further amended to increase the maximum aggregate number of Shares issuable under the Plan to 6,000,000 Shares. Except as set forth herein, the Plan, as previously amended, remains in full force and effect.")

for rel, text in FILES.items():
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
print(f"wrote {len(FILES)} files under {root}")
