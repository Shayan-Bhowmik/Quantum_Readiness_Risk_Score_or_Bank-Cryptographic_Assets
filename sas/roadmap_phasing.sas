/********************************************************************************
 * SAS Viya for Learners - Banking Track: Migration Roadmap Phasing Logic
 * File: sas/roadmap_phasing.sas
 *
 * Description:
 *   1. Categorizes scored crypto assets into migration phases:
 *        - Phase 1: risk_score >= 70 (Immediate/High priority remediation)
 *        - Phase 2: 40 <= risk_score < 70 (Mid-term migration runway)
 *        - Phase 3: risk_score < 40 (Long-term / low risk transition)
 *   2. Merges legacy algorithm specifications with the official NIST PQC
 *      mapping dataset to attach recommended post-quantum replacements.
 ********************************************************************************/

/* 1. Import Scored Assets and NIST PQC Mapping Table into WORK library */
proc import datafile="&SCORED_ASSETS_PATH"
    out=work.scored_assets
    dbms=csv
    replace;
    getnames=yes;
run;

proc import datafile="&PQC_MAPPING_PATH"
    out=work.pqc_mapping
    dbms=csv
    replace;
    getnames=yes;
run;

/* 2. Format legacy key key for joining (e.g., 'RSA-2048') */
data work.scored_assets_prep;
    set work.scored_assets;
    length lookup_key $ 64;
    lookup_key = upcase(strip(algorithm)) || '-' || strip(put(key_size_bits, 8.));
run;

data work.pqc_mapping_prep;
    set work.pqc_mapping;
    length lookup_key $ 64;
    lookup_key = upcase(strip(legacy_algorithm));
run;

/* 3. Join with PQC Mapping Table and assign deterministic Phase */
proc sql;
    create table work.phased_roadmap as
    select 
        a.asset_id,
        a.asset_name,
        a.system_category,
        a.algorithm,
        a.key_size_bits,
        a.data_sensitivity,
        a.estimated_years_to_break,
        a.migration_cost_score,
        a.risk_score,
        case 
            when a.risk_score >= 70.0 then 'Phase 1'
            when a.risk_score >= 40.0 then 'Phase 2'
            else 'Phase 3'
        end as migration_phase length=8,
        case 
            when m.recommended_pqc_algorithm is not missing then m.recommended_pqc_algorithm
            when upcase(a.algorithm) = 'RSA' then 'CRYSTALS-Dilithium (ML-DSA)'
            when upcase(a.algorithm) in ('ECC', 'DIFFIE-HELLMAN') then 'CRYSTALS-Kyber (ML-KEM)'
            when upcase(a.algorithm) = 'AES' then 'AES-256'
            else 'NIST Standardized PQC Target'
        end as recommended_pqc_algorithm length=40,
        m.standard_reference,
        m.notes as pqc_compliance_notes,
        a.created_at,
        a.updated_at
    from work.scored_assets_prep as a
    left join work.pqc_mapping_prep as m
        on a.lookup_key = m.lookup_key
    order by a.risk_score desc;
quit;

/* 4. Executive Phase Distribution Summary */
title "Migration Roadmap Phasing - Asset Count & Average Risk by Phase";
proc freq data=work.phased_roadmap;
    tables migration_phase / nocum;
run;

proc means data=work.phased_roadmap mean min max maxdec=1;
    class migration_phase;
    var risk_score estimated_years_to_break migration_cost_score;
run;
title;
