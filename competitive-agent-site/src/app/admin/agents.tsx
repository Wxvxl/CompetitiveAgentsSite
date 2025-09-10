"use client";
import { useEffect, useState } from "react";

type Agent = {
  id: number;
  filename: string;
  uploader: string;
  upload_time: string;
};

export default function AgentListPage() {
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/agents", { credentials: "include" })
      .then((res) => res.json())
      .then(setAgents);
  }, []);

  return (
    <section>
      <h2>All Uploaded Agents</h2>
      <table>
        <thead>
          <tr>
            <th>Filename</th>
            <th>Uploader</th>
            <th>Upload Time</th>
          </tr>
        </thead>
        <tbody>
          {agents.map((agent) => (
            <tr key={agent.id}>
              <td>{agent.filename}</td>
              <td>{agent.uploader}</td>
              <td>{agent.upload_time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
