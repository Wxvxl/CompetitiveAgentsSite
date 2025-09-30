"use client";
import AgentUploadForm from "../forms/AgentUploadForm";
import AgentList from "./AgentList";

export default function StudentAgentPanel() {
  return (
    <section>
      <h3>Upload Your Agent</h3>
      <AgentUploadForm />
      <div style={{ marginTop: 16 }}>
        <h3>Your Uploaded Agents</h3>
        <AgentList scope="mine" />
      </div>
    </section>
  );
}
