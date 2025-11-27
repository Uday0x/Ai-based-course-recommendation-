import React, { useState } from "react";
import axios from "axios";

const apiBase = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function InterestForm() {
  const [interests, setInterests] = useState("python, ml, numpy");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const resp = await axios.post(`${apiBase}/predict`, { interests });
      setResult(resp.data);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={submit} style={{ display: "grid", gap: 8 }}>
        <label>
          Interests (comma-separated):
          <input type="text" value={interests} onChange={e => setInterests(e.target.value)} style={{ width: "100%" }} />
        </label>
        <button type="submit" disabled={loading}>{loading ? "Predicting..." : "Get Recommendation"}</button>
      </form>

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>Recommendation</h3>
          {result.error ? (
            <pre style={{ color: "red" }}>{JSON.stringify(result, null, 2)}</pre>
          ) : (
            <div>
              <p><strong>Course:</strong> {result.recommended_course}</p>
              <p><strong>Confidence:</strong> {result.probability}</p>
              <h4>Explanation</h4>
              <pre>{JSON.stringify(result.explanation, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}