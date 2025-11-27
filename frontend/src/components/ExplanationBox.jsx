import React from "react";

/**
 * ExplanationBox
 * props:
 *  - explanation: {
 *      method: string,
 *      top_contributing_tokens: { token: number, ... }
 *    }
 */
function formatNumber(n) {
  if (Math.abs(n) >= 1) return n.toFixed(3);
  return n.toFixed(4);
}

export default function ExplanationBox({ explanation }) {
  if (!explanation) return null;

  const tokensObj = explanation.top_contributing_tokens || {};
  const tokens = Object.entries(tokensObj);

  if (tokens.length === 0) {
    return (
      <div style={{ fontStyle: "italic", color: "#666" }}>
        No explanation available.
      </div>
    );
  }

  tokens.sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
  const maxAbs = Math.max(...tokens.map(([, v]) => Math.abs(v)), 1);

  return (
    <div style={{ fontFamily: "system-ui, Arial, sans-serif", maxWidth: 700 }}>
      <div style={{ marginBottom: 10, color: "#222", fontWeight: 700, fontSize: 16 }}>
        Explanation ({explanation.method || "unknown"})
      </div>

      <div style={{ display: "grid", gap: 10 }}>
        {tokens.map(([token, val]) => {
          const abs = Math.abs(val);
          const widthPct = Math.min((abs / maxAbs) * 100, 100);
          const positive = val > 0;
          return (
            <div key={token} style={{ display: "flex", alignItems: "center" }}>
              <div style={{ width: 140, fontWeight: 700 }}>{token}</div>

              <div
                style={{
                  height: 16,
                  background: "#f0f0f0",
                  borderRadius: 8,
                  overflow: "hidden",
                  flex: 1,
                  marginRight: 12,
                }}
                aria-hidden
              >
                <div
                  style={{
                    width: `${widthPct}%`,
                    height: "100%",
                    background: positive ? "#16a34a" : "#ef4444",
                    transition: "width .25s ease",
                  }}
                />
              </div>

              <div style={{ width: 90, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>
                <span style={{ color: positive ? "#166534" : "#9f1239", fontWeight: 700 }}>
                  {positive ? "+" : "−"}
                </span>{" "}
                {formatNumber(val)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
