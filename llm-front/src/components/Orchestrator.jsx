import { useState, useRef, useEffect } from "react";
import { Box, TextField, Button, Paper, FormControl, InputLabel, Select, MenuItem } from "@mui/material";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";
import remarkGfm from "remark-gfm";

import { useChatStream } from "../hooks/useChatStream";
import ChatMessageBox from "./ChatMessageBox";

export default function Orchestrator() {

  const [streaming, setStreaming] = useState(true);
  const [sessionId, setSessionId] = useState("");
  const chatEndRef = useRef(null);

  const modelOptions = [
    "qooba/qwen3-coder-30b-a3b-instruct:q3_k_m",
    "llama3.1:8b",
    "qwen2.5-coder:14b",
    "deepseek-coder:33b",
  ];

  const [generationModel, setGenerationModel] = useState(modelOptions[0]);
  const [classificationModel, setClassificationModel] = useState(modelOptions[0]);

  const {
    messages,
    input,
    setInput,
    sendMessage,
  } = useChatStream();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Box
      sx={{
        width: "100%",
        height: "100%",
        margin: 0,
        display: "flex",
        flexDirection: "column",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <Paper
        elevation={3}
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          padding: 1,
          height: 300,
          overflowY: "auto",
          mb: 1,
        }}
      >
        {messages.map((msg, i) => (
          <ChatMessageBox key={i} message={msg} />
        ))}
        <div ref={chatEndRef} />
      </Paper>

      <Box sx={{ display: "flex", gap: 1, mb: 1, flexWrap: "wrap" }}>
        <FormControl size="small" sx={{ minWidth: 240 }}>
          <InputLabel id="generation-model-label">Modelo generación</InputLabel>
          <Select
            labelId="generation-model-label"
            value={generationModel}
            label="Modelo generación"
            onChange={(e) => setGenerationModel(e.target.value)}
          >
            {modelOptions.map((model) => (
              <MenuItem key={model} value={model}>
                {model}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 240 }}>
          <InputLabel id="classification-model-label">Modelo clasificación</InputLabel>
          <Select
            labelId="classification-model-label"
            value={classificationModel}
            label="Modelo clasificación"
            onChange={(e) => setClassificationModel(e.target.value)}
          >
            {modelOptions.map((model) => (
              <MenuItem key={model} value={model}>
                {model}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Box sx={{ display: "flex", gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) =>
            e.key === "Enter" &&
            sendMessage({
              classificationModel,
              generationModel,
            })
          }
          placeholder="Type a message..."
        />
        <Button
          variant="contained"
          onClick={() =>
            sendMessage({
              classificationModel,
              generationModel,
            })
          }
        >
          Send
        </Button>
      </Box>
    </Box>
  );
}
