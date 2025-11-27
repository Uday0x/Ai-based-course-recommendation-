// frontend/src/components/InterestForm.jsx
import React, { useState } from "react";
import axios from "axios";
import ExplanationBox from "./ExplanationBox";

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
      // If your frontend uses a proxy, you can call "/predict" (relative).
      // Otherwise use full URL: http://localhost:8000/predict
      const resp = await axios.post("/predict", { interests: input });
      setResult(resp.data);
    } catch (err) {
      // try to present a readable error
      if (err.response?.data) {
        setError(err.response.data);
      } else {
        setError(err.message || "Network error");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ marginBottom: 18 }}>
        <label style={{ fontWeight: 600 }}>Interests (comma-separated):</label>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. python, ml, nlp"
          style={{
            width: "100%",
            padding: "8px 10px",
            marginTop: 6,
            marginBottom: 8,
            borderRadius: 4,
            border: "1px solid #ccc",
            boxSizing: "border-box",
          }}
        />
        <div>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "8px 14px",
              background: "#1f2937",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              cursor: loading ? "default" : "pointer",
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

          <div style={{ marginBottom: 8 }}>
            <div style={{ fontWeight: 700 }}>Course:</div>
            <div style={{ marginTop: 6 }}>{result.recommended_course}</div>
          </div>

          <div style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 700 }}>Confidence:</div>
            <div style={{ marginTop: 6 }}>{(result.probability * 100).toFixed(2)}%</div>
          </div>

          <ExplanationBox explanation={result.explanation} />
        </div>
      )}
    </div>
  );
}
