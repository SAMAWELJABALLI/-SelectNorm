# Example provenance and reuse status (ACIIDS 2027, Table 4)

All values come from `results/qualitative/examples_mE5.json` (mE5 encoder, primary Arabic-script regime, lambda = 0, SelectNorm-adapt). Labels, p0, p1 and the per-seed predictions were re-checked against `results/export/per_example`; normalised outputs were re-checked by re-running T_cons. `src_id` is the first 12 hex digits of the md5 of the source sentence, as used in the archived exports.

Privacy check: each quoted sentence was read in full; none contains a username, @-mention, URL, phone number, personal name of a private individual or other personal identifier. *Maroc* (a country) is the only proper noun. Full sentences rather than excerpts are shown because predictions are made at sentence level; all quoted sentences are 5-12 tokens.

MYC carries no licence and consists of YouTube comments, so quotation eligibility is uncertain: following condition 7 of the brief, its text and normalised output are not reproduced in the submission; the table gives the corpus row, the phenomenon and the archived predictions. The MYC text is kept only in the private JSON next to this file for the authors' verification and must not be redistributed.

| Paper ID | Internal ID | src_id | Corpus location | Commit | Licence | Reuse status | Effect | Phenomenon | gold y | p0 | p1 | g (seeds 0-4) | yhat (seeds 0-4) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TSAC 796 | S3_tsac_lat:1091 | d906da9a0b95 | test file, line 796 | github.com/fbougares/TSAC @3995e70 | LGPL-3.0 | verbatim quoted | help | negator *mech* mapped by fixed list; French *role* protected | 0 | 0.565 | 0.127 | 11111 | 00000 |
| TSAC 86 | S3_tsac_lat:40 | 0e83d233515d | test file, line 86 | github.com/fbougares/TSAC @3995e70 | LGPL-3.0 | verbatim quoted | harm | *ijale4*, *la5er* fall back to character rules | 1 | 0.806 | 0.004 | 11111 | 00000 |
| NArabizi 2 | S5_narabizi:240 | 8aca8ea1a08d | UD sent_id 2 | UD_Maghrebi_Arabic_French-Arabizi @89fddb4 | CC BY-SA 4.0 (text); sentiment label from Touileb et al. repository, no licence stated | verbatim quoted (text only) | help | French article *le* read as Arabizi and mapped to لا | 1 | 0.175 | 0.842 | 11111 | 11111 |
| NArabizi 4609 | S5_narabizi:298 | 661746dc3aec | UD sent_id 4609 | UD_Maghrebi_Arabic_French-Arabizi @89fddb4 | CC BY-SA 4.0 (text); sentiment label from Touileb et al. repository, no licence stated | verbatim quoted (text only) | harm | *le* mapped to لا; *Maroc* protected | 1 | 0.519 | 0.088 | 11111 | 00000 |
| MYC 9079 | S6_myc_lat:1359 | 12aa67112d9c | DATA_CLEANED.csv row 9079 | github.com/MouadJb/MYC @645d51a | no licence; YouTube comments | WITHHELD (text and normalised output) | harm (seeds 2-4) | two ma...ch negations split as ما...ش; letter elongations squeezed; emoji kept | 1 | 0.645 | 0.250 | 00111 | 11000 |
| MYC 14543 | S6_myc_lat:2738 | 4f3a38718e2e | DATA_CLEANED.csv row 14543 | github.com/MouadJb/MYC @645d51a | no licence; YouTube comments | WITHHELD (text and normalised output) | both views wrong | two Latin-script loanwords protected; negated verb split; emoji kept | 1 | 0.480 | 0.302 | 00001 | 00000 |
| MYC 10259 | S6_myc_lat:1703 | 5106aa2aa8aa | DATA_CLEANED.csv row 10259 | github.com/MouadJb/MYC @645d51a | no licence; YouTube comments | WITHHELD; spare, not in paper | - | - | 1 | 0.458 | 0.530 | 11111 | 11111 |

Text shown in the paper (TSAC and NArabizi only; the NArabizi source uses a typographic apostrophe in *d’or*):

- TSAC 796: `mech 5arej 3lik el role` -> `مش خارج عليك ال role`
- TSAC 86: `Metrobi mouch kif ijale4 la5er` -> `متربي موش كيف يجلذ لخر`
- NArabizi 2: `salem 3alikoum inchalah le pondium et les midailes d’or` -> `سلام عليكوم ان شاء الله لا بنديوم ات لس ميديلس د ’ اور`
- NArabizi 4609: `oui le Maroc aktar jahiziya li had tasfiyat la 3ala lmostawa tandimi` -> `وي لا Maroc اكتر جهيزييا اللي حد تسفييت لا علي لمستوا تنديمي`

Residual issues:

- NArabizi sentiment labels come from the Touileb et al. repository, which states no licence. Only the UD text (CC BY-SA 4.0) is quoted; the label is reported as a fact about the archived evaluation. Authors should confirm this reading before submission.
- CC BY-SA 4.0 requires attribution and indication of changes: the paper names the UD release and its licence in the Code and Reproducibility paragraph, and the normalised outputs are marked as model output.
- LGPL-3.0 (TSAC) is a software licence applied to the data repository; short quotation with attribution is consistent with it, but authors may wish to inform the corpus authors.
- The examples were hand-picked and are not representative; the paper says so.
