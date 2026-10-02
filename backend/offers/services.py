"""Offer decoder + red-flag detector. Informational only; never invents salary data."""
from matching.services.utils import format_inr

DISCLAIMER = ("Informational only, not legal or financial advice. Read your offer letter and agreement "
              "carefully and ask the company to clarify anything unclear.")


def decode_offer(ctc_total, fixed=None, variable=None, joining_bonus=None, other=None, assumed_variable_percent=None):
    comps, notes = [], []
    known = {"Fixed salary": fixed, "Variable pay": variable, "Joining bonus": joining_bonus, "Other components": other}
    for name, amt in known.items():
        if amt is not None:
            comps.append({"name": name, "amount": float(amt), "formatted": format_inr(amt), "kind": "actual"})
    known_sum = sum(c["amount"] for c in comps)
    if ctc_total is None:
        notes.append("Total CTC was not provided.")
    elif comps:
        rest = float(ctc_total) - known_sum
        if rest < 0:
            notes.append("The listed components add up to more than the total CTC. Please re-check the numbers.")
        elif rest > 0:
            comps.append({"name": "Not itemised in the data", "amount": rest, "formatted": format_inr(rest), "kind": "undisclosed"})
            notes.append("Part of the CTC is not itemised in the source data. Ask the company what it includes.")
    elif assumed_variable_percent is not None:
        pct = float(assumed_variable_percent)
        var_est = float(ctc_total) * pct / 100
        comps = [{"name": "Fixed salary (ESTIMATE)", "amount": float(ctc_total) - var_est,
                  "formatted": format_inr(float(ctc_total) - var_est), "kind": "estimate"},
                 {"name": "Variable pay (ESTIMATE)", "amount": var_est, "formatted": format_inr(var_est), "kind": "estimate"}]
        notes.append(f"These are ESTIMATES using your assumption of {pct:g}% variable pay, not real offer data.")
    else:
        notes.append("No component breakdown is available. DriveIQ will not guess one; "
                     "you can test an assumption by supplying assumed_variable_percent.")
    return {"total_ctc": float(ctc_total) if ctc_total is not None else None, "total_formatted": format_inr(ctc_total),
            "components": comps, "notes": notes, "disclaimer": DISCLAIMER}


def detect_red_flags(drive):
    flags, unspecified = [], []

    def flag(sev, title, detail):
        flags.append({"severity": sev, "title": title, "detail": detail})

    if drive.bond_years is None:
        unspecified.append("Service bond")
    elif drive.bond_years > 0:
        pen = f" Penalty: {format_inr(drive.bond_penalty)}." if drive.bond_penalty is not None else " Penalty amount not specified."
        flag("warning", "Service bond detected", f"Bond duration: {drive.bond_years:g} year(s).{pen} Review the agreement carefully before accepting.")
    if drive.ctc_total and drive.ctc_variable:
        share = float(drive.ctc_variable) / float(drive.ctc_total) * 100
        if share >= 15:
            flag("warning", "Significant variable pay", f"Variable pay is about {share:.0f}% of total CTC ({format_inr(drive.ctc_variable)}) and may not be guaranteed.")
        else:
            flag("info", "Variable pay present", f"Variable pay is about {share:.0f}% of total CTC.")
    elif drive.ctc_total and drive.ctc_fixed is None:
        flag("info", "Compensation components unclear", "Total CTC is given but fixed vs variable split is not specified.")
    if drive.joining_bonus:
        flag("info", "Joining bonus", f"{format_inr(drive.joining_bonus)}. Check whether it is repayable if you leave early.")
    if drive.training_agreement:
        flag("warning", "Training agreement", "A training agreement applies. Check duration, stipend and exit terms.")
    if drive.relocation_required:
        flag("info", "Relocation required", "Relocation is mentioned. Check whether costs are covered.")
    if drive.notice_period_days is None:
        unspecified.append("Notice period")
    elif drive.notice_period_days > 0:
        flag("info", "Notice period", f"{drive.notice_period_days} day(s).")
    if drive.probation_months:
        flag("info", "Probation", f"{drive.probation_months} month(s) probation.")
    return {"flags": flags, "not_specified": unspecified, "disclaimer": DISCLAIMER}
