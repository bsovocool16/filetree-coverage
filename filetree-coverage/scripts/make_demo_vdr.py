#!/usr/bin/env python3
"""
Builds a small fictional data room ("Project Lantern" — the sale of Meridian
Coatings, Inc., an invented Ohio industrial-coatings manufacturer) so the
coverage pipeline and viewer can be exercised without real client documents.

Everything here is invented. Run:  python make_demo_vdr.py ./demo_vdr
"""
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "demo_vdr")

BOILER = {
    "recitals": "WHEREAS, Meridian Coatings, Inc., a Delaware corporation with its principal place of business at 4400 Needmore Road, Dayton, Ohio 45424 (the \"Company\"), and the counterparty named above wish to set out the terms on which they will do business; NOW, THEREFORE, in consideration of the mutual covenants set out below, the parties agree as follows.",
    "law": "This Agreement is governed by the laws of the State of Ohio without regard to its conflict-of-laws rules. The parties submit to the exclusive jurisdiction of the state and federal courts sitting in Montgomery County, Ohio.",
    "notices": "Notices must be in writing and delivered by hand, by nationally recognized overnight courier, or by email with confirmation of receipt, to the addresses set out on the signature page, and are effective on receipt.",
    "counterparts": "This Agreement may be executed in counterparts, each of which is an original and all of which together constitute one instrument. Signatures delivered by PDF or electronic signature service are effective as originals.",
    "entire": "This Agreement, together with its schedules and exhibits, is the entire agreement of the parties on its subject matter and supersedes all prior discussions. It may be amended only by a writing signed by both parties.",
    "confidentiality": "Each party will keep the other's Confidential Information in confidence, use it only to perform this Agreement, and disclose it only to personnel and advisers who need to know it and are bound by written obligations no less protective than these.",
    "force": "Neither party is liable for failure to perform (other than payment obligations) caused by events beyond its reasonable control, including fire, flood, epidemic, labor disputes not involving its own employees, and acts of governmental authority, provided it gives prompt notice and uses reasonable efforts to resume performance.",
    "insurance": "The Company maintains commercial general liability insurance of not less than $2,000,000 per occurrence and $5,000,000 in the aggregate, and will furnish certificates of insurance on request.",
}

FILES = {}


def doc(path, title, *paras, boiler=("recitals", "confidentiality", "law", "notices", "counterparts", "entire")):
    body = [title.upper(), ""]
    body += [p for p in paras]
    body += [BOILER[b] for b in boiler]
    FILES[path] = "\n\n".join(body)


# ---------------------------------------------------------------- 01 Corporate
doc("01 Corporate/1.01 Certificate of Incorporation.txt", "Amended and Restated Certificate of Incorporation of Meridian Coatings, Inc.",
    "The name of the corporation is Meridian Coatings, Inc. The corporation was originally incorporated in Delaware on March 3, 1998 under the name Miami Valley Protective Coatings, Inc.",
    "The total number of shares of stock the corporation is authorized to issue is 12,000,000 shares of Common Stock, par value $0.001 per share, and 3,000,000 shares of Series A Preferred Stock, par value $0.001 per share.",
    "The corporation shall indemnify its directors and officers to the fullest extent permitted by the Delaware General Corporation Law.",
    boiler=("counterparts",))
doc("01 Corporate/1.02 Bylaws.txt", "Amended and Restated Bylaws of Meridian Coatings, Inc. (adopted June 14, 2021)",
    "The Board of Directors consists of seven directors. Directors are elected annually at the annual meeting of stockholders. A majority of the whole Board constitutes a quorum.",
    "Special meetings of stockholders may be called by the Chair, the Chief Executive Officer, or holders of at least 25% of the outstanding voting stock.",
    "Any merger, consolidation, or sale of all or substantially all of the assets of the corporation requires approval of a majority of the whole Board and the affirmative vote of holders of a majority of the outstanding Common Stock and Series A Preferred Stock, voting together as a single class.",
    boiler=())
doc("01 Corporate/1.03 Stockholders Agreement.txt", "Stockholders Agreement dated as of September 30, 2019",
    "The Stockholders Agreement is among the Company, Vance Family Holdings LLC, Greenlake Growth Partners III, L.P., and the management holders listed on Schedule A.",
    "Drag-along. If holders of at least 60% of the outstanding shares (which must include Greenlake) approve a Sale of the Company, all other holders must vote for, consent to, and raise no objection to the transaction and, if structured as a stock sale, sell their shares on the same terms.",
    "Right of first refusal and co-sale. Transfers by any holder other than to Permitted Transferees are subject to a right of first refusal in favor of the Company and then the other holders, and to a co-sale right in favor of Greenlake.",
    "Board composition. Greenlake is entitled to designate two directors and Vance Family Holdings two directors for so long as each holds at least 10% of the outstanding shares.",
    boiler=("law", "notices", "counterparts", "entire"))
doc("01 Corporate/1.04 Board Minutes 2023.txt", "Minutes of Meetings of the Board of Directors — 2023",
    "February 21, 2023. The Board reviewed FY2022 results. Revenue of $148.2 million, EBITDA of $19.4 million. The Board approved the FY2023 budget and the capital plan for the Toledo line 4 expansion ($6.1 million).",
    "May 16, 2023. Management reported on the Ohio EPA inspection of the Dayton facility and stated that a written response to the inspector's observations had been submitted. Counsel briefed the Board on the Dorsey product liability claim and the status of the insurer's reservation of rights.",
    "September 12, 2023. The Board approved the amendment to the First Meridian Bank credit agreement extending the maturity to September 2027 and the increase of the revolving commitment to $35 million.",
    "November 28, 2023. The Board discussed strategic alternatives and authorized management to engage Harlow Partners as financial adviser.",
    boiler=())
doc("01 Corporate/1.05 Board Minutes 2024.txt", "Minutes of Meetings of the Board of Directors — 2024",
    "March 5, 2024. The Board reviewed FY2023 audited results and the auditor's management letter. Management summarized the Notice of Violation received from Ohio EPA in January 2024 relating to volatile organic compound recordkeeping at Dayton and the corrective action plan.",
    "June 18, 2024. Counsel reported on the demand letter from the Tri-County Water District concerning alleged discharges from the Toledo facility. The Board directed management to notify the pollution legal liability carrier.",
    "August 20, 2024. The Board approved retention bonus arrangements for eight key employees in connection with the strategic process (see Retention Bonus Letters).",
    "December 10, 2024. The Board approved the FY2025 budget and ratified the renewal of the Halvorsen Marine master supply agreement through 2028.",
    boiler=())
doc("01 Corporate/1.06 Capitalization Table.txt", "Capitalization Table as of June 30, 2025",
    "Common Stock outstanding: 8,412,500 shares. Series A Preferred outstanding: 2,400,000 shares (convertible 1:1). Options outstanding under the 2019 Equity Incentive Plan: 611,000, weighted average exercise price $4.18. Warrants: 60,000 held by First Meridian Bank, exercise price $6.00.",
    "Holders: Vance Family Holdings LLC 41.2% (fully diluted), Greenlake Growth Partners III, L.P. 30.9%, management and employees 22.4%, other 5.5%.",
    boiler=())
doc("01 Corporate/1.07 Subsidiary Organization Chart.txt", "Organization Chart",
    "Meridian Coatings, Inc. (Delaware) owns 100% of Meridian Coatings Europe GmbH (Germany, sales office, 4 employees), 100% of MC Toledo Realty LLC (Ohio, holds the Toledo facility), and 100% of Meridian Coatings de Mexico S. de R.L. de C.V. (dormant since 2022).",
    boiler=())

# ---------------------------------------------------------------- 02 Financial
doc("02 Financial/2.01 Audited Financial Statements FY2023.txt", "Meridian Coatings, Inc. — Consolidated Financial Statements, Year Ended December 31, 2023 (Audited)",
    "Independent auditor's report: unqualified opinion, Whitcomb & Ashe LLP, dated March 1, 2024.",
    "Revenue $152.7 million (2022: $148.2 million). Gross margin 31.4%. Net income $8.9 million. Total debt $41.3 million under the First Meridian Bank credit agreement and the Cascade equipment lease.",
    "Note 12 — Commitments and contingencies. The Company is a defendant in a product liability action (Dorsey) and has received a Notice of Violation from Ohio EPA. Management believes a loss is reasonably possible but not estimable. An accrual of $0.4 million has been recorded for environmental remediation at the Toledo facility.",
    "Note 14 — Related party transactions. The Company leases its Columbus warehouse from an entity controlled by the Vance family at $312,000 per year.",
    boiler=())
doc("02 Financial/2.02 Audited Financial Statements FY2024.txt", "Meridian Coatings, Inc. — Consolidated Financial Statements, Year Ended December 31, 2024 (Audited)",
    "Independent auditor's report: unqualified opinion, Whitcomb & Ashe LLP, dated March 7, 2025.",
    "Revenue $161.9 million. Gross margin 32.8%. Net income $10.6 million. Total debt $38.0 million.",
    "Note 12 — Commitments and contingencies. Dorsey v. Meridian remains pending; trial is set for November 2025. The Tri-County Water District has asserted claims relating to alleged stormwater discharges; no suit has been filed. The environmental accrual was increased to $1.1 million.",
    "Note 15 — Subsequent events. In February 2025 the Company received a sales tax assessment from the Ohio Department of Taxation of $0.62 million, which it is contesting.",
    boiler=())
doc("02 Financial/2.03 Management Accounts H1 2025.txt", "Monthly Management Accounts, January–June 2025",
    "Year-to-date revenue $84.1 million, 6.3% ahead of budget, driven by marine and infrastructure coatings. EBITDA $11.9 million. Capital expenditure $2.7 million. Net debt $33.4 million at June 30, 2025.",
    "Top customers YTD: Halvorsen Marine 18.4%, Ridgeline Automotive 11.2%, Port of Tacoma Authority 7.9%, Nordwind GmbH (distributor) 6.1%.",
    boiler=())
doc("02 Financial/2.04 Budget FY2026.txt", "FY2026 Budget and Three-Year Plan",
    "Revenue $174 million; EBITDA $24 million. Assumes renewal of the Kestrel Chemicals resin supply agreement at current pricing and no loss of the Ridgeline Automotive account.",
    "Capital plan: $4.5 million for a regenerative thermal oxidizer at Dayton to address VOC emissions and the requirements of the Ohio EPA corrective action plan.",
    boiler=())
doc("02 Financial/2.05 Auditor Management Letter 2024.txt", "Whitcomb & Ashe LLP — Management Letter, FY2024 Audit",
    "Observations: (1) Inventory count variances at Toledo of 2.1% of inventory value; (2) revenue cut-off errors at year end totaling $0.3 million, corrected; (3) the Company's environmental accrual methodology relies on a single consultant estimate and should be refreshed following the Phase I assessment.",
    boiler=())

# ---------------------------------------------------------------- 03 Material Contracts
doc("03 Material Contracts/3.1 Customer Agreements/3.1.01 Master Supply Agreement - Halvorsen Marine.txt", "Master Supply Agreement between Meridian Coatings, Inc. and Halvorsen Marine A/S, dated January 1, 2020, as amended",
    "Term. The initial term runs through December 31, 2025, renewed by Amendment No. 1 through December 31, 2028. Halvorsen commits to purchase not less than 70% of its annual requirements for anti-corrosive hull and deck coatings from the Company.",
    "Pricing. Prices are fixed annually with a raw-material index adjustment tied to epoxy resin prices; the Company bears the first 3% of any increase.",
    "Assignment; change of control. Neither party may assign this Agreement without the other's prior written consent. For this purpose, a change of control of the Company, meaning any transaction or series of transactions by which any person or group acquires more than 50% of the voting power of the Company or all or substantially all of its assets, is deemed an assignment requiring Halvorsen's consent, which Halvorsen may withhold in its sole discretion.",
    "Termination. Either party may terminate for uncured material breach on 60 days' notice. Halvorsen may terminate on 180 days' notice if the Company's on-time delivery rate falls below 92% for two consecutive quarters.",
    "Note: Amendment No. 2 (executed May 2025) is filed separately as a scanned copy.")
doc("03 Material Contracts/3.1 Customer Agreements/3.1.02 Supply Agreement - Ridgeline Automotive.txt", "Supply Agreement between Meridian Coatings, Inc. and Ridgeline Automotive Systems LLC, dated April 15, 2022",
    "Products. E-coat primers and powder topcoats for Ridgeline's Marysville and Chattanooga plants, in accordance with Ridgeline Supplier Quality Manual rev. 7.",
    "Term. Three years from the effective date with automatic one-year renewals unless either party gives 120 days' notice of non-renewal. Ridgeline may terminate for convenience on 90 days' notice.",
    "Assignment. Neither party may assign, delegate, or otherwise transfer this Agreement or any of its rights or obligations, whether voluntarily, by merger, by operation of law, or otherwise, without the prior written consent of the other party, which consent may be withheld in its sole discretion. Any purported transfer in violation of this Section is void.",
    "Most favored customer. The Company warrants that prices to Ridgeline are no higher than prices charged to any other automotive customer for comparable products and volumes.")
doc("03 Material Contracts/3.1 Customer Agreements/3.1.03 Framework Agreement - Port of Tacoma Authority.txt", "Framework Agreement for Protective Coatings, Port of Tacoma Authority, Contract No. PTA-2021-0448",
    "Scope. Supply of marine-grade protective coatings and technical services for pier and crane structures under task orders issued through December 31, 2026.",
    "Change of control. The Authority may terminate this Agreement on 30 days' written notice if the Contractor undergoes a change of control, including any acquisition of a majority of its voting stock, without the Authority's prior written approval. The Contractor must notify the Authority in writing at least 60 days before any such change of control.",
    "Public records. Documents submitted to the Authority are subject to the Washington Public Records Act.",
    "Prevailing wage and Buy American requirements apply to task orders funded with federal grant money.",
    boiler=("law", "notices", "counterparts", "entire"))
doc("03 Material Contracts/3.1 Customer Agreements/3.1.04 Standard Terms and Conditions of Sale.txt", "Meridian Coatings, Inc. — Standard Terms and Conditions of Sale (rev. 2023)",
    "These terms apply to all purchase orders not governed by a separate written agreement. Warranty: products conform to published specifications for 12 months from shipment; the exclusive remedy is replacement or refund. Limitation of liability: no consequential damages; aggregate liability capped at the price paid.",
    boiler=("law",))
doc("03 Material Contracts/3.2 Supplier Agreements/3.2.01 Resin Supply Agreement - Kestrel Chemicals.txt", "Resin Supply Agreement between Kestrel Chemicals Corporation and Meridian Coatings, Inc., dated July 1, 2021",
    "Exclusivity. The Company will purchase 100% of its requirements for bisphenol-A epoxy resin from Kestrel for the term. Kestrel grants the Company most-favored-nation pricing among Kestrel's coatings customers in North America.",
    "Term. Through June 30, 2026, with one three-year renewal at the Company's option on 12 months' notice.",
    "Assignment. This Agreement may not be assigned by either party without the consent of the other, not to be unreasonably withheld, except that either party may assign to an affiliate or to a successor to all or substantially all of its business without consent.")
doc("03 Material Contracts/3.2 Supplier Agreements/3.2.02 Pigment Supply Agreement - Aurelius Minerals.txt", "Pigment Supply Agreement between Aurelius Minerals Ltd. and Meridian Coatings, Inc., dated February 2, 2023",
    "Supply of titanium dioxide and iron oxide pigments on a take-or-pay basis: minimum 1,800 metric tons per year. Shortfall payment equals 40% of the contract price of the shortfall quantity.",
    "Term through December 31, 2027. Freely assignable to affiliates; otherwise consent required, not to be unreasonably withheld.")
doc("03 Material Contracts/3.2 Supplier Agreements/3.2.03 Toll Manufacturing Agreement - Bexley Industries.txt", "Toll Manufacturing Agreement between Meridian Coatings, Inc. and Bexley Industries, Inc., dated October 1, 2020",
    "Bexley manufactures waterborne architectural coatings for the Company at its Zanesville facility using Company formulations and trade secrets. Minimum annual volume 500,000 gallons.",
    "Change of control. If the Company undergoes a change of control in favor of a competitor of Bexley (as listed on Schedule 4), Bexley may terminate on 90 days' notice. Any other change of control requires notice only.",
    "Technology. All formulations, process parameters, and improvements are the Company's Confidential Information and property. Bexley receives a limited, non-exclusive, non-transferable license solely to perform this Agreement.")
doc("03 Material Contracts/3.3 Distribution/3.3.01 Distribution Agreement - Nordwind GmbH.txt", "Exclusive Distribution Agreement between Meridian Coatings, Inc. and Nordwind Beschichtungen GmbH, dated March 1, 2019",
    "Territory. Exclusive distributor for Germany, Austria, Switzerland, and the Benelux countries for marine and industrial coatings.",
    "Non-compete. During the term and for two years thereafter, the Company will not appoint another distributor or sell directly in the Territory, except to Halvorsen Marine.",
    "Change of control. Nordwind may terminate this Agreement, and will be entitled to a termination indemnity equal to one year's average gross margin on Nordwind's sales of Company products, if the Company is acquired by or merges with a person that distributes competing coatings in the Territory. Any other change of control of the Company requires 90 days' prior notice to Nordwind.",
    "Governing law: Germany; arbitration under the DIS Rules in Hamburg.",
    boiler=("confidentiality", "notices", "counterparts", "entire"))
doc("03 Material Contracts/3.3 Distribution/3.3.02 Sales Agency Agreement - Latam.txt", "Sales Agency Agreement between Meridian Coatings, Inc. and Comercial Andina S.A., dated August 1, 2021",
    "Non-exclusive commission agent for Chile, Peru, and Colombia. Commission 6% of net invoiced sales. Terminable by either party on 60 days' notice. Agent has no authority to bind the Company.",
    boiler=("law", "notices", "counterparts"))
doc("03 Material Contracts/3.4 Financing/3.4.01 Credit Agreement - First Meridian Bank.txt", "Amended and Restated Credit Agreement among Meridian Coatings, Inc., the Guarantors party thereto, and First Meridian Bank, N.A., dated September 15, 2023",
    "Facilities. $35,000,000 revolving credit facility and $20,000,000 term loan, maturing September 15, 2027. Interest at Term SOFR plus 2.75% to 3.50% based on leverage. Secured by a first-priority lien on substantially all assets and a mortgage on the Toledo facility.",
    "Financial covenants. Maximum total leverage 3.25x; minimum fixed charge coverage 1.20x, tested quarterly.",
    "Events of default include (i) nonpayment; (ii) covenant breach; (iii) cross-default to other indebtedness above $1,000,000; (iv) a Change of Control, defined as (a) any person or group (other than Vance Family Holdings LLC and Greenlake Growth Partners III, L.P.) acquiring beneficial ownership of more than 35% of the voting stock of the Borrower, (b) the Borrower ceasing to own 100% of any Guarantor, or (c) a majority of the Board ceasing to be Continuing Directors.",
    "Prepayment. The term loan may be prepaid without premium after September 15, 2025.",
    boiler=("law", "notices", "counterparts", "entire"))
doc("03 Material Contracts/3.4 Financing/3.4.02 Equipment Lease - Cascade Leasing.txt", "Master Equipment Lease Agreement between Cascade Leasing Corp. and Meridian Coatings, Inc., dated May 1, 2022",
    "Schedules 1 through 4 cover the Toledo line 4 application and curing equipment. Aggregate remaining rent $3.9 million through April 2029. Lessee may not assign or sublease without Lessor's consent. Change of control of Lessee is an Event of Default unless Lessor has consented in writing, such consent not to be unreasonably withheld if the successor's credit is at least equal to Lessee's.",
    boiler=("law", "notices", "counterparts"))
doc("03 Material Contracts/3.4 Financing/3.4.03 Intercreditor Agreement.txt", "Intercreditor Agreement between First Meridian Bank, N.A. and Cascade Leasing Corp., dated May 1, 2022",
    "Cascade's security interest in the leased equipment is senior; First Meridian's lien on all other assets is senior. Standstill of 90 days on Cascade enforcement following a First Meridian default notice.",
    boiler=("law", "notices", "counterparts"))

# ---------------------------------------------------------------- 04 IP
doc("04 Intellectual Property/4.01 Patent Schedule.txt", "Schedule of Patents and Applications",
    "US 10,842,117 — Low-VOC epoxy-siloxane hybrid coating, issued Nov 2020, expires 2038. US 11,306,442 — Self-stratifying anti-corrosive primer, issued Apr 2022. EP 3 512 880 — validated in DE, FR, GB, NL. Two pending US applications relating to bio-based curing agents (filed 2024).",
    "All patents are owned by Meridian Coatings, Inc. and recorded at the USPTO. A security interest in favor of First Meridian Bank is recorded against each.", boiler=())
doc("04 Intellectual Property/4.02 Trademark Schedule.txt", "Schedule of Trademarks",
    "MERIDIAN COATINGS (US Reg. 4,911,220), HULLSHIELD (US Reg. 5,204,118; EU 017 992 331), DURAPRIME (US Reg. 5,877,001). Domain names listed separately.", boiler=())
doc("04 Intellectual Property/4.03 License Agreement - University of Akron.txt", "Exclusive License Agreement between The University of Akron and Meridian Coatings, Inc., dated December 12, 2018",
    "License. Exclusive, worldwide, royalty-bearing license under UA patent family 2017-041 (siloxane-modified polymer) in the field of protective coatings for metal substrates. Running royalty 2.5% of net sales of licensed products; minimum annual royalty $150,000.",
    "Assignment. Licensee may not assign this Agreement except to a successor in connection with the transfer of all or substantially all of the business to which this Agreement relates, and only if the successor agrees in writing to be bound and the University receives notice within 30 days. The University may terminate if the Licensee becomes controlled by an entity that is not primarily engaged in the manufacture of coatings.",
    "Diligence. Licensee must maintain commercial sales of licensed products in each calendar year or the University may convert the license to non-exclusive.",
    boiler=("confidentiality", "law", "notices", "counterparts", "entire"))
doc("04 Intellectual Property/4.04 Invention Assignment Agreement Template.txt", "Employee Confidentiality and Invention Assignment Agreement (form)",
    "Employee assigns to the Company all inventions conceived during employment relating to the Company's business. Ohio Rev. Code 4113.? notice not required; California Labor Code 2870 notice included for California employees.",
    boiler=("law",))
doc("04 Intellectual Property/4.05 Domain Names.txt", "Domain Name Schedule",
    "meridiancoatings.com, hullshield.com, duraprime.net, meridiancoatings.de — all registered to the Company through Tucows; renewals current through 2027.", boiler=())

# ---------------------------------------------------------------- 05 Employment
doc("05 Employment/5.01 Employee Census.txt", "Employee Census as of June 30, 2025",
    "Total employees 412: Dayton 238 (of which 171 hourly, represented by IUE-CWA Local 412), Toledo 131, Columbus 19, Europe 4, remote 20. Average tenure 9.1 years. Eight employees on retention bonus arrangements.", boiler=())
doc("05 Employment/5.02 Employment Agreement - CEO.txt", "Amended and Restated Employment Agreement between Meridian Coatings, Inc. and Robert Vance, dated January 1, 2022",
    "Position: President and Chief Executive Officer. Base salary $485,000; target annual bonus 75% of base.",
    "Change in control. If, within 24 months following a Change in Control, the Executive's employment is terminated by the Company without Cause or by the Executive for Good Reason, the Executive will receive a lump sum equal to 2.0 times the sum of base salary and target bonus, 24 months of COBRA premiums, and full acceleration of all unvested equity awards. Good Reason includes a material diminution in duties or a relocation of more than 35 miles.",
    "Section 280G. Payments are cut back to the safe-harbor amount only if the cut-back produces a better after-tax result for the Executive.",
    "Restrictive covenants. Non-competition and non-solicitation for 18 months following termination in North America and Europe.",
    boiler=("confidentiality", "law", "notices", "counterparts", "entire"))
doc("05 Employment/5.03 Employment Agreement - CFO.txt", "Employment Agreement between Meridian Coatings, Inc. and Priya Natarajan, dated March 15, 2021",
    "Position: Chief Financial Officer. Base salary $310,000; target bonus 50%.",
    "Severance. On termination without Cause or resignation for Good Reason, 12 months' base salary continuation. If such termination occurs within 12 months after a Change in Control, severance is increased to 18 months of base salary plus target bonus, and unvested equity awards accelerate in full.",
    "Restrictive covenants. Non-competition for 12 months.",
    boiler=("confidentiality", "law", "notices", "counterparts", "entire"))
doc("05 Employment/5.04 Employee Handbook.txt", "Employee Handbook (rev. January 2024)",
    "At-will employment statement; equal employment opportunity; anti-harassment reporting procedure; paid time off accrual (hourly employees accrue 0.0577 hours per hour worked); safety rules for the Dayton and Toledo plants including respirator fit-testing and hazard communication training.", boiler=())
doc("05 Employment/5.05 2019 Equity Incentive Plan.txt", "Meridian Coatings, Inc. 2019 Equity Incentive Plan",
    "Share reserve: 1,200,000 shares. Awards: incentive and nonqualified stock options, restricted stock, and restricted stock units.",
    "Section 11 — Change in Control. Unless the successor assumes or substitutes outstanding awards, all awards vest in full immediately before the Change in Control. If awards are assumed, they vest in full upon a termination without Cause within 12 months after the Change in Control. The Administrator may cash out awards at the transaction price less the exercise price.",
    "A Change in Control means (a) a merger after which the Company's stockholders hold less than 50% of the voting power of the surviving entity, (b) a sale of all or substantially all assets, or (c) any person becoming the beneficial owner of more than 50% of the voting stock.",
    boiler=("law",))
doc("05 Employment/5.06 Collective Bargaining Agreement - Local 412.txt", "Collective Bargaining Agreement between Meridian Coatings, Inc. (Dayton Plant) and IUE-CWA Local 412, effective May 1, 2023 through April 30, 2027",
    "Recognition; union security; dues checkoff. Wage schedule with 3.0% increases on each May 1. Health insurance premium share 18% employee.",
    "Article 28 — Successors and assigns. This Agreement is binding on the successors and assigns of the Company. In the event of a sale, transfer, or merger of the Dayton Plant, the Company will give the Union at least 60 days' notice and will require the purchaser or transferee to assume this Agreement as a condition of the transaction.",
    "Article 30 — Plant closure. Severance of one week's pay per year of service in the event of a permanent closure of the Dayton Plant.",
    boiler=())
doc("05 Employment/5.07 Retention Bonus Letters.txt", "Retention Bonus Letters (August 2024)",
    "Eight letters, aggregate $1,240,000. Each bonus is payable 50% on the closing of a Sale Transaction and 50% on the six-month anniversary of closing, conditioned on continued employment. A Sale Transaction is defined by reference to the 2019 Equity Incentive Plan's definition of Change in Control.", boiler=())

# ---------------------------------------------------------------- 06 Litigation
doc("06 Litigation/6.01 Litigation Summary Schedule.txt", "Schedule of Pending and Threatened Litigation, Claims and Investigations (prepared by General Counsel, July 2025)",
    "1. Dorsey v. Meridian Coatings, Inc., Court of Common Pleas, Lucas County, Ohio, Case No. CI-2023-1187. Product liability / failure to warn (respiratory injury alleged from isocyanate exposure). Demand $4.5 million. Insurer (Hartwell Mutual) defending under reservation of rights. Trial November 2025.",
    "2. Tri-County Water District — demand letter dated May 28, 2024 alleging unpermitted stormwater discharges from the Toledo facility and demanding $2.3 million for remediation and monitoring. No suit filed. Pollution legal liability carrier notified.",
    "3. EEOC Charge No. 532-2024-01977 (Dayton) — alleged age discrimination in a 2024 reduction in force. Position statement filed; no determination.",
    "4. Ohio Department of Taxation sales and use tax assessment, $0.62 million, under petition for reassessment.",
    "5. Ohio EPA Notice of Violation (January 2024) — Dayton Title V permit recordkeeping. Corrective action plan accepted; penalty negotiations ongoing; agency's initial proposed penalty $187,500.",
    boiler=())
doc("06 Litigation/6.02 Complaint - Dorsey v. Meridian.txt", "Complaint and Jury Demand — Dorsey v. Meridian Coatings, Inc., Lucas County Court of Common Pleas",
    "Plaintiff Marcus Dorsey, a contract painter, alleges that he developed occupational asthma after applying the Company's DURAPRIME two-component polyurethane topcoat at a job site in 2021 and that the product's safety data sheet and label failed adequately to warn of isocyanate sensitization risk. Counts: strict liability (design and warning defect), negligence, breach of implied warranty. Damages sought in excess of $25,000 (Ohio pleading minimum); pre-suit demand $4.5 million.",
    boiler=())
doc("06 Litigation/6.03 Demand Letter - Tri-County Water District.txt", "Letter from counsel for Tri-County Water District to Meridian Coatings, Inc., dated May 28, 2024",
    "The District asserts that stormwater runoff from the Toledo facility's outdoor drum storage area has discharged solvent-contaminated water to the Ottawa River tributary in violation of the Clean Water Act and the facility's NPDES permit, and that the District has incurred sampling and treatment costs. The District demands $2.3 million and a remediation plan and threatens a citizen suit under CWA section 505 if no agreement is reached within 60 days.",
    "The letter attaches sampling results from March and April 2024 showing xylene and toluene above benchmark values at outfall 002.",
    boiler=())
doc("06 Litigation/6.04 Settlement Agreement - Former Distributor.txt", "Confidential Settlement Agreement and Mutual Release between Meridian Coatings, Inc. and Coastline Coatings Supply, Inc., dated August 9, 2022",
    "Resolves Coastline's claims for wrongful termination of its Gulf Coast distributorship. Company paid $425,000; mutual releases; two-year non-disparagement; Coastline may continue to sell existing inventory through December 2022.",
    boiler=("confidentiality", "law", "counterparts"))
doc("06 Litigation/6.05 EEOC Charge 2024.txt", "EEOC Charge of Discrimination No. 532-2024-01977 and Company Position Statement",
    "Charging party, age 58, was one of eleven employees separated in the March 2024 Dayton reduction in force. Alleges age discrimination under the ADEA. The Company's position statement describes the selection criteria (skills matrix and seniority within classification) and notes that six of the eleven separated employees were under 40.",
    boiler=())

# ---------------------------------------------------------------- 07 Real Estate
doc("07 Real Estate/7.01 Lease - Dayton Plant.txt", "Industrial Lease between Needmore Road Properties LLC (Landlord) and Meridian Coatings, Inc. (Tenant), dated June 1, 2016",
    "Premises: 212,000 square feet manufacturing and office at 4400 Needmore Road, Dayton. Term through May 31, 2031 with two five-year renewal options. Base rent $1,166,000 per year, escalating 2.5% annually.",
    "Assignment and subletting. Tenant may not assign this Lease or sublet the Premises without Landlord's prior written consent, not to be unreasonably withheld. A transfer of a controlling interest in Tenant, by merger, stock sale, or otherwise, is deemed an assignment; provided that a transfer to a successor with a tangible net worth of at least $50 million does not require consent but does require 30 days' notice.",
    "Environmental. Tenant is responsible for all Hazardous Materials brought onto the Premises during the term and must deliver a Phase II environmental assessment at Landlord's request at surrender.",
    boiler=("law", "notices", "counterparts", "entire"))
doc("07 Real Estate/7.02 Lease - Columbus Warehouse.txt", "Warehouse Lease between VFH Realty LLC and Meridian Coatings, Inc., dated January 1, 2020",
    "Premises: 48,000 square feet at 2200 Alum Creek Drive, Columbus. Rent $312,000 per year. Landlord is an affiliate of Vance Family Holdings LLC (related party). Month-to-month after December 31, 2025. Freely assignable to any successor to Tenant's business.",
    boiler=("law", "counterparts"))
doc("07 Real Estate/7.03 Deed - Toledo Facility.txt", "General Warranty Deed — 1850 Front Street, Toledo, Ohio",
    "Conveyed to MC Toledo Realty LLC by Great Lakes Industrial Partners on October 4, 2012. Parcel No. 18-77201. Subject to easements of record and to a mortgage in favor of First Meridian Bank, N.A. recorded September 2023.", boiler=())
doc("07 Real Estate/7.04 Phase I Environmental Site Assessment - Toledo.txt", "Phase I Environmental Site Assessment, 1850 Front Street, Toledo, Ohio — Brightwater Environmental, LLC, March 2025",
    "Recognized environmental conditions: (1) historical use of the parcel as a solvent recycling facility (1961–1988) with documented soil impacts; (2) current outdoor drum storage area without secondary containment adjacent to storm drain 002; (3) two 10,000-gallon underground storage tanks removed in 1997 with no closure documentation on file with the Ohio Bureau of Underground Storage Tank Regulations.",
    "Permits observed: NPDES industrial stormwater permit OHR000006 coverage, Toledo Division of Water Reclamation industrial pretreatment permit No. IU-0331, and a City of Toledo air installation permit for the line 4 curing oven. The assessor was unable to locate a current stormwater pollution prevention plan.",
    "Recommendation: Phase II subsurface investigation of the former solvent recycling area and the drum storage area; estimated cost $85,000 to $120,000.",
    boiler=())
doc("07 Real Estate/7.05 Title Commitment - Toledo.txt", "Commitment for Title Insurance — Chicago Title, Commitment No. 2025-04-TOL-118",
    "Schedule B exceptions: utility easements; a 1974 rail spur easement in favor of Norfolk Southern; the First Meridian mortgage; an environmental covenant recorded 2013 restricting groundwater use on the parcel.", boiler=())

# ---------------------------------------------------------------- 08 Regulatory & Environmental
doc("08 Regulatory and Environmental/8.01 Ohio EPA Title V Air Permit - Dayton.txt", "Title V Operating Permit No. P0128884 — Meridian Coatings, Inc., Dayton Facility (Ohio EPA, Division of Air Pollution Control)",
    "Issued March 2021; expires March 2026; renewal application due September 2025. Facility-wide VOC emission limit 92 tons per year. Emissions units P001–P006 (mixing and thinning), P007 (spray booth), P008 (curing oven). Requires monthly VOC material balance recordkeeping and semi-annual deviation reports.",
    "Compliance history: Notice of Violation issued January 17, 2024 for incomplete monthly VOC recordkeeping for June–October 2023 and for exceeding the 12-month rolling VOC limit at P007 in September 2023 (calculated 94.6 tons).",
    boiler=())
doc("08 Regulatory and Environmental/8.02 NPDES Permit - Toledo.txt", "NPDES Industrial Stormwater General Permit OHR000006 — Notice of Intent Coverage, MC Toledo Realty LLC / Meridian Coatings, Inc., Toledo Facility",
    "Coverage effective July 2021. Outfalls 001 and 002 to an unnamed tributary of the Ottawa River. Requires a Stormwater Pollution Prevention Plan, quarterly visual monitoring, and annual benchmark monitoring for oil and grease, TSS, and pH. Benchmark exceedances at outfall 002 reported for Q1 2024 and Q2 2024.",
    boiler=())
doc("08 Regulatory and Environmental/8.03 Notice of Violation - Ohio EPA 2024.txt", "Ohio EPA Notice of Violation dated January 17, 2024 — Dayton Facility, Title V Permit P0128884",
    "Violations cited: failure to maintain monthly VOC usage records for emissions unit P007 for June through October 2023; exceedance of the 12-month rolling VOC emission limit at P007 for the period ending September 2023; failure to report the deviation in the semi-annual report. The facility submitted a corrective action plan on March 1, 2024 (accepted April 2024) including installation of a regenerative thermal oxidizer by Q2 2026. Ohio EPA's initial proposed civil penalty is $187,500; negotiations are ongoing.",
    boiler=())
doc("08 Regulatory and Environmental/8.04 RCRA Hazardous Waste Generator Registration.txt", "RCRA Notification of Regulated Waste Activity",
    "Dayton: EPA ID OHD 987 654 321, Large Quantity Generator (spent solvents F003/F005, paint waste D001). Toledo: EPA ID OHD 123 456 789, Small Quantity Generator. Biennial reports filed 2023. Contracted transporter and TSDF: Heritage Environmental Services.", boiler=())
doc("08 Regulatory and Environmental/8.05 OSHA Inspection Report 2023.txt", "OSHA Inspection No. 1687221 — Dayton Facility, August 2023",
    "Citations: one serious (respiratory protection program — medical evaluations not documented for 14 employees), one other-than-serious (hazard communication labeling). Penalties $11,250, settled at $7,875 with abatement certified November 2023.", boiler=())
doc("08 Regulatory and Environmental/8.06 Compliance Certifications 2024.txt", "Annual Compliance Certifications, 2024",
    "Title V annual compliance certification (Dayton) — certified with deviations noted per the January 2024 NOV. Tier II chemical inventory reports filed for Dayton and Toledo. TSCA CDR submitted. No Prop 65 notices received.", boiler=())
FILES["08 Regulatory and Environmental/8.07 Stormwater Pollution Prevention Plan - PLACEHOLDER.txt"] = ""

# ---------------------------------------------------------------- 09 Insurance
doc("09 Insurance/9.01 Insurance Schedule.txt", "Schedule of Insurance Policies, 2025–2026 Policy Year",
    "Commercial general liability (Hartwell Mutual) $2M/$5M; umbrella $25M; products-completed operations included. Property (all risk) $140M TIV. Workers' compensation: Ohio state fund. Pollution legal liability (Sentinel Specialty) $10M per condition / $10M aggregate, claims-made, retroactive date July 1, 2019. Directors and officers $10M.", boiler=())
doc("09 Insurance/9.02 Pollution Legal Liability Policy.txt", "Pollution Legal Liability Policy No. PLL-88-40211 — Sentinel Specialty Insurance Company",
    "Insured locations: Dayton and Toledo. Covers on-site and off-site cleanup costs and third-party claims arising from pollution conditions first discovered during the policy period. Known conditions exclusion: excludes the former solvent recycling area at Toledo identified in the 2012 Phase I. Change of control: coverage continues for the acquired insured if the insurer is notified within 60 days; the policy is not assignable without consent.", boiler=())
doc("09 Insurance/9.03 D&O Policy.txt", "Directors and Officers Liability Policy — Sterling Underwriters",
    "$10M limit, $250,000 retention. Change in control provision: on a Change in Control the policy converts to run-off for the remainder of the policy period, and a six-year extended reporting period is available for 225% of the annual premium.", boiler=())
doc("09 Insurance/9.04 Loss Runs 2020-2024.txt", "Five-Year Loss Runs (all lines)",
    "General liability: 6 claims, $312,000 paid, $1,900,000 reserved (Dorsey). Workers' compensation: 41 claims, $684,000 incurred. Property: 2 claims, $95,000. Pollution: 1 notice (Tri-County), $0 paid, reserve not set.", boiler=())

# ---------------------------------------------------------------- 10 Tax
doc("10 Tax/10.01 Federal Income Tax Returns 2022-2024.txt", "Forms 1120, tax years 2022–2024 (summary)",
    "Consolidated returns filed timely. Taxable income 2024 $12.1 million; effective rate 23.4%. Section 174 R&E capitalization of $3.2 million. No NOL carryforwards. No IRS examinations open.", boiler=())
doc("10 Tax/10.02 State Nexus Study.txt", "Multistate Sales and Income Tax Nexus Study — Whitcomb & Ashe LLP, 2024",
    "Company files income/franchise returns in OH, MI, TN, WA, TX, CA. Study identified potential unfiled sales tax exposure in Georgia and North Carolina following Wayfair, estimated $140,000–$220,000 including interest.", boiler=())
doc("10 Tax/10.03 Sales and Use Tax Audit - Ohio.txt", "Ohio Department of Taxation Sales and Use Tax Audit, 2021–2023",
    "Assessment of $620,000 issued February 2025, principally on the claimed manufacturing exemption for the Toledo line 4 equipment. Petition for reassessment filed March 2025. Counsel assesses a 60% likelihood of reducing the assessment below $200,000.", boiler=())
doc("10 Tax/10.04 Transfer Pricing Memo.txt", "Transfer Pricing Memorandum — Meridian Coatings Europe GmbH",
    "The German sales subsidiary is compensated on a cost-plus 5% basis for sales support services. No intercompany product sales; products are sold directly by the US company to European customers with the GmbH as commission agent.", boiler=())

# ---------------------------------------------------------------- write everything
for rel, text in FILES.items():
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)

# two image-only "scanned" PDFs — exactly the kind of executed copy that has no text layer
try:
    from PIL import Image, ImageDraw

    def scanned_pdf(rel, lines):
        img = Image.new("RGB", (1240, 1754), "white")
        d = ImageDraw.Draw(img)
        y = 120
        for ln in lines:
            d.text((110, y), ln, fill=(30, 30, 30))
            y += 34
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        img.save(p, "PDF", resolution=150)

    scanned_pdf("03 Material Contracts/3.1 Customer Agreements/3.1.05 Amendment No. 2 - Halvorsen Marine (scanned).pdf",
                ["AMENDMENT NO. 2 TO MASTER SUPPLY AGREEMENT", "Halvorsen Marine A/S / Meridian Coatings, Inc.", "Executed May 12, 2025",
                 "Section 14.2 (Change of Control) is amended to provide that Halvorsen may terminate", "on 90 days' notice following any change of control of the Company, and that",
                 "the minimum purchase commitment in Section 3.1 is suspended for 12 months thereafter."])
    scanned_pdf("06 Litigation/6.06 Executed Tolling Agreement - Tri-County Water District (scanned).pdf",
                ["TOLLING AGREEMENT", "Tri-County Water District and Meridian Coatings, Inc.", "Executed August 2, 2024",
                 "The parties agree that all limitations periods are tolled through March 31, 2026", "while the parties negotiate."])
except ImportError:
    pass

n = sum(1 for _ in root.rglob("*") if _.is_file())
print(f"wrote {n} files under {root}")
