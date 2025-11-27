import React from "react";
import InterestForm from "./components/InterestForm";

function App() {
  return (
    <div style={{ maxWidth: 800, margin: "40px auto", fontFamily: "Arial, sans-serif" }}>
      <h1>AI Course Recommender — Demo</h1>
      <p>Enter comma-separated interests and get a recommended AI course.</p>
      <InterestForm />
    </div>
  );
}

export default App;