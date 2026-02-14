import { useState, useRef, useEffect } from "react";


export function to_markdown_table(results_str) {
  let table_md = ""; 

  try {
    const rows = results_str
      .substring(1, results_str.length - 1)
      .split("), (")
      .map(r => r.replace(/^\(/, "").replace(/\)$/, "").split(", "));

    if (rows.length > 0) {
      // header
      table_md += "| " + rows[0].map((_, i) => `Col${i + 1}`).join(" | ") + " |\n";
      table_md += "| " + rows[0].map(() => "---").join(" | ") + " |\n";

      // data rows
      rows.forEach(row => {
        table_md += "| " + row.join(" | ") + " |\n";
      });
    }
  } catch (e) {
    table_md = results_str;
  }

  return table_md;
}

const DEFAULT_MODEL = "qooba/qwen3-coder-30b-a3b-instruct:q3_k_m";

export function useChatStream() {
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState("");

  const sendMessage = async ({ classificationModel, generationModel } = {}) => {
    if (!input.trim()) return;

    const selectedGenerationModel = (generationModel || "").trim() || DEFAULT_MODEL;
    const selectedClassificationModel = (classificationModel || "").trim() || selectedGenerationModel;

    setMessages(prev => [...prev, { sender: "user", text: input }]);
    setMessages(prev => [...prev, { sender: "bot", text: "" }]);

    const response = await fetch("http://192.168.1.120:9000/orchestrate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: selectedGenerationModel,
        generation_model: selectedGenerationModel,
        classification_model: selectedClassificationModel,
        system: "You are a helpful assistant.",
        prompt: input.trim(),
        stream: true,
        session_id: sessionId,
      }),
    });

    console.log("Session ID:", sessionId);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;


      buffer += decoder.decode(value, { stream: true });

      let idx;
      while ((idx = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, idx).trim();
        buffer = buffer.slice(idx + 1);

        if (!line) continue;

        const json = JSON.parse(line);

        if (json.session_id && !sessionId) {
          setSessionId(json.session_id);
          continue;
        }

        if (json.delta) {
          //{"type": "model_token", "timestamp": 1768675249.0428748, "delta": "{\"delta\": \" registered\"}"}
          //{"type": "model_token", "timestamp": 1768675428.4032488, "delta": "{\"session_id\": \"14071a4f-b066-4437-af95-ceeee041687b\"}"}
          const delta = JSON.parse(json.delta);
          const token = delta.delta;

          //session_id update
          if (delta.session_id && !sessionId) {
            setSessionId(delta.session_id);
          }
          if (token === undefined) continue;

          setMessages(prev => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...updated[updated.length - 1],
              text: updated[updated.length - 1].text + delta.delta,
            };
            return updated;
          });

          //{"type": "status", "timestamp": 1768675718.1897707, "message": "Classifying prompt..."}
          //{"type": "classification", "timestamp": 1768675720.599638, "value": "simple_request"}
          //{"type": "status", "timestamp": 1768675720.5999477, "message": "Generating response..."}


        } else if (json.message) {

          console.log("Status message:", json.message);


        } else if (json.type === "classification") {
          setMessages(prev => {
            const updated = [...prev];
            updated.splice(updated.length - 1, 0, {
              sender: "bot",
              kind: "system_info",
              text: `*Prompt classified as: ${json.value}*`,
            });
            return updated;
          });
        } else if (json.type === "sql_query") {
          setMessages(prev => {
            const updated = [...prev];
            updated.splice(updated.length - 1, 0, {
              sender: "bot",
              kind: "system_info",
              text: `*Generated SQL Query:*\n\`\`\`sql\n${json.query}\n\`\`\``,
            });
            return updated;
          });
        } else if (json.type === "query_results") {
          
          let table_md = ""; 

          table_md = to_markdown_table(json.results);

          setMessages(prev => {
            const updated = [...prev];
            updated.splice(updated.length - 1, 0, {
              sender: "bot",
              kind: "system_info",
              text: `*Query Results:*\n${table_md}`,
            });
            return updated;
          });
        }
      }
    }

    setInput("");
  };

  return { messages, input, setInput, sendMessage };
}
