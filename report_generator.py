from datetime import datetime
from langfuse import observe

@observe()
def generate_screening_report(df,jd):
    sim   = df[df["Status"] == "Similar"]
    nosim = df[df["Status"] != "Similar"]
    now   = datetime.now().strftime("%d %B %Y, %I:%M %p")
    top   = df.iloc[0] if len(df) else None

    lines = [
        "=" * 60,
        "       RESUME SCREENING REPORT",
        "=" * 60,
        f"  Date       : {now}",
        "=" * 60,
        "",
        "SUMMARY",
        "-" * 30,
        f"  Total Resumes Screened : {len(df)}",
        f"  Shortlisted (Similar)  : {len(sim)}",
        f"  Not Matching           : {len(nosim)}",
        f"  Average Match Score    : {round(df['Score'].mean(), 2)}%",
        f"  Highest Score          : {df['Score'].max()}%  ({top['Candidate'] if top is not None else 'N/A'})",
        f"  Lowest Score           : {df['Score'].min()}%",
        "",
        "JOB DESCRIPTION (excerpt)",
        "-" * 30,
        f"  {jd[:300].strip()}{'...' if len(jd) > 300 else ''}",
        "",
        "CANDIDATE RANKINGS",
        "-" * 30,
    ]

    for _, row in df.iterrows():
        lines += [
            f"  #{row['Rank']}  {row['Candidate']}",
            f"       File    : {row['File']}",
            f"       Score   : {row['Score']}%   |   Status: {row['Status']}",
            f"       Matched : {row['Matched Skills']}",
            f"       Missing : {row['Missing Skills']}",
            "",
        ]

    lines += [
        "SHORTLISTED CANDIDATES",
        "-" * 30,
    ]
    if len(sim):
        for _, row in sim.iterrows():
            lines.append(f"  ✓  {row['Candidate']} — {row['Score']}%")
    else:
        lines.append("  No candidates shortlisted.")

    lines += [
        "",
        "NOT MATCHING",
        "-" * 30,
    ]
    if len(nosim):
        for _, row in nosim.iterrows():
            lines.append(f"  ✗  {row['Candidate']} — {row['Score']}%")
    else:
        lines.append("  All candidates matched!")

    lines += ["", "=" * 60, "  END OF REPORT", "=" * 60]
    return "\n".join(lines)
