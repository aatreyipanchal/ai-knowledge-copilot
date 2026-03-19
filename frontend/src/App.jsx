import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Send, 
  Upload, 
  FileText, 
  BarChart3, 
  Image as ImageIcon, 
  Search, 
  MessageSquare, 
  Trash2,
  ChevronRight,
  Loader2,
  Paperclip,
  Activity
} from 'lucide-react';
import './App.css';

const API_BASE = "http://localhost:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(`session_${Math.random().toString(36).substr(2, 9)}`);
  const [activeTab, setActiveTab] = useState("chat");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const chatEndRef = useRef(null);

  // Load history on mount
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${API_BASE}/chat/history/${sessionId}`);
        const history = response.data.map(msg => {
          let extra = {};
          try {
            extra = msg.extra_info ? JSON.parse(msg.extra_info) : {};
          } catch (e) { console.error("History parse error", e); }
          
          return {
            role: msg.role,
            content: msg.content,
            route: extra.route,
            sources: extra.sources,
            charts: extra.charts || (extra.chart ? [extra.chart] : [])
          };
        });
        setMessages(history);
      } catch (err) {
        console.error("Failed to fetch history", err);
      }
    };

    const fetchFiles = async () => {
      try {
        const response = await axios.get(`${API_BASE}/files`);
        const files = response.data.csv_files.map(name => ({
          name,
          type: "text/csv",
          size: "Unknown",
          date: "Previously Uploaded"
        }));
        setUploadedFiles(files);
      } catch (err) {
        console.error("Failed to fetch files", err);
      }
    };

    fetchHistory();
    fetchFiles();
  }, [sessionId]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    let endpoint = "/upload/pdf";
    if (file.name.endsWith(".csv")) endpoint = "/upload/csv";
    else if (file.name.match(/\.(jpg|jpeg|png)$/i)) endpoint = "/upload/image";

    setUploadStatus("Uploading...");
    try {
      await axios.post(`${API_BASE}${endpoint}`, formData);
      setUploadStatus(`Success: ${file.name}`);
      setSelectedFile(file.name);
      
      setUploadedFiles(prev => [...prev, {
        name: file.name,
        type: file.type,
        size: (file.size / 1024).toFixed(2) + " KB",
        date: new Date().toLocaleDateString()
      }]);

      setMessages(prev => [...prev, {
        role: "system",
        content: `Uploaded ${file.name} successfully.`
      }]);
    } catch (err) {
      setUploadStatus("Upload failed");
      console.error(err);
    }
  };

  const handleSend = async () => {
    if (!input.trim() && !selectedFile) return;

    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        question: input,
        session_id: sessionId,
        filename: selectedFile
      });

      const botMessage = {
        role: "assistant",
        content: response.data.answer,
        route: response.data.route,
        sources: response.data.sources,
        charts: response.data.charts || []
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: "assistant", 
        content: "Error: Could not reach the AI gateway. Make sure the backend is running."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="premium-bg" />
      
      {/* Sidebar */}
      <aside className="sidebar glass-card">
        <div className="sidebar-header">
          <Activity className="text-primary" />
          <h1>Knowledge Copilot</h1>
        </div>
        
        <div className="sidebar-section">
          <h2>Upload Documents</h2>
          <label className="upload-zone">
            <input type="file" onChange={handleUpload} hidden />
            <Upload size={20} />
            <span>Click to upload PDF, CSV, or Image</span>
          </label>
          {uploadStatus && <div className="status-text">{uploadStatus}</div>}
        </div>

        <nav className="sidebar-nav">
          <div 
            className={`nav-item ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            <MessageSquare size={18} />
            <span>Chat Assistant</span>
          </div>
          <div 
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <BarChart3 size={18} />
            <span>Data Dashboard</span>
          </div>
          <div 
            className={`nav-item ${activeTab === "library" ? "active" : ""}`}
            onClick={() => setActiveTab("library")}
          >
            <FileText size={18} />
            <span>Library</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <p>Session: {sessionId}</p>
        </div>
      </aside>

      {/* Main Area */}
      <main className="chat-area">
        <header className="chat-header glass-card">
          <div className="header-info">
            <h2>{activeTab === "chat" ? "Specialized AI Agent" : activeTab === "dashboard" ? "Analytics Dashboard" : "Document Library"}</h2>
            <span className="online-tag">Online</span>
          </div>
        </header>

        {activeTab === "chat" && (
          <>
            <div className="messages-container">
              {messages.length === 0 && (
                <div className="welcome-screen">
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="welcome-card"
                  >
                    <h1>How can I help you today?</h1>
                    <p>Upload a document to analyze, a CSV to visualize, or an image to describe.</p>
                    <div className="suggested-actions">
                      <button className="glass-card" onClick={() => setInput("Describe the current market trends from my CSV.")}>
                        Analyze Data
                      </button>
                      <button className="glass-card" onClick={() => setInput("Summarize the key points of the uploaded PDF.")}>
                        Query Documents
                      </button>
                    </div>
                  </motion.div>
                </div>
              )}

              {messages.map((msg, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`message-wrapper ${msg.role}`}
                >
                  <div className={`message glass-card ${msg.role === 'user' ? 'user-msg' : 'bot-msg'}`}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                    {msg.charts && msg.charts.length > 0 && (
                      <div className="charts-wrapper">
                        {msg.charts.map((chart, idx) => (
                          <div key={idx} className="chart-container">
                            <img src={`data:image/png;base64,${chart}`} alt={`Visualization ${idx + 1}`} />
                          </div>
                        ))}
                      </div>
                    )}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources">
                        <span>Sources: {msg.sources.join(", ")}</span>
                      </div>
                    )}
                    {msg.route && <div className="route-tag">{msg.route}</div>}
                  </div>
                </motion.div>
              ))}
              {loading && (
                <div className="message-wrapper assistant">
                  <div className="message bot-msg glass-card loading-msg">
                    <Loader2 className="animate-spin" />
                    <span>Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="input-container glass-card">
              <div className="input-wrapper">
                <Paperclip className="input-icon" />
                <textarea 
                  placeholder="Ask anything..." 
                  value={input}
                  onChange={(e) => {
                    setInput(e.target.value);
                    e.target.style.height = 'auto';
                    e.target.style.height = e.target.scrollHeight + 'px';
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  className="chat-input"
                  rows="1"
                />
                <button className="send-btn" onClick={handleSend} disabled={loading}>
                  <Send size={18} />
                </button>
              </div>
            </div>
          </>
        )}

        {activeTab === "dashboard" && (
          <div className="dashboard-view container-scroll">
            <div className="dashboard-grid">
              {messages.flatMap((m, msgIdx) => 
                (m.charts || []).map((chart, chartIdx) => ({
                  chart,
                  content: m.content,
                  id: `${msgIdx}-${chartIdx}`
                }))
              ).map((item, i) => (
                <motion.div 
                  key={item.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="dashboard-card glass-card"
                >
                   <h3>Visualization {i+1}</h3>
                   <div className="chart-preview">
                     <img src={`data:image/png;base64,${item.chart}`} alt="Chart" />
                   </div>
                   <p className="chart-context">{item.content.substring(0, 100)}...</p>
                </motion.div>
              ))}
              {messages.every(m => !m.charts || m.charts.length === 0) && (
                <div className="empty-state">
                  <BarChart3 size={48} />
                  <p>No visualizations yet. Ask the Data Agent to generate charts!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "library" && (
          <div className="library-view container-scroll">
            <div className="library-list">
              {uploadedFiles.map((file, i) => (
                <div key={i} className="library-item glass-card">
                  <div className="item-info">
                    {file.name.endsWith(".csv") ? <BarChart3 size={24} /> : file.name.match(/\.(jpg|jpeg|png)$/i) ? <ImageIcon size={24} /> : <FileText size={24} />}
                    <div>
                      <h4>{file.name}</h4>
                      <span>{file.size} • {file.date}</span>
                    </div>
                  </div>
                  <button className="btn-icon" onClick={() => {
                    setSelectedFile(file.name);
                    setActiveTab("chat");
                  }}>
                    <ChevronRight size={20} />
                  </button>
                </div>
              ))}
              {uploadedFiles.length === 0 && (
                <div className="empty-state">
                   <FileText size={48} />
                   <p>No files uploaded yet.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
