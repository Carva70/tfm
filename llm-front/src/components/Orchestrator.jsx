import { useState, useRef, useEffect } from "react";
import { Box, TextField, Button, Paper, FormControl, InputLabel, Select, MenuItem, FormGroup, FormControlLabel, Checkbox } from "@mui/material";
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
    "llama3.1:8b",
  ];

  const [generationModel, setGenerationModel] = useState(modelOptions[0]);
  const [classificationModel, setClassificationModel] = useState(modelOptions[0]);
  const [showClassification, setShowClassification] = useState(true);
  const [showSqlQuery, setShowSqlQuery] = useState(true);
  const [showQueryResults, setShowQueryResults] = useState(true);

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

      <FormGroup row sx={{ mb: 1 }}>
        <FormControlLabel
          sx={{ "& .MuiFormControlLabel-label": { color: "black" } }}
          control={
            <Checkbox
              size="small"
              checked={showClassification}
              onChange={(e) => setShowClassification(e.target.checked)}
            />
          }
          label="Mostrar clasificación"
        />
        <FormControlLabel
          sx={{ "& .MuiFormControlLabel-label": { color: "black" } }}
          control={
            <Checkbox
              size="small"
              checked={showSqlQuery}
              onChange={(e) => setShowSqlQuery(e.target.checked)}
            />
          }
          label="Mostrar SQL"
        />
        <FormControlLabel
          sx={{ "& .MuiFormControlLabel-label": { color: "black" } }}
          control={
            <Checkbox
              size="small"
              checked={showQueryResults}
              onChange={(e) => setShowQueryResults(e.target.checked)}
            />
          }
          label="Mostrar resultados"
        />
      </FormGroup>

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
              showClassification,
              showSqlQuery,
              showQueryResults,
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
              showClassification,
              showSqlQuery,
              showQueryResults,
            })
          }
        >
          Send
        </Button>
      </Box>
    </Box>
  );
}
