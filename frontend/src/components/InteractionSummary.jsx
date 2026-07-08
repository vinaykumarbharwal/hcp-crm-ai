import React from "react";
export function InteractionSummary({ draft }) {
  if (!draft) {
    return (
      <aside className="panel muted-panel">
        <h2>Draft Summary</h2>
        <p>Agent output appears here after the field note is analyzed.</p>
      </aside>
    );
  }

  return (
    <aside className="panel">
      <h2>Draft Summary</h2>
      <dl className="summary-list">
        <div><dt>HCP</dt><dd>{draft.hcp_name}</dd></div>
        <div><dt>Product</dt><dd>{draft.product}</dd></div>
        <div><dt>Sentiment</dt><dd>{draft.sentiment}</dd></div>
        <div><dt>Compliance</dt><dd>{draft.compliance_status}</dd></div>
      </dl>

      <h3>Action Items</h3>
      <ul>
        {draft.action_items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>

      <h3>Competitive Intelligence</h3>
      <p>{draft.competitive_intelligence || "No competitor mention found."}</p>
    </aside>
  );
}
