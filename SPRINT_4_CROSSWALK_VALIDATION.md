# Sprint 4 — Authoritative Crosswalk Validation

**Investigation date:** 2026-11-20  
**Database access:** read-only `SELECT` queries through `python/db_connect.py`; no database writes or DDL.  
**Project changes:** only this requested report was created. No SQL, Python, dataset, chart, KPI, or database object was modified.

## Executive summary

The official BTS October 2015 file confirms that the 5-digit values in the local October CSV are airport identifiers, not the airport-code values. The BTS archive has 486,165 records, matching the local October CSV’s 486,165 records and database October count (486,165). For all six compared flight identity fields—date, carrier, flight number, scheduled departure, origin ID, and destination ID—the multiset matches exactly for both `Reporting_Airline` and `IATA_CODE_Reporting_Airline` carrier fields. Adding tail number also gives an exact multiset match. This establishes the same flight population at the compared field level.

All 306 distinct local origin IDs and all 307 distinct local destination IDs were present in the corresponding BTS ID fields; per-ID frequencies match exactly. BTS provides exactly one airport code per ID in each direction for this October file. There were no multi-code IDs, no cross-direction ID/code conflicts, and no AirportSeqID variation for an ID within this month. All paired BTS airport codes match the local airport reference. Thus all 307 IDs in the union have an authoritative, October 2015 BTS mapping.

The ten existing SQL candidates are **all confirmed** by the official file, both as origin ID → origin code and destination ID → destination code. This validates their use for this October 2015 population only; it is not authorization to modify data in this sprint. No ambiguous, obsolete, or unresolved numeric IDs were found in the 307-ID union.

## Official source details

| Item | Value |
|---|---|
| Source URL | https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2015_10.zip |
| Download date | 2026-11-20 (UTC date) |
| Archive file | `On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2015_10.zip` |
| Archive size | 23,879,320 bytes |
| SHA-256 | `4f689e7b9e6410bcfd5ab91235e57523087e53ef4952d7261d1f164f244f08f7` |
| CSV inside archive | `On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2015_10.csv` |
| Uncompressed CSV size | 219,158,206 bytes |
| Official row count | 486,165 |
| FlightDate range | 2015-10-01 through 2015-10-31 |
| Required fields | All present: `OriginAirportID`, `OriginAirportSeqID`, `Origin`, `DestAirportID`, `DestAirportSeqID`, `Dest` |

The archive was processed in `Temp` temporary storage and removed after validation; it was not added to the project.

BTS defines `OriginAirportID` as a unique DOT-assigned airport identifier and `Origin` as the airport-code field; `OriginAirportSeqID` is the time-specific sequence identifier. The destination fields have the corresponding meanings. See the [BTS TranStats field definitions](https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ) and [official table profile/definitions](https://transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&V0s1_b0yB=D&gnoyr_VQ=FGJ).

## Dataset compatibility and population comparison

| Check | Result |
|---|---|
| Required official fields | Present |
| Official October rows | 486,165 |
| Local October CSV rows | 486,165 |
| Database October rows | 486,165 |
| Official date range | 2015-10-01 to 2015-10-31 |
| Distinct local origin numeric IDs vs official `OriginAirportID` | 306 vs 306; sets equal: True; frequency mismatches: 0 |
| Distinct local destination numeric IDs vs official `DestAirportID` | 307 vs 307; sets equal: True; frequency mismatches: 0 |
| Flight key multiset: date + carrier + flight number + scheduled departure + both airport IDs | exact match with BTS `Reporting_Airline`: True; exact match with `IATA_CODE_Reporting_Airline`: True |
| Same flight key plus tail number | exact match with BTS `Reporting_Airline`: True; exact match with `IATA_CODE_Reporting_Airline`: True |
| Airport IDs map to same code in origin and destination fields when present in both | conflicts: 0 |
| Official code maps to the local 322-code airport reference | unmatched origin IDs: 0; unmatched destination IDs: 0 |

This is stronger than matching monthly totals: each flight-key multiplicity matches, including both numeric airport IDs. The local values therefore correspond to the official DOT airport-ID columns, while BTS’s `Origin` and `Dest` values supply the airport codes.

## ID-to-code validation results

**Status definition:** “Confirmed” means that the corresponding numeric local ID equals the official BTS airport-ID field, BTS provides one code for that ID in the relevant direction, the ID/code frequency matches the local source, the ID has one sequence ID within October, and the code exists in the local airport reference. All IDs meet this condition in both applicable directions.

- Origin: 306 IDs, 306 distinct `(OriginAirportID, OriginAirportSeqID, Origin)` tuples; ambiguous/multi-code IDs: 0; IDs with multiple sequence IDs: 0.
- Destination: 307 IDs, 307 distinct `(DestAirportID, DestAirportSeqID, Dest)` tuples; ambiguous/multi-code IDs: 0; IDs with multiple sequence IDs: 0.
- Across origin and destination together: IDs with conflicting airport codes: 0.
- Mapping coverage: 307 of 307 IDs in the union confirmed; ambiguous: 0; obsolete: 0 identified in this October snapshot; unresolved: 0.

### Ten existing SQL candidates

Every candidate below is confirmed in BTS. Local and BTS frequencies are shown separately; their equality validates the frequency comparison, while the flight-key comparison above establishes population alignment.

| Numeric ID | Existing SQL IATA candidate | BTS origin code(s) | BTS destination code(s) | Origin rows: local / BTS | Destination rows: local / BTS | Local reference match |
|---:|:---:|:---|:---|---:|---:|:---:|
| 10397 | ATL | ATL | ATL | 32,588 / 32,588 | 32,594 / 32,594 | yes |
| 13930 | ORD | ORD | ORD | 27,652 / 27,652 | 27,608 / 27,608 | yes |
| 11298 | DFW | DFW | DFW | 21,044 / 21,044 | 21,033 / 21,033 | yes |
| 11292 | DEN | DEN | DEN | 18,136 / 18,136 | 18,125 / 18,125 | yes |
| 12892 | LAX | LAX | LAX | 17,728 / 17,728 | 17,739 / 17,739 | yes |
| 14771 | SFO | SFO | SFO | 14,170 / 14,170 | 14,170 / 14,170 | yes |
| 12266 | IAH | IAH | IAH | 13,211 / 13,211 | 13,227 / 13,227 | yes |
| 14107 | PHX | PHX | PHX | 12,921 / 12,921 | 12,932 / 12,932 | yes |
| 12889 | LAS | LAS | LAS | 12,688 / 12,688 | 12,702 / 12,702 | yes |
| 13487 | MSP | MSP | MSP | 10,584 / 10,584 | 10,623 / 10,623 | yes |

### All 307 numeric IDs

The following table gives the complete origin and destination results separately for every ID in the union. “—” means that the ID does not occur in that direction during October. `AirportSeqID` values are shown as recorded in the official file.

| Numeric ID | Local origin rows | BTS origin code | BTS origin rows | Origin sequence ID(s) | Local destination rows | BTS destination code | BTS destination rows | Destination sequence ID(s) | Status |
|---:|---:|:---:|---:|:---|---:|:---:|---:|:---|:---|
| 10135 | 239 | ABE | 239 | 1013503 | 238 | ABE | 238 | 1013503 | Confirmed in both directions |
| 10136 | 201 | ABI | 201 | 1013603 | 201 | ABI | 201 | 1013603 | Confirmed in both directions |
| 10140 | 1,816 | ABQ | 1,816 | 1014003 | 1,815 | ABQ | 1,815 | 1014003 | Confirmed in both directions |
| 10141 | 71 | ABR | 71 | 1014103 | 71 | ABR | 71 | 1014103 | Confirmed in both directions |
| 10146 | 87 | ABY | 87 | 1014602 | 87 | ABY | 87 | 1014602 | Confirmed in both directions |
| 10154 | 28 | ACK | 28 | 1015403 | 28 | ACK | 28 | 1015403 | Confirmed in both directions |
| 10155 | 148 | ACT | 148 | 1015502 | 148 | ACT | 148 | 1015502 | Confirmed in both directions |
| 10157 | 122 | ACV | 122 | 1015703 | 122 | ACV | 122 | 1015703 | Confirmed in both directions |
| 10158 | 248 | ACY | 248 | 1015804 | 248 | ACY | 248 | 1015804 | Confirmed in both directions |
| 10165 | 9 | ADK | 9 | 1016503 | 9 | ADK | 9 | 1016503 | Confirmed in both directions |
| 10170 | 31 | ADQ | 31 | 1017001 | 31 | ADQ | 31 | 1017001 | Confirmed in both directions |
| 10185 | 282 | AEX | 282 | 1018502 | 282 | AEX | 282 | 1018502 | Confirmed in both directions |
| 10208 | 223 | AGS | 223 | 1020803 | 222 | AGS | 222 | 1020803 | Confirmed in both directions |
| 10257 | 734 | ALB | 734 | 1025702 | 733 | ALB | 733 | 1025702 | Confirmed in both directions |
| 10268 | 57 | ALO | 57 | 1026802 | 56 | ALO | 56 | 1026802 | Confirmed in both directions |
| 10279 | 307 | AMA | 307 | 1027903 | 307 | AMA | 307 | 1027903 | Confirmed in both directions |
| 10299 | 1,234 | ANC | 1,234 | 1029904 | 1,232 | ANC | 1,232 | 1029904 | Confirmed in both directions |
| 10333 | 53 | APN | 53 | 1033302 | 53 | APN | 53 | 1033302 | Confirmed in both directions |
| 10372 | 59 | ASE | 59 | 1037203 | 59 | ASE | 59 | 1037203 | Confirmed in both directions |
| 10397 | 32,588 | ATL | 32,588 | 1039705 | 32,594 | ATL | 32,594 | 1039705 | Confirmed in both directions |
| 10408 | 260 | ATW | 260 | 1040803 | 260 | ATW | 260 | 1040803 | Confirmed in both directions |
| 10423 | 4,021 | AUS | 4,021 | 1042302 | 4,014 | AUS | 4,014 | 1042302 | Confirmed in both directions |
| 10431 | 284 | AVL | 284 | 1043102 | 283 | AVL | 283 | 1043102 | Confirmed in both directions |
| 10434 | 113 | AVP | 113 | 1043403 | 113 | AVP | 113 | 1043403 | Confirmed in both directions |
| 10469 | 121 | AZO | 121 | 1046902 | 121 | AZO | 121 | 1046902 | Confirmed in both directions |
| 10529 | 1,714 | BDL | 1,714 | 1052904 | 1,715 | BDL | 1,715 | 1052904 | Confirmed in both directions |
| 10551 | 84 | BET | 84 | 1055102 | 84 | BET | 84 | 1055102 | Confirmed in both directions |
| 10561 | 183 | BFL | 183 | 1056103 | 183 | BFL | 183 | 1056103 | Confirmed in both directions |
| 10577 | 62 | BGM | 62 | 1057703 | 61 | BGM | 61 | 1057703 | Confirmed in both directions |
| 10581 | 27 | BGR | 27 | 1058102 | 26 | BGR | 26 | 1058102 | Confirmed in both directions |
| 10599 | 1,146 | BHM | 1,146 | 1059904 | 1,146 | BHM | 1,146 | 1059904 | Confirmed in both directions |
| 10620 | 264 | BIL | 264 | 1062002 | 263 | BIL | 263 | 1062002 | Confirmed in both directions |
| 10627 | 339 | BIS | 339 | 1062702 | 340 | BIS | 340 | 1062702 | Confirmed in both directions |
| 10631 | 62 | BJI | 62 | 1063104 | 62 | BJI | 62 | 1063104 | Confirmed in both directions |
| 10666 | 0 | — | 0 | — | 1 | BLI | 1 | 1066602 | Confirmed (destination only) |
| 10685 | 238 | BMI | 238 | 1068502 | 238 | BMI | 238 | 1068502 | Confirmed in both directions |
| 10693 | 4,477 | BNA | 4,477 | 1069302 | 4,479 | BNA | 4,479 | 1069302 | Confirmed in both directions |
| 10713 | 1,160 | BOI | 1,160 | 1071302 | 1,163 | BOI | 1,163 | 1071302 | Confirmed in both directions |
| 10721 | 10,164 | BOS | 10,164 | 1072102 | 10,161 | BOS | 10,161 | 1072102 | Confirmed in both directions |
| 10728 | 87 | BPT | 87 | 1072804 | 87 | BPT | 87 | 1072804 | Confirmed in both directions |
| 10731 | 85 | BQK | 85 | 1073103 | 85 | BQK | 85 | 1073103 | Confirmed in both directions |
| 10732 | 96 | BQN | 96 | 1073203 | 98 | BQN | 98 | 1073203 | Confirmed in both directions |
| 10739 | 53 | BRD | 53 | 1073905 | 53 | BRD | 53 | 1073905 | Confirmed in both directions |
| 10747 | 204 | BRO | 204 | 1074702 | 203 | BRO | 203 | 1074702 | Confirmed in both directions |
| 10754 | 81 | BRW | 81 | 1075403 | 81 | BRW | 81 | 1075403 | Confirmed in both directions |
| 10779 | 62 | BTM | 62 | 1077902 | 62 | BTM | 62 | 1077902 | Confirmed in both directions |
| 10781 | 659 | BTR | 659 | 1078103 | 659 | BTR | 659 | 1078103 | Confirmed in both directions |
| 10785 | 348 | BTV | 348 | 1078502 | 349 | BTV | 349 | 1078502 | Confirmed in both directions |
| 10792 | 1,593 | BUF | 1,593 | 1079204 | 1,587 | BUF | 1,587 | 1079204 | Confirmed in both directions |
| 10800 | 1,768 | BUR | 1,768 | 1080003 | 1,767 | BUR | 1,767 | 1080003 | Confirmed in both directions |
| 10821 | 8,022 | BWI | 8,022 | 1082103 | 8,020 | BWI | 8,020 | 1082103 | Confirmed in both directions |
| 10849 | 335 | BZN | 335 | 1084903 | 335 | BZN | 335 | 1084903 | Confirmed in both directions |
| 10868 | 434 | CAE | 434 | 1086803 | 434 | CAE | 434 | 1086803 | Confirmed in both directions |
| 10874 | 491 | CAK | 491 | 1087402 | 490 | CAK | 490 | 1087402 | Confirmed in both directions |
| 10918 | 53 | CDC | 53 | 1091802 | 53 | CDC | 53 | 1091802 | Confirmed in both directions |
| 10926 | 62 | CDV | 62 | 1092603 | 62 | CDV | 62 | 1092603 | Confirmed in both directions |
| 10980 | 417 | CHA | 417 | 1098002 | 416 | CHA | 416 | 1098002 | Confirmed in both directions |
| 10990 | 237 | CHO | 237 | 1099002 | 237 | CHO | 237 | 1099002 | Confirmed in both directions |
| 10994 | 1,207 | CHS | 1,207 | 1099402 | 1,207 | CHS | 1,207 | 1099402 | Confirmed in both directions |
| 11003 | 532 | CID | 532 | 1100303 | 533 | CID | 533 | 1100303 | Confirmed in both directions |
| 11013 | 57 | CIU | 57 | 1101303 | 57 | CIU | 57 | 1101303 | Confirmed in both directions |
| 11042 | 3,224 | CLE | 3,224 | 1104203 | 3,221 | CLE | 3,221 | 1104203 | Confirmed in both directions |
| 11049 | 223 | CLL | 223 | 1104902 | 222 | CLL | 222 | 1104902 | Confirmed in both directions |
| 11057 | 9,572 | CLT | 9,572 | 1105703 | 9,573 | CLT | 9,573 | 1105703 | Confirmed in both directions |
| 11066 | 2,188 | CMH | 2,188 | 1106603 | 2,188 | CMH | 2,188 | 1106603 | Confirmed in both directions |
| 11067 | 206 | CMI | 206 | 1106702 | 206 | CMI | 206 | 1106702 | Confirmed in both directions |
| 11076 | 62 | CMX | 62 | 1107602 | 62 | CMX | 62 | 1107602 | Confirmed in both directions |
| 11097 | 31 | COD | 31 | 1109702 | 31 | COD | 31 | 1109702 | Confirmed in both directions |
| 11109 | 610 | COS | 610 | 1110902 | 607 | COS | 607 | 1110902 | Confirmed in both directions |
| 11111 | 123 | COU | 123 | 1111102 | 123 | COU | 123 | 1111102 | Confirmed in both directions |
| 11122 | 138 | CPR | 138 | 1112203 | 139 | CPR | 139 | 1112203 | Confirmed in both directions |
| 11140 | 366 | CRP | 366 | 1114005 | 366 | CRP | 366 | 1114005 | Confirmed in both directions |
| 11146 | 224 | CRW | 224 | 1114604 | 224 | CRW | 224 | 1114604 | Confirmed in both directions |
| 11150 | 112 | CSG | 112 | 1115003 | 112 | CSG | 112 | 1115003 | Confirmed in both directions |
| 11193 | 1,919 | CVG | 1,919 | 1119302 | 1,917 | CVG | 1,917 | 1119302 | Confirmed in both directions |
| 11203 | 145 | CWA | 145 | 1120302 | 144 | CWA | 144 | 1120302 | Confirmed in both directions |
| 11252 | 119 | DAB | 119 | 1125203 | 119 | DAB | 119 | 1125203 | Confirmed in both directions |
| 11259 | 5,930 | DAL | 5,930 | 1125903 | 5,930 | DAL | 5,930 | 1125903 | Confirmed in both directions |
| 11267 | 753 | DAY | 753 | 1126702 | 753 | DAY | 753 | 1126702 | Confirmed in both directions |
| 11274 | 87 | DBQ | 87 | 1127402 | 87 | DBQ | 87 | 1127402 | Confirmed in both directions |
| 11278 | 6,819 | DCA | 6,819 | 1127803 | 6,818 | DCA | 6,818 | 1127803 | Confirmed in both directions |
| 11292 | 18,136 | DEN | 18,136 | 1129202 | 18,125 | DEN | 18,125 | 1129202 | Confirmed in both directions |
| 11298 | 21,044 | DFW | 21,044 | 1129804 | 21,033 | DFW | 21,033 | 1129804 | Confirmed in both directions |
| 11308 | 118 | DHN | 118 | 1130802 | 118 | DHN | 118 | 1130802 | Confirmed in both directions |
| 11315 | 61 | DIK | 61 | 1131502 | 61 | DIK | 61 | 1131502 | Confirmed in both directions |
| 11337 | 223 | DLH | 223 | 1133703 | 223 | DLH | 223 | 1133703 | Confirmed in both directions |
| 11413 | 178 | DRO | 178 | 1141304 | 178 | DRO | 178 | 1141304 | Confirmed in both directions |
| 11423 | 710 | DSM | 710 | 1142303 | 710 | DSM | 710 | 1142303 | Confirmed in both directions |
| 11433 | 9,925 | DTW | 9,925 | 1143302 | 9,913 | DTW | 9,913 | 1143302 | Confirmed in both directions |
| 11447 | 49 | DVL | 49 | 1144703 | 48 | DVL | 48 | 1144703 | Confirmed in both directions |
| 11471 | 62 | EAU | 62 | 1147103 | 62 | EAU | 62 | 1147103 | Confirmed in both directions |
| 11481 | 376 | ECP | 376 | 1148102 | 375 | ECP | 375 | 1148102 | Confirmed in both directions |
| 11503 | 4 | EGE | 4 | 1150303 | 3 | EGE | 3 | 1150303 | Confirmed in both directions |
| 11525 | 53 | EKO | 53 | 1152503 | 53 | EKO | 53 | 1152503 | Confirmed in both directions |
| 11537 | 195 | ELM | 195 | 1153703 | 195 | ELM | 195 | 1153703 | Confirmed in both directions |
| 11540 | 1,046 | ELP | 1,046 | 1154003 | 1,045 | ELP | 1,045 | 1154003 | Confirmed in both directions |
| 11577 | 57 | ERI | 57 | 1157704 | 57 | ERI | 57 | 1157704 | Confirmed in both directions |
| 11587 | 53 | ESC | 53 | 1158702 | 53 | ESC | 53 | 1158702 | Confirmed in both directions |
| 11603 | 328 | EUG | 328 | 1160302 | 328 | EUG | 328 | 1160302 | Confirmed in both directions |
| 11612 | 399 | EVV | 399 | 1161204 | 399 | EVV | 399 | 1161204 | Confirmed in both directions |
| 11617 | 55 | EWN | 55 | 1161706 | 55 | EWN | 55 | 1161706 | Confirmed in both directions |
| 11618 | 9,622 | EWR | 9,622 | 1161802 | 9,656 | EWR | 9,656 | 1161802 | Confirmed in both directions |
| 11624 | 151 | EYW | 151 | 1162402 | 151 | EYW | 151 | 1162402 | Confirmed in both directions |
| 11630 | 177 | FAI | 177 | 1163002 | 177 | FAI | 177 | 1163002 | Confirmed in both directions |
| 11637 | 527 | FAR | 527 | 1163703 | 526 | FAR | 526 | 1163703 | Confirmed in both directions |
| 11638 | 656 | FAT | 656 | 1163805 | 657 | FAT | 657 | 1163805 | Confirmed in both directions |
| 11641 | 150 | FAY | 150 | 1164102 | 150 | FAY | 150 | 1164102 | Confirmed in both directions |
| 11648 | 123 | FCA | 123 | 1164802 | 123 | FCA | 123 | 1164802 | Confirmed in both directions |
| 11695 | 158 | FLG | 158 | 1169502 | 158 | FLG | 158 | 1169502 | Confirmed in both directions |
| 11697 | 5,812 | FLL | 5,812 | 1169704 | 5,820 | FLL | 5,820 | 1169704 | Confirmed in both directions |
| 11721 | 413 | FNT | 413 | 1172102 | 412 | FNT | 412 | 1172102 | Confirmed in both directions |
| 11775 | 445 | FSD | 445 | 1177502 | 444 | FSD | 444 | 1177502 | Confirmed in both directions |
| 11778 | 180 | FSM | 180 | 1177801 | 180 | FSM | 180 | 1177801 | Confirmed in both directions |
| 11823 | 511 | FWA | 511 | 1182304 | 511 | FWA | 511 | 1182304 | Confirmed in both directions |
| 11865 | 88 | GCC | 88 | 1186502 | 88 | GCC | 88 | 1186502 | Confirmed in both directions |
| 11867 | 62 | GCK | 62 | 1186703 | 62 | GCK | 62 | 1186703 | Confirmed in both directions |
| 11884 | 828 | GEG | 828 | 1188402 | 829 | GEG | 829 | 1188402 | Confirmed in both directions |
| 11898 | 90 | GFK | 90 | 1189802 | 89 | GFK | 89 | 1189802 | Confirmed in both directions |
| 11905 | 59 | GGG | 59 | 1190502 | 60 | GGG | 60 | 1190502 | Confirmed in both directions |
| 11921 | 271 | GJT | 271 | 1192102 | 271 | GJT | 271 | 1192102 | Confirmed in both directions |
| 11953 | 234 | GNV | 234 | 1195302 | 234 | GNV | 234 | 1195302 | Confirmed in both directions |
| 11973 | 304 | GPT | 304 | 1197302 | 303 | GPT | 303 | 1197302 | Confirmed in both directions |
| 11977 | 489 | GRB | 489 | 1197702 | 488 | GRB | 488 | 1197702 | Confirmed in both directions |
| 11980 | 57 | GRI | 57 | 1198002 | 57 | GRI | 57 | 1198002 | Confirmed in both directions |
| 11982 | 371 | GRK | 371 | 1198202 | 370 | GRK | 370 | 1198202 | Confirmed in both directions |
| 11986 | 928 | GRR | 928 | 1198603 | 927 | GRR | 927 | 1198603 | Confirmed in both directions |
| 11995 | 598 | GSO | 598 | 1199502 | 595 | GSO | 595 | 1199502 | Confirmed in both directions |
| 11996 | 631 | GSP | 631 | 1199603 | 630 | GSP | 630 | 1199603 | Confirmed in both directions |
| 12003 | 190 | GTF | 190 | 1200302 | 190 | GTF | 190 | 1200302 | Confirmed in both directions |
| 12007 | 88 | GTR | 88 | 1200702 | 88 | GTR | 88 | 1200702 | Confirmed in both directions |
| 12016 | 31 | GUM | 31 | 1201602 | 31 | GUM | 31 | 1201602 | Confirmed in both directions |
| 12094 | 20 | HDN | 20 | 1209402 | 20 | HDN | 20 | 1209402 | Confirmed in both directions |
| 12129 | 84 | HIB | 84 | 1212903 | 84 | HIB | 84 | 1212903 | Confirmed in both directions |
| 12156 | 141 | HLN | 141 | 1215603 | 141 | HLN | 141 | 1215603 | Confirmed in both directions |
| 12173 | 3,780 | HNL | 3,780 | 1217302 | 3,780 | HNL | 3,780 | 1217302 | Confirmed in both directions |
| 12177 | 53 | HOB | 53 | 1217703 | 53 | HOB | 53 | 1217703 | Confirmed in both directions |
| 12191 | 4,718 | HOU | 4,718 | 1219102 | 4,717 | HOU | 4,717 | 1219102 | Confirmed in both directions |
| 12197 | 721 | HPN | 721 | 1219702 | 720 | HPN | 720 | 1219702 | Confirmed in both directions |
| 12206 | 287 | HRL | 287 | 1220603 | 286 | HRL | 286 | 1220603 | Confirmed in both directions |
| 12217 | 390 | HSV | 390 | 1221702 | 390 | HSV | 390 | 1221702 | Confirmed in both directions |
| 12255 | 53 | HYS | 53 | 1225502 | 53 | HYS | 53 | 1225502 | Confirmed in both directions |
| 12264 | 2,996 | IAD | 2,996 | 1226402 | 3,000 | IAD | 3,000 | 1226402 | Confirmed in both directions |
| 12265 | 22 | IAG | 22 | 1226503 | 22 | IAG | 22 | 1226503 | Confirmed in both directions |
| 12266 | 13,211 | IAH | 13,211 | 1226603 | 13,227 | IAH | 13,227 | 1226603 | Confirmed in both directions |
| 12278 | 698 | ICT | 698 | 1227803 | 698 | ICT | 698 | 1227803 | Confirmed in both directions |
| 12280 | 201 | IDA | 201 | 1228002 | 201 | IDA | 201 | 1228002 | Confirmed in both directions |
| 12323 | 215 | ILM | 215 | 1232303 | 215 | ILM | 215 | 1232303 | Confirmed in both directions |
| 12335 | 58 | IMT | 58 | 1233502 | 57 | IMT | 57 | 1233502 | Confirmed in both directions |
| 12339 | 2,373 | IND | 2,373 | 1233904 | 2,378 | IND | 2,378 | 1233904 | Confirmed in both directions |
| 12343 | 53 | INL | 53 | 1234303 | 53 | INL | 53 | 1234303 | Confirmed in both directions |
| 12389 | 221 | ISN | 221 | 1238902 | 220 | ISN | 220 | 1238902 | Confirmed in both directions |
| 12391 | 366 | ISP | 366 | 1239102 | 366 | ISP | 366 | 1239102 | Confirmed in both directions |
| 12402 | 503 | ITO | 503 | 1240203 | 504 | ITO | 504 | 1240203 | Confirmed in both directions |
| 12441 | 158 | JAC | 158 | 1244102 | 157 | JAC | 157 | 1244102 | Confirmed in both directions |
| 12448 | 654 | JAN | 654 | 1244805 | 654 | JAN | 654 | 1244805 | Confirmed in both directions |
| 12451 | 1,712 | JAX | 1,712 | 1245102 | 1,710 | JAX | 1,710 | 1245102 | Confirmed in both directions |
| 12478 | 8,303 | JFK | 8,303 | 1247803 | 8,285 | JFK | 8,285 | 1247803 | Confirmed in both directions |
| 12511 | 58 | JLN | 58 | 1251102 | 58 | JLN | 58 | 1251102 | Confirmed in both directions |
| 12519 | 75 | JMS | 75 | 1251902 | 75 | JMS | 75 | 1251902 | Confirmed in both directions |
| 12523 | 336 | JNU | 336 | 1252303 | 336 | JNU | 336 | 1252303 | Confirmed in both directions |
| 12758 | 967 | KOA | 967 | 1275803 | 967 | KOA | 967 | 1275803 | Confirmed in both directions |
| 12819 | 186 | KTN | 186 | 1281902 | 186 | KTN | 186 | 1281902 | Confirmed in both directions |
| 12884 | 222 | LAN | 222 | 1288403 | 224 | LAN | 224 | 1288403 | Confirmed in both directions |
| 12888 | 53 | LAR | 53 | 1288802 | 53 | LAR | 53 | 1288802 | Confirmed in both directions |
| 12889 | 12,688 | LAS | 12,688 | 1288903 | 12,702 | LAS | 12,702 | 1288903 | Confirmed in both directions |
| 12891 | 124 | LAW | 124 | 1289102 | 124 | LAW | 124 | 1289102 | Confirmed in both directions |
| 12892 | 17,728 | LAX | 17,728 | 1289203 | 17,739 | LAX | 17,739 | 1289203 | Confirmed in both directions |
| 12896 | 436 | LBB | 436 | 1289605 | 435 | LBB | 435 | 1289605 | Confirmed in both directions |
| 12898 | 117 | LBE | 117 | 1289803 | 117 | LBE | 117 | 1289803 | Confirmed in both directions |
| 12915 | 198 | LCH | 198 | 1291503 | 198 | LCH | 198 | 1291503 | Confirmed in both directions |
| 12945 | 587 | LEX | 587 | 1294503 | 586 | LEX | 586 | 1294503 | Confirmed in both directions |
| 12951 | 431 | LFT | 431 | 1295104 | 432 | LFT | 432 | 1295104 | Confirmed in both directions |
| 12953 | 8,590 | LGA | 8,590 | 1295302 | 8,570 | LGA | 8,570 | 1295302 | Confirmed in both directions |
| 12954 | 774 | LGB | 774 | 1295402 | 775 | LGB | 775 | 1295402 | Confirmed in both directions |
| 12982 | 881 | LIH | 881 | 1298202 | 882 | LIH | 882 | 1298202 | Confirmed in both directions |
| 12992 | 1,048 | LIT | 1,048 | 1299204 | 1,050 | LIT | 1,050 | 1299204 | Confirmed in both directions |
| 13029 | 288 | LNK | 288 | 1302902 | 288 | LNK | 288 | 1302902 | Confirmed in both directions |
| 13061 | 203 | LRD | 203 | 1306104 | 203 | LRD | 203 | 1306104 | Confirmed in both directions |
| 13076 | 166 | LSE | 166 | 1307603 | 166 | LSE | 166 | 1307603 | Confirmed in both directions |
| 13127 | 53 | LWS | 53 | 1312702 | 53 | LWS | 53 | 1312702 | Confirmed in both directions |
| 13158 | 600 | MAF | 600 | 1315802 | 601 | MAF | 601 | 1315802 | Confirmed in both directions |
| 13184 | 142 | MBS | 142 | 1318403 | 142 | MBS | 142 | 1318403 | Confirmed in both directions |
| 13198 | 3,555 | MCI | 3,555 | 1319801 | 3,557 | MCI | 3,557 | 1319801 | Confirmed in both directions |
| 13204 | 9,047 | MCO | 9,047 | 1320402 | 9,048 | MCO | 9,048 | 1320402 | Confirmed in both directions |
| 13230 | 285 | MDT | 285 | 1323002 | 285 | MDT | 285 | 1323002 | Confirmed in both directions |
| 13232 | 7,617 | MDW | 7,617 | 1323202 | 7,613 | MDW | 7,613 | 1323202 | Confirmed in both directions |
| 13241 | 84 | MEI | 84 | 1324102 | 84 | MEI | 84 | 1324102 | Confirmed in both directions |
| 13244 | 1,520 | MEM | 1,520 | 1324402 | 1,518 | MEM | 1,518 | 1324402 | Confirmed in both directions |
| 13256 | 238 | MFE | 238 | 1325602 | 239 | MFE | 239 | 1325602 | Confirmed in both directions |
| 13264 | 243 | MFR | 243 | 1326403 | 243 | MFR | 243 | 1326403 | Confirmed in both directions |
| 13277 | 309 | MGM | 309 | 1327702 | 309 | MGM | 309 | 1327702 | Confirmed in both directions |
| 13290 | 151 | MHK | 151 | 1329002 | 151 | MHK | 151 | 1329002 | Confirmed in both directions |
| 13296 | 577 | MHT | 577 | 1329604 | 579 | MHT | 579 | 1329604 | Confirmed in both directions |
| 13303 | 5,958 | MIA | 5,958 | 1330303 | 5,956 | MIA | 5,956 | 1330303 | Confirmed in both directions |
| 13342 | 2,642 | MKE | 2,642 | 1334205 | 2,644 | MKE | 2,644 | 1334205 | Confirmed in both directions |
| 13344 | 62 | MKG | 62 | 1334402 | 62 | MKG | 62 | 1334402 | Confirmed in both directions |
| 13360 | 116 | MLB | 116 | 1336003 | 116 | MLB | 116 | 1336003 | Confirmed in both directions |
| 13367 | 308 | MLI | 308 | 1336703 | 308 | MLI | 308 | 1336703 | Confirmed in both directions |
| 13377 | 279 | MLU | 279 | 1337702 | 278 | MLU | 278 | 1337702 | Confirmed in both directions |
| 13422 | 437 | MOB | 437 | 1342202 | 438 | MOB | 438 | 1342202 | Confirmed in both directions |
| 13433 | 218 | MOT | 218 | 1343302 | 218 | MOT | 218 | 1343302 | Confirmed in both directions |
| 13459 | 26 | MQT | 26 | 1345902 | 26 | MQT | 26 | 1345902 | Confirmed in both directions |
| 13476 | 241 | MRY | 241 | 1347603 | 241 | MRY | 241 | 1347603 | Confirmed in both directions |
| 13485 | 838 | MSN | 838 | 1348502 | 837 | MSN | 837 | 1348502 | Confirmed in both directions |
| 13486 | 171 | MSO | 171 | 1348602 | 170 | MSO | 170 | 1348602 | Confirmed in both directions |
| 13487 | 10,584 | MSP | 10,584 | 1348702 | 10,623 | MSP | 10,623 | 1348702 | Confirmed in both directions |
| 13495 | 3,663 | MSY | 3,663 | 1349503 | 3,670 | MSY | 3,670 | 1349503 | Confirmed in both directions |
| 13502 | 6 | MTJ | 6 | 1350202 | 7 | MTJ | 7 | 1350202 | Confirmed in both directions |
| 13541 | 11 | MVY | 11 | 1354102 | 11 | MVY | 11 | 1354102 | Confirmed in both directions |
| 13577 | 507 | MYR | 507 | 1357702 | 507 | MYR | 507 | 1357702 | Confirmed in both directions |
| 13795 | 112 | OAJ | 112 | 1379502 | 112 | OAJ | 112 | 1379502 | Confirmed in both directions |
| 13796 | 4,016 | OAK | 4,016 | 1379604 | 4,012 | OAK | 4,012 | 1379604 | Confirmed in both directions |
| 13830 | 1,823 | OGG | 1,823 | 1383002 | 1,823 | OGG | 1,823 | 1383002 | Confirmed in both directions |
| 13851 | 1,641 | OKC | 1,641 | 1385103 | 1,639 | OKC | 1,639 | 1385103 | Confirmed in both directions |
| 13871 | 1,501 | OMA | 1,501 | 1387102 | 1,501 | OMA | 1,501 | 1387102 | Confirmed in both directions |
| 13873 | 62 | OME | 62 | 1387303 | 62 | OME | 62 | 1387303 | Confirmed in both directions |
| 13891 | 1,742 | ONT | 1,742 | 1389101 | 1,742 | ONT | 1,742 | 1389101 | Confirmed in both directions |
| 13930 | 27,652 | ORD | 27,652 | 1393004 | 27,608 | ORD | 27,608 | 1393004 | Confirmed in both directions |
| 13931 | 914 | ORF | 914 | 1393102 | 911 | ORF | 911 | 1393102 | Confirmed in both directions |
| 13933 | 62 | ORH | 62 | 1393303 | 62 | ORH | 62 | 1393303 | Confirmed in both directions |
| 13964 | 36 | OTH | 36 | 1396403 | 36 | OTH | 36 | 1396403 | Confirmed in both directions |
| 13970 | 62 | OTZ | 62 | 1397003 | 62 | OTZ | 62 | 1397003 | Confirmed in both directions |
| 14006 | 62 | PAH | 62 | 1400602 | 62 | PAH | 62 | 1400602 | Confirmed in both directions |
| 14025 | 13 | PBG | 13 | 1402501 | 13 | PBG | 13 | 1402501 | Confirmed in both directions |
| 14027 | 1,742 | PBI | 1,742 | 1402702 | 1,746 | PBI | 1,746 | 1402702 | Confirmed in both directions |
| 14057 | 4,550 | PDX | 4,550 | 1405702 | 4,553 | PDX | 4,553 | 1405702 | Confirmed in both directions |
| 14098 | 114 | PHF | 114 | 1409803 | 114 | PHF | 114 | 1409803 | Confirmed in both directions |
| 14100 | 6,094 | PHL | 6,094 | 1410002 | 6,089 | PHL | 6,089 | 1410002 | Confirmed in both directions |
| 14107 | 12,921 | PHX | 12,921 | 1410702 | 12,932 | PHX | 12,932 | 1410702 | Confirmed in both directions |
| 14108 | 476 | PIA | 476 | 1410803 | 475 | PIA | 475 | 1410803 | Confirmed in both directions |
| 14109 | 53 | PIB | 53 | 1410902 | 53 | PIB | 53 | 1410902 | Confirmed in both directions |
| 14113 | 57 | PIH | 57 | 1411302 | 57 | PIH | 57 | 1411302 | Confirmed in both directions |
| 14122 | 2,131 | PIT | 2,131 | 1412202 | 2,130 | PIT | 2,130 | 1412202 | Confirmed in both directions |
| 14150 | 62 | PLN | 62 | 1415002 | 62 | PLN | 62 | 1415002 | Confirmed in both directions |
| 14193 | 478 | PNS | 478 | 1419304 | 478 | PNS | 478 | 1419304 | Confirmed in both directions |
| 14222 | 9 | PPG | 9 | 1422204 | 9 | PPG | 9 | 1422204 | Confirmed in both directions |
| 14252 | 210 | PSC | 210 | 1425202 | 210 | PSC | 210 | 1425202 | Confirmed in both directions |
| 14254 | 62 | PSE | 62 | 1425403 | 62 | PSE | 62 | 1425403 | Confirmed in both directions |
| 14256 | 62 | PSG | 62 | 1425603 | 62 | PSG | 62 | 1425603 | Confirmed in both directions |
| 14262 | 673 | PSP | 673 | 1426204 | 673 | PSP | 673 | 1426204 | Confirmed in both directions |
| 14307 | 1,098 | PVD | 1,098 | 1430702 | 1,098 | PVD | 1,098 | 1430702 | Confirmed in both directions |
| 14321 | 477 | PWM | 477 | 1432103 | 479 | PWM | 479 | 1432103 | Confirmed in both directions |
| 14457 | 236 | RAP | 236 | 1445702 | 236 | RAP | 236 | 1445702 | Confirmed in both directions |
| 14487 | 62 | RDD | 62 | 1448702 | 62 | RDD | 62 | 1448702 | Confirmed in both directions |
| 14489 | 200 | RDM | 200 | 1448902 | 200 | RDM | 200 | 1448902 | Confirmed in both directions |
| 14492 | 3,002 | RDU | 3,002 | 1449202 | 2,999 | RDU | 2,999 | 1449202 | Confirmed in both directions |
| 14520 | 88 | RHI | 88 | 1452002 | 89 | RHI | 89 | 1452002 | Confirmed in both directions |
| 14524 | 1,647 | RIC | 1,647 | 1452401 | 1,647 | RIC | 1,647 | 1452401 | Confirmed in both directions |
| 14543 | 57 | RKS | 57 | 1454302 | 57 | RKS | 57 | 1454302 | Confirmed in both directions |
| 14570 | 1,144 | RNO | 1,144 | 1457002 | 1,144 | RNO | 1,144 | 1457002 | Confirmed in both directions |
| 14574 | 223 | ROA | 223 | 1457402 | 223 | ROA | 223 | 1457402 | Confirmed in both directions |
| 14576 | 737 | ROC | 737 | 1457604 | 738 | ROC | 738 | 1457604 | Confirmed in both directions |
| 14588 | 92 | ROW | 92 | 1458801 | 92 | ROW | 92 | 1458801 | Confirmed in both directions |
| 14633 | 185 | RST | 185 | 1463303 | 185 | RST | 185 | 1463303 | Confirmed in both directions |
| 14635 | 1,766 | RSW | 1,766 | 1463502 | 1,778 | RSW | 1,778 | 1463502 | Confirmed in both directions |
| 14674 | 93 | SAF | 93 | 1467402 | 93 | SAF | 93 | 1467402 | Confirmed in both directions |
| 14679 | 6,209 | SAN | 6,209 | 1467903 | 6,207 | SAN | 6,207 | 1467903 | Confirmed in both directions |
| 14683 | 2,624 | SAT | 2,624 | 1468303 | 2,626 | SAT | 2,626 | 1468303 | Confirmed in both directions |
| 14685 | 661 | SAV | 661 | 1468502 | 661 | SAV | 661 | 1468502 | Confirmed in both directions |
| 14689 | 565 | SBA | 565 | 1468902 | 564 | SBA | 564 | 1468902 | Confirmed in both directions |
| 14696 | 415 | SBN | 415 | 1469606 | 416 | SBN | 416 | 1469606 | Confirmed in both directions |
| 14698 | 250 | SBP | 250 | 1469802 | 249 | SBP | 249 | 1469802 | Confirmed in both directions |
| 14709 | 81 | SCC | 81 | 1470903 | 81 | SCC | 81 | 1470903 | Confirmed in both directions |
| 14711 | 62 | SCE | 62 | 1471102 | 62 | SCE | 62 | 1471102 | Confirmed in both directions |
| 14730 | 843 | SDF | 843 | 1473003 | 844 | SDF | 844 | 1473003 | Confirmed in both directions |
| 14747 | 10,388 | SEA | 10,388 | 1474703 | 10,385 | SEA | 10,385 | 1474703 | Confirmed in both directions |
| 14771 | 14,170 | SFO | 14,170 | 1477102 | 14,170 | SFO | 14,170 | 1477102 | Confirmed in both directions |
| 14783 | 531 | SGF | 531 | 1478302 | 529 | SGF | 529 | 1478302 | Confirmed in both directions |
| 14794 | 203 | SGU | 203 | 1479402 | 203 | SGU | 203 | 1479402 | Confirmed in both directions |
| 14814 | 556 | SHV | 556 | 1481402 | 555 | SHV | 555 | 1481402 | Confirmed in both directions |
| 14828 | 93 | SIT | 93 | 1482803 | 93 | SIT | 93 | 1482803 | Confirmed in both directions |
| 14831 | 3,481 | SJC | 3,481 | 1483103 | 3,482 | SJC | 3,482 | 1483103 | Confirmed in both directions |
| 14842 | 149 | SJT | 149 | 1484202 | 148 | SJT | 148 | 1484202 | Confirmed in both directions |
| 14843 | 1,868 | SJU | 1,868 | 1484304 | 1,876 | SJU | 1,876 | 1484304 | Confirmed in both directions |
| 14869 | 8,763 | SLC | 8,763 | 1486903 | 8,764 | SLC | 8,764 | 1486903 | Confirmed in both directions |
| 14893 | 3,618 | SMF | 3,618 | 1489302 | 3,618 | SMF | 3,618 | 1489302 | Confirmed in both directions |
| 14905 | 62 | SMX | 62 | 1490503 | 62 | SMX | 62 | 1490503 | Confirmed in both directions |
| 14908 | 3,542 | SNA | 3,542 | 1490803 | 3,538 | SNA | 3,538 | 1490803 | Confirmed in both directions |
| 14952 | 150 | SPI | 150 | 1495203 | 150 | SPI | 150 | 1495203 | Confirmed in both directions |
| 14960 | 122 | SPS | 122 | 1496002 | 122 | SPS | 122 | 1496002 | Confirmed in both directions |
| 14986 | 305 | SRQ | 305 | 1498603 | 306 | SRQ | 306 | 1498603 | Confirmed in both directions |
| 15016 | 4,314 | STL | 4,314 | 1501603 | 4,310 | STL | 4,310 | 1501603 | Confirmed in both directions |
| 15024 | 237 | STT | 237 | 1502403 | 237 | STT | 237 | 1502403 | Confirmed in both directions |
| 15027 | 68 | STX | 68 | 1502704 | 69 | STX | 69 | 1502704 | Confirmed in both directions |
| 15041 | 62 | SUN | 62 | 1504102 | 62 | SUN | 62 | 1504102 | Confirmed in both directions |
| 15048 | 57 | SUX | 57 | 1504803 | 57 | SUX | 57 | 1504803 | Confirmed in both directions |
| 15070 | 62 | SWF | 62 | 1507002 | 62 | SWF | 62 | 1507002 | Confirmed in both directions |
| 15096 | 640 | SYR | 640 | 1509602 | 639 | SYR | 639 | 1509602 | Confirmed in both directions |
| 15249 | 279 | TLH | 279 | 1524904 | 279 | TLH | 279 | 1524904 | Confirmed in both directions |
| 15295 | 88 | TOL | 88 | 1529502 | 88 | TOL | 88 | 1529502 | Confirmed in both directions |
| 15304 | 5,143 | TPA | 5,143 | 1530402 | 5,148 | TPA | 5,148 | 1530402 | Confirmed in both directions |
| 15323 | 159 | TRI | 159 | 1532302 | 159 | TRI | 159 | 1532302 | Confirmed in both directions |
| 15356 | 277 | TTN | 277 | 1535602 | 277 | TTN | 277 | 1535602 | Confirmed in both directions |
| 15370 | 1,319 | TUL | 1,319 | 1537002 | 1,318 | TUL | 1,318 | 1537002 | Confirmed in both directions |
| 15376 | 1,311 | TUS | 1,311 | 1537602 | 1,313 | TUS | 1,313 | 1537602 | Confirmed in both directions |
| 15380 | 208 | TVC | 208 | 1538003 | 208 | TVC | 208 | 1538003 | Confirmed in both directions |
| 15389 | 87 | TWF | 87 | 1538902 | 87 | TWF | 87 | 1538902 | Confirmed in both directions |
| 15401 | 88 | TXK | 88 | 1540103 | 88 | TXK | 88 | 1540103 | Confirmed in both directions |
| 15411 | 227 | TYR | 227 | 1541103 | 227 | TYR | 227 | 1541103 | Confirmed in both directions |
| 15412 | 629 | TYS | 629 | 1541203 | 629 | TYS | 629 | 1541203 | Confirmed in both directions |
| 15497 | 14 | UST | 14 | 1549703 | 14 | UST | 14 | 1549703 | Confirmed in both directions |
| 15607 | 88 | VLD | 88 | 1560702 | 88 | VLD | 88 | 1560702 | Confirmed in both directions |
| 15624 | 415 | VPS | 415 | 1562402 | 416 | VPS | 416 | 1562402 | Confirmed in both directions |
| 15841 | 62 | WRG | 62 | 1584102 | 62 | WRG | 62 | 1584102 | Confirmed in both directions |
| 15919 | 941 | XNA | 941 | 1591902 | 940 | XNA | 940 | 1591902 | Confirmed in both directions |
| 15991 | 62 | YAK | 62 | 1599102 | 62 | YAK | 62 | 1599102 | Confirmed in both directions |
| 16218 | 177 | YUM | 177 | 1621801 | 177 | YUM | 177 | 1621801 | Confirmed in both directions |

## Root-cause and reconciliation assessment

The local airport lookup has `iata_code` values but no DOT airport-ID or sequence-ID columns. It could not independently validate the numeric IDs. The official BTS file supplies the authoritative ID-to-code pairings. The local October source’s numeric columns align exactly to the BTS airport-ID fields, while the local database’s raw destination column remains numeric and its origin column has ten prior substitutions; the official data confirms those ten target codes.

The Sprint 3 hypothesis that the values were likely DOT/BTS Airport IDs is now confirmed for this October flight population. The evidence does not establish why the source CSV used AirportID values in its `ORIGIN_AIRPORT`/`DESTINATION_AIRPORT` columns only in October, nor who applied the ten origin changes. It does establish that the correction logic’s ten mappings are correct for the October 2015 BTS snapshot.

## Recommended next implementation step

A separate implementation sprint can now use this official October crosswalk, but should preserve the original numeric columns and retain source/version metadata. Apply the verified mapping to both origin and destination through a small explicit crosswalk layer; keep the mapping scoped to the source identifier system and October 2015 snapshot. Validate unique mapping keys, unchanged row counts (486,165 October rows), no join multiplication, and 100% endpoint coverage before allowing airport/route joins. Do not silently discard unresolved values if future data differs from this snapshot.

## Tests performed and limitations

**Performed:** downloaded the official ZIP; verified archive size and SHA-256; inspected ZIP contents, CSV headers, required fields, row count and FlightDate range; compared all 307 IDs separately by origin and destination; compared per-ID frequencies and ID/code/sequence cardinality; validated the ten SQL candidates; compared full flight-key multisets (with and without tail number) between the official BTS file and local October CSV; checked official codes against the local airport reference; reviewed existing SQL statically.

**Limitations:** the comparison is scoped to October 2015 and the supplied local CSV/database snapshot. No changes were applied. A mapping valid for this month should not be generalized to other years or future data without checking the source identifier/version and effective sequence.

## Final verdict

**Sprint 4 investigation: PASS.** All 307 numeric IDs are validated against the official October 2015 BTS file, with no ambiguous or unresolved mappings in this snapshot. This PASS means the investigation is complete; it does not mean reconciliation has been implemented. No corrections were made.
