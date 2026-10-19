/********************************************************************************
 * SAS Viya for Learners - Banking Track: Quantum-Readiness Risk Scoring Engine
 * File: sas/risk_score_engine.sas
 *
 * Description:
 *   Calculates the normalized Quantum Risk Score (0-100) for bank cryptographic
 *   assets based on data sensitivity, quantum time-to-break urgency, and 
 *   migration cost/complexity.
 *
 * Formula:
 *   Raw_Risk = Sensitivity_Weight * (1 / max(estimated_years_to_break, 0.25)) * migration_cost_score
 *   Risk_Score = Min(100.0, Max(0.0, (Raw_Risk / Max_Possible_Raw) * 100.0))
 ********************************************************************************/

/* 1. Import CSV asset inventory into SAS work library */
proc import datafile="&CSV_PATH"
    out=work.crypto_assets_raw
    dbms=csv
    replace;
    getnames=yes;
run;

/* 2. Compute Raw Risk Metric using DATA step */
data work.crypto_assets_scored;
    set work.crypto_assets_raw;

    /* Assign numeric sensitivity weight per security tier */
    length sensitivity_weight 8;
    select (upcase(strip(data_sensitivity)));
        when ('CRITICAL') sensitivity_weight = 4.0;
        when ('HIGH')     sensitivity_weight = 3.0;
        when ('MEDIUM')   sensitivity_weight = 2.0;
        when ('LOW')      sensitivity_weight = 1.0;
        otherwise         sensitivity_weight = 1.0;
    end;

    /* Prevent division-by-zero or extreme spikes with a lower bound threshold */
    safe_years = max(estimated_years_to_break, 0.25);
    time_urgency = 1.0 / safe_years;

    /* Bounded migration cost score (1 to 10 scale) */
    safe_cost = min(max(migration_cost_score, 1.0), 10.0);

    /* Compute raw component score */
    raw_risk = sensitivity_weight * time_urgency * safe_cost;

    /* 
     * Normalization scaling factor:
     * Theoretical maximum raw risk = 4.0 (Critical) * (1 / 0.5 yrs) * 10.0 (Cost) = 80.0
     */
    normalizer = 80.0;
    
    /* Scale to 0-100 and round to 1 decimal place */
    risk_score = round(min(100.0, max(0.0, (raw_risk / normalizer) * 100.0)), 0.1);

    /* Derive Migration Phase based on SAS Risk Score threshold */
    length migration_phase $ 8;
    if risk_score >= 70.0 then migration_phase = 'Phase 1';
    else if risk_score >= 40.0 then migration_phase = 'Phase 2';
    else migration_phase = 'Phase 3';

    drop safe_years time_urgency safe_cost normalizer;
run;

/* 3. Output top 10% highest risk assets for verification */
proc sort data=work.crypto_assets_scored out=work.sorted_risk;
    by descending risk_score;
run;

title "Quantum-Readiness Risk Scoring Engine - Top Critical Assets";
proc print data=work.sorted_risk(obs=10);
    var asset_id asset_name system_category algorithm key_size_bits data_sensitivity estimated_years_to_break risk_score migration_phase;
run;
title;
