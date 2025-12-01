// frontend/src/components/InterestForm.jsx
import React, { useState } from "react";
import axios from "axios";
import ExplanationBox from "./ExplanationBox";

function PercentBar({ value }) {
  // value: 0..1
  const pct = Math.max(0, Math.min(1, Number(value || 0)));
  const pctDisplay = (pct * 100).toFixed(1) + "%";
  return (
    <div style={{ marginTop: 6 }}>
      <div style={{
        height: 14,
        background: "#eee",
        borderRadius: 8,
        overflow: "hidden",
      }}>
        <div style={{
          width: `${pct * 100}%`,
          height: "100%",
          background: pct >= 0.5 ? "#16a34a" : (pct >= 0.25 ? "#f59e0b" : "#ef4444"),
          transition: "width .35s ease"
        }} />
      </div>
      <div style={{ marginTop: 6, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: 13, color: "#444" }}>Confidence</div>
        <div style={{ fontWeight: 700, color: "#111" }}>{pctDisplay}</div>
      </div>
    </div>
  );
}

export default function InterestForm() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Uses CRA proxy if set; otherwise change to full URL
      const resp = await axios.post("/predict", { interests: input });
      setResult(resp.data);
    } catch (err) {
      if (err.response?.data) setError(err.response.data);
      else setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ marginBottom: 18 }}>
        <label style={{ fontWeight: 700 }}>Interests (comma-separated):</label>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. python, ml, nlp"
          style={{
            width: "100%",
            padding: "10px 12px",
            marginTop: 8,
            marginBottom: 10,
            borderRadius: 6,
            border: "1px solid #cbd5e1",
            boxSizing: "border-box",
            fontSize: 15
          }}
        />
        <div>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "10px 16px",
              background: "#111827",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              cursor: loading ? "default" : "pointer",
              boxShadow: "0 2px 6px rgba(0,0,0,0.08)"
            }}
          >
            {loading ? "Thinking..." : "Get Recommendation"}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ color: "darkred", marginBottom: 12 }}>
          <strong>Error:</strong>{" "}
          <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>
            {typeof error === "string" ? error : JSON.stringify(error, null, 2)}
          </pre>
        </div>
      )}

      {result && (
        <div>
          <h2 style={{ marginTop: 6 }}>Recommendation</h2>

          {/* Highlighted Course Card */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginBottom: 14
          }}>
            <div style={{
              flex: "0 0 auto",
              padding: "12px 18px",
              borderRadius: 12,
              background: "linear-gradient(180deg,#ffffff,#f8fafc)",
              boxShadow: "0 6px 18px rgba(2,6,23,0.06)",
              border: "1px solid rgba(2,6,23,0.06)",
              minWidth: 260
            }}>
              <div style={{ fontSize: 13, color: "#334155", fontWeight: 700, marginBottom: 6 }}>Course</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: "#0f172a" }}>{result.recommended_course}</div>
            </div>

            {/* Confidence badge + percent bar */}
            <div style={{ flex: 1, minWidth: 300 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ fontSize: 13, color: "#334155", fontWeight: 700 }}>Confidence</div>
                {/* numeric badge */}
                <div style={{
                  background: "linear-gradient(180deg,#f8fafc,#ffffff)",
                  padding: "6px 10px",
                  borderRadius: 10,
                  border: "1px solid rgba(2,6,23,0.06)",
                  fontWeight: 800,
                  color: "#0f172a"
                }}>
                  {(result.probability * 100).toFixed(2)}%
                </div>
              </div>

              {/* visual percent bar */}
              <div style={{ marginTop: 8 }}>
                <PercentBar value={result.probability} />
              </div>
            </div>
          </div>

          {/* Explanation heading */}
          <div style={{ fontWeight: 700, marginBottom: 8 }}>
            {/* Explanation ({result.explanation?.method || "—"}) */}
          </div>

          <ExplanationBox explanation={result.explanation} />
        </div>
      )}
    </div>
  );
}
