import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Card,
  CardContent,
  TextField,
  Button,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  IconButton
} from '@mui/material';
import { Send as SendIcon, SmartToy as BotIcon, Person as PersonIcon } from '@mui/icons-material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const wsRef = useRef(null);
  const chatContainerRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    // Open a new WebSocket connection for each message
    const ws = new window.WebSocket('ws://localhost:8000/ws/chat');
    wsRef.current = ws;

    let reply = '';
    ws.onopen = () => {
      ws.send(JSON.stringify({ messages: newMessages }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.content) {
        reply += data.content;
        setMessages([...newMessages, { role: 'assistant', content: reply }]);
      }
      if (data.done) {
        setLoading(false);
        ws.close();
      }
      if (data.error) {
        setMessages([...newMessages, { role: 'assistant', content: 'Error: ' + data.error }]);
        setLoading(false);
        ws.close();
      }
    };

    ws.onerror = (err) => {
      setMessages([...newMessages, { role: 'assistant', content: 'WebSocket error' }]);
      setLoading(false);
      ws.close();
    };
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="static">
          <Toolbar>
            <BotIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Ollama Chatbot
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="md" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
          <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', mb: 2 }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
              <Box 
                ref={chatContainerRef}
                sx={{ 
                  flexGrow: 1, 
                  overflow: 'auto', 
                  p: 2,
                  scrollBehavior: 'smooth',
                  '&::-webkit-scrollbar': {
                    width: '8px',
                  },
                  '&::-webkit-scrollbar-track': {
                    background: '#f1f1f1',
                    borderRadius: '4px',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    background: '#c1c1c1',
                    borderRadius: '4px',
                    '&:hover': {
                      background: '#a8a8a8',
                    },
                  },
                }}
              >
                {messages.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <BotIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      Start a conversation with your AI assistant
                    </Typography>
                  </Box>
                ) : (
                  <List sx={{ p: 0 }}>
                    {messages.map((msg, idx) => (
                      <React.Fragment key={idx}>
                        <ListItem sx={{ 
                          justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                          px: 0,
                          py: 0.5
                        }}>
                          <Paper
                            sx={{
                              p: 2,
                              maxWidth: '70%',
                              backgroundColor: msg.role === 'user' ? 'primary.main' : 'grey.100',
                              color: msg.role === 'user' ? 'white' : 'text.primary',
                              borderRadius: 2,
                              display: 'flex',
                              alignItems: 'flex-start',
                              gap: 1
                            }}
                          >
                            {msg.role === 'assistant' && <BotIcon sx={{ fontSize: 20, mt: 0.5 }} />}
                            {msg.role === 'user' && <PersonIcon sx={{ fontSize: 20, mt: 0.5 }} />}
                            <Box sx={{ wordBreak: 'break-word' }}>
                              {msg.role === 'assistant' ? (
                                <ReactMarkdown 
                                  remarkPlugins={[remarkGfm]}
                                  components={{
                                    // Style code blocks
                                    code: ({node, inline, className, children, ...props}) => {
                                      const match = /language-(\w+)/.exec(className || '');
                                      return !inline ? (
                                        <Box
                                          component="pre"
                                          sx={{
                                            backgroundColor: 'rgba(0,0,0,0.1)',
                                            borderRadius: 1,
                                            p: 1,
                                            overflow: 'auto',
                                            fontSize: '0.875rem',
                                            my: 1
                                          }}
                                        >
                                          <Box
                                            component="code"
                                            className={className}
                                            {...props}
                                            sx={{
                                              fontFamily: 'monospace',
                                              backgroundColor: 'transparent'
                                            }}
                                          >
                                            {children}
                                          </Box>
                                        </Box>
                                      ) : (
                                        <Box
                                          component="code"
                                          className={className}
                                          {...props}
                                          sx={{
                                            backgroundColor: 'rgba(0,0,0,0.1)',
                                            borderRadius: 0.5,
                                            px: 0.5,
                                            fontFamily: 'monospace',
                                            fontSize: '0.875rem'
                                          }}
                                        >
                                          {children}
                                        </Box>
                                      );
                                    },
                                    // Style headings
                                    h1: ({node, ...props}) => <Typography variant="h4" {...props} sx={{ mt: 2, mb: 1 }} />,
                                    h2: ({node, ...props}) => <Typography variant="h5" {...props} sx={{ mt: 2, mb: 1 }} />,
                                    h3: ({node, ...props}) => <Typography variant="h6" {...props} sx={{ mt: 2, mb: 1 }} />,
                                    // Style paragraphs
                                    p: ({node, ...props}) => <Typography variant="body1" {...props} sx={{ mb: 1 }} />,
                                    // Style lists
                                    ul: ({node, ...props}) => <Box component="ul" {...props} sx={{ pl: 2, mb: 1 }} />,
                                    ol: ({node, ...props}) => <Box component="ol" {...props} sx={{ pl: 2, mb: 1 }} />,
                                    // Style links
                                    a: ({node, ...props}) => (
                                      <Typography
                                        component="a"
                                        {...props}
                                        sx={{ color: 'primary.main', textDecoration: 'underline' }}
                                      />
                                    ),
                                  }}
                                >
                                  {msg.content}
                                </ReactMarkdown>
                              ) : (
                                <Typography variant="body1">
                                  {msg.content}
                                </Typography>
                              )}
                            </Box>
                          </Paper>
                        </ListItem>
                        {idx < messages.length - 1 && <Divider sx={{ my: 1 }} />}
                      </React.Fragment>
                    ))}
                    {loading && (
                      <ListItem sx={{ justifyContent: 'flex-start', px: 0, py: 0.5 }}>
                        <Paper sx={{ p: 2, backgroundColor: 'grey.100', borderRadius: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                          <BotIcon sx={{ fontSize: 20 }} />
                          <CircularProgress size={20} />
                          <Typography variant="body2" color="text.secondary">
                            Thinking...
                          </Typography>
                        </Paper>
                      </ListItem>
                    )}
                  </List>
                )}
              </Box>
            </CardContent>
          </Card>

          <Paper component="form" onSubmit={handleSend} sx={{ p: 2, display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              size="small"
            />
            <IconButton
              type="submit"
              disabled={loading || !input.trim()}
              color="primary"
              sx={{ minWidth: 56 }}
            >
              <SendIcon />
            </IconButton>
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;