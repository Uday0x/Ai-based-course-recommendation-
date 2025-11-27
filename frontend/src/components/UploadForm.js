import React, { useState } from "react";
import axios from "axios";

const apiBase = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function UploadForm() {
  const [file, setFile] = useState(null);
  const [preprocess, setPreprocess] = useState("none");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);
    fd.append("preprocess", preprocess);
    try {
      const resp = await axios.post(`${apiBase}/extract`, fd, {
        headers: { "Content-Type": "multipart/form-data" }
      });
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
          Image file:
          <input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} />
        </label>
        <label>
          Preprocessing:
          <select value={preprocess} onChange={e => setPreprocess(e.target.value)}>
            <option value="none">None</option>
            <option value="grayscale">Grayscale</option>
            <option value="binarize">Binarize (Otsu)</option>
            <option value="denoise">Denoise (median)</option>
          </select>
        </label>
        <button type="submit" disabled={loading || !file}>{loading ? "Processing..." : "Upload & Extract"}</button>
      </form>

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>Result</h3>
          {result.error ? (
            <pre style={{ color: "red" }}>{JSON.stringify(result, null, 2)}</pre>
          ) : (
            <div>
              <h4>Full Text</h4>
              <pre style={{ whiteSpace: "pre-wrap" }}>{result.text}</pre>
              <h4>Words</h4>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr><th style={{textAlign:"left"}}>Text</th><th>Left</th><th>Top</th><th>W</th><th>H</th><th>Conf</th></tr>
                </thead>
                <tbody>
                  {result.words.map((w, i) => (
                    <tr key={i}>
                      <td>{w.text}</td>
                      <td>{w.left}</td>
                      <td>{w.top}</td>
                      <td>{w.width}</td>
                      <td>{w.height}</td>
                      <td>{w.conf}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}