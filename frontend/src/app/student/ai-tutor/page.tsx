'use client';

import { useEffect, useState, useRef } from 'react';
import { Brain, Send, BookOpen, AlertCircle, RefreshCcw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import api from '@/lib/api';

interface Subject {
    id: number;
    name: string;
    code: string;
    has_pdfs: boolean;
    pdf_count: number;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
    citations?: string[];
}

interface AIStatus {
    exam_mode: boolean;
    message: string;
}

export default function AITutorPage() {
    const [subjects, setSubjects] = useState<Subject[]>([]);
    const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
    const [sessionId, setSessionId] = useState<number | null>(null);
    const [rateLimitInfo, setRateLimitInfo] = useState({ remaining: 10, limited: false });

    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetchStatus();
        fetchSubjects();
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const fetchStatus = async () => {
        try {
            const response = await api.get('/api/ai/status');
            setAiStatus(response.data);
        } catch (error) {
            console.error('Failed to fetch AI status:', error);
        }
    };

    const fetchSubjects = async () => {
        try {
            const response = await api.get('/api/ai/subjects');
            setSubjects(response.data);
        } catch (error) {
            console.error('Failed to fetch subjects:', error);
        }
    };

    const fetchRateLimit = async () => {
        try {
            const response = await api.get('/api/ai/rate-limit');
            setRateLimitInfo({
                remaining: response.data.queries_remaining,
                limited: response.data.is_limited
            });
        } catch (error) {
            console.error('Failed to fetch rate limit:', error);
        }
    };

    const handleSend = async () => {
        if (!input.trim() || !selectedSubject || loading) return;

        const userMessage: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await api.post('/api/ai/chat', {
                subject_id: selectedSubject.id,
                question: input,
                session_id: sessionId
            });

            const aiMessage: Message = {
                role: 'assistant',
                content: response.data.answer,
                citations: response.data.citations
            };

            setMessages(prev => [...prev, aiMessage]);
            setSessionId(response.data.session_id);
            fetchRateLimit();
        } catch (error: any) {
            if (error.response?.status === 429) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: '⚠️ Rate limit exceeded. Please wait a moment before asking another question.'
                }]);
            } else if (error.response?.status === 403) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: '🚫 AI Tutor is currently disabled during the examination period.'
                }]);
            } else {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: 'Sorry, I encountered an error. Please try again.'
                }]);
            }
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const selectSubject = (subject: Subject) => {
        setSelectedSubject(subject);
        setMessages([]);
        setSessionId(null);
        fetchRateLimit();
    };

    // Exam mode check
    if (aiStatus?.exam_mode) {
        return (
            <div className="flex items-center justify-center h-[calc(100vh-8rem)]">
                <div className="text-center max-w-md">
                    <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <AlertCircle className="w-10 h-10 text-red-500" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">AI Tutor Unavailable</h2>
                    <p className="text-gray-600">
                        The AI Tutor is temporarily disabled during the examination period to maintain academic integrity.
                    </p>
                    <p className="text-sm text-gray-500 mt-4">
                        You can still use the Chat feature to contact your teachers.
                    </p>
                </div>
            </div>
        );
    }

    // Subject selection
    if (!selectedSubject) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">AI Tutor</h1>
                    <p className="text-gray-500 mt-1">Select a subject to start learning</p>
                </div>

                {subjects.length === 0 ? (
                    <div className="card text-center py-12">
                        <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500">No subjects with course materials available yet.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {subjects.map((subject) => (
                            <button
                                key={subject.id}
                                onClick={() => selectSubject(subject)}
                                className={`card card-hover text-left`}
                            >
                                <div className="flex items-start gap-4">
                                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${subject.has_pdfs ? 'bg-student-primary/10' : 'bg-gray-100'
                                        }`}>
                                        <BookOpen className={`w-6 h-6 ${subject.has_pdfs ? 'text-student-primary' : 'text-gray-400'
                                            }`} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-medium text-gray-800 truncate">{subject.name}</h3>
                                        <p className="text-sm text-gray-500">{subject.code}</p>
                                        {subject.has_pdfs ? (
                                            <span className="badge-success mt-2">
                                                {subject.pdf_count} PDF{subject.pdf_count > 1 ? 's' : ''} available
                                            </span>
                                        ) : (
                                            <span className="badge-warning mt-2">No materials • General Mode</span>
                                        )}
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                )}
            </div>
        );
    }

    // Chat interface
    return (
        <div className="h-[calc(100vh-8rem)] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setSelectedSubject(null)}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        ← Back
                    </button>
                    <div>
                        <h1 className="text-lg font-bold text-gray-800">{selectedSubject.name}</h1>
                        <p className="text-sm text-gray-500">AI Tutor • Socratic Method</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-500">
                        {rateLimitInfo.remaining}/10 queries left
                    </span>
                    <button
                        onClick={() => {
                            setMessages([]);
                            setSessionId(null);
                        }}
                        className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                        title="New conversation"
                    >
                        <RefreshCcw className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto bg-gray-50 rounded-xl p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center py-12">
                        <Brain className="w-16 h-16 text-student-primary/30 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-700 mb-2">
                            Ask me anything about {selectedSubject.name}
                        </h3>
                        <p className="text-sm text-gray-500 max-w-md mx-auto">
                            I'll help you understand concepts using the Socratic method, guiding you with questions.
                            {!selectedSubject.has_pdfs && (
                                <span className="block mt-2 text-amber-600">
                                    Note: No course materials uploaded. Answering from general knowledge.
                                </span>
                            )}
                        </p>
                    </div>
                )}

                {messages.map((message, index) => (
                    <div key={index} className={`ai-message ${message.role}`}>
                        <div className={`prose prose-sm max-w-none ${message.role === 'user' ? 'prose-invert' : 'prose-gray'}`}>
                            <ReactMarkdown
                                remarkPlugins={[remarkMath]}
                                rehypePlugins={[rehypeKatex]}
                            >
                                {message.content}
                            </ReactMarkdown>
                        </div>
                        {message.citations && message.citations.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-white/20">
                                <p className="text-xs font-medium mb-1">📚 Sources:</p>
                                <ul className="text-xs opacity-80">
                                    {message.citations.map((citation, i) => (
                                        <li key={i}>• {citation}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="ai-message assistant">
                        <div className="loading-dots">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="mt-4 flex gap-3">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question..."
                    className="flex-1 input-student"
                    disabled={loading || rateLimitInfo.limited}
                />
                <button
                    onClick={handleSend}
                    disabled={!input.trim() || loading || rateLimitInfo.limited}
                    className="btn-student px-6 flex items-center gap-2 disabled:opacity-50"
                >
                    <Send className="w-5 h-5" />
                    <span className="hidden sm:inline">Send</span>
                </button>
            </div>
        </div>
    );
}
