import React from "react";
import PropTypes from "prop-types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { Box } from "@mui/material";

const ChatMessageBox = ({ message }) => {

  if (message.kind === "system_info") {
    return (
      <Box
        sx={{
          alignSelf: "lef",
          bgcolor: "#f0f0f0",
          color: "black",
          p: 1,
          borderRadius: 2,
          mb: 1,
          maxWidth: "80%",
          wordBreak: "break-word",
          textAlign: "left",
          fontStyle: "italic",
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
        >
          {message.text}
        </ReactMarkdown>
      </Box>
    );
  }


  return (
    <Box
      sx={{
        alignSelf: message.sender === "user" ? "flex-end" : "flex-start",
        bgcolor: message.sender === "user" ? "primary.main" : "#e5e5ea",
        color: message.sender === "user" ? "white" : "black",
        p: 1,
        borderRadius: 2,
        mb: 1,
        maxWidth: "80%",
        wordBreak: "break-word",
        textAlign: "left",
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
      >
        {message.text}
      </ReactMarkdown>
    </Box>
  );
};

ChatMessageBox.propTypes = {
  message: PropTypes.shape({
    sender: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
  }).isRequired,
};

export default ChatMessageBox;
