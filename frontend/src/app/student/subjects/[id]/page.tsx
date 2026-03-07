'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import useSWR from 'swr';
import { fetcher } from '@/lib/api';
import { ArrowLeft, FileText, Download, User, BookOpen, Clock, File, Eye, X, MessageSquare, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface SubjectDetail {
    id: number;
    name: string;
    code: string;
    credits: number;
    teacher: {
        id: number;
        name: string;
        email: string;
    } | null;
}

interface ClassNote {
    id: number;
    title: string;
    file_url: string;
    uploaded_at: string;
}

export default function SubjectDetails({ params }: { params: { id: string } }) {
    const router = useRouter();
    const { id } = params;

    const { data: subjectData, isLoading: loadingSubject } = useSWR<SubjectDetail>(id ? `/api/student/subjects/${id}` : null, fetcher);
    const { data: notesData, isLoading: loadingNotes } = useSWR<ClassNote[]>(id ? `/api/student/subjects/${id}/notes` : null, fetcher);

    const subject = subjectData || null;
    const notes = notesData || [];
    const loading = loadingSubject || loadingNotes;

    const [selectedPdf, setSelectedPdf] = useState<string | null>(null);

    // AI Chat State
    const [askAiText, setAskAiText] = useState<string>('');
    const [askAiResponse, setAskAiResponse] = useState<string>('');
    const [isAskAiLoading, setIsAskAiLoading] = useState(false);
    const [selectionRect, setSelectionRect] = useState<{ x: number, y: number } | null>(null);

    // Listen for text selection to show Ask AI tooltip
    useEffect(() => {
        const handleSelection = () => {
            const selection = window.getSelection();
            if (selection && selection.toString().trim().length > 0) {
                const range = selection.getRangeAt(0);
                const rect = range.getBoundingClientRect();

                // Position the tooltip slightly above the selection
                setSelectionRect({
                    x: rect.left + (rect.width / 2),
                    y: rect.top - 10
                });
            } else {
                setSelectionRect(null);
            }
        };

        // Listen for mouseup on the document to catch selections
        document.addEventListener('mouseup', handleSelection);

        // Also try to listen to iframe messages if it's from the same origin
        const handleMessage = (event: MessageEvent) => {
            if (event.data && event.data.type === 'textSelected') {
                const { text, rect } = event.data;
                // Try to map iframe coordinates to parent document
                const iframe = document.getElementById('pdf-viewer-iframe');
                if (iframe) {
                    const iframeRect = iframe.getBoundingClientRect();

                    // We need to simulate storing the text for the button to pick up
                    // But since we can't easily read window.getSelection() from the iframe securely across origins,
                    // we'll store it explicitly
                    window.sessionStorage.setItem('currentSelection', text);

                    setSelectionRect({
                        x: iframeRect.left + rect.left + (rect.width / 2),
                        y: iframeRect.top + rect.top - 10
                    });
                }
            } else if (event.data && event.data.type === 'selectionCleared') {
                setSelectionRect(null);
                window.sessionStorage.removeItem('currentSelection');
            }
        };

        window.addEventListener('message', handleMessage);

        return () => {
            document.removeEventListener('mouseup', handleSelection);
            window.removeEventListener('message', handleMessage);
        };
    }, []);

    const handleAskAI = async (text: string) => {
        setAskAiText(text);
        setIsAskAiLoading(true);
        setAskAiResponse('');

        try {
            const response = await api.post('/api/ai/chat', {
                subject_id: Number(id),
                question: `Explain this text from the document:\n\n"${text}"`
            });
            setAskAiResponse(response.data.answer);
        } catch (error: any) {
            console.error("AI Error:", error);
            setAskAiResponse(error.response?.data?.detail || "Sorry, I couldn't process your request right now.");
        } finally {
            setIsAskAiLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-student-primary"></div>
            </div>
        );
    }

    if (!subject) {
        return (
            <div className="text-center py-12">
                <h2 className="text-xl font-semibold text-gray-800">Subject not found</h2>
                <button
                    onClick={() => router.back()}
                    className="mt-4 text-student-primary hover:underline"
                >
                    Go Back
                </button>
            </div>
        );
    }

    const getDownloadUrl = (url: string) => {
        if (!url) return '#';
        if (url.startsWith('http')) return url;
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        if (url.startsWith('/uploads/') || url.startsWith('uploads/')) {
            const cleanPath = url.startsWith('/') ? url : `/${url}`;
            return `${apiUrl}${cleanPath}`;
        }
        const cleanPath = url.startsWith('/') ? url.slice(1) : url;
        return `${apiUrl}/uploads/${cleanPath}`;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-bl-full -mr-16 -mt-16 opacity-50 pointer-events-none"></div>

                <button
                    onClick={() => router.back()}
                    className="relative z-10 flex items-center text-gray-500 hover:text-student-primary mb-6 transition-colors font-medium text-sm group"
                >
                    <ArrowLeft className="w-4 h-4 mr-1 transition-transform group-hover:-translate-x-1" />
                    Back to All Subjects
                </button>

                <div className="relative z-10 flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-4 mb-3">
                            <h1 className="text-3xl font-bold text-gray-900">{subject.name}</h1>
                            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100 font-mono">
                                {subject.code}
                            </span>
                        </div>

                        <div className="flex items-center gap-6 text-sm text-gray-600">
                            <div className="flex items-center gap-2">
                                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-600 border border-gray-200">
                                    {subject.credits} Credits
                                </span>
                            </div>

                            {subject.teacher && (
                                <div className="flex items-center gap-2 bg-gray-50 py-1 px-3 rounded-full border border-gray-100">
                                    <User className="w-4 h-4 text-gray-400" />
                                    <span className="font-medium text-gray-700">{subject.teacher.name}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-200">
                        <BookOpen className="w-8 h-8 text-white" />
                    </div>
                </div>
            </div>

            {/* Notes Section */}
            <div>
                <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                    <div className="p-2 bg-indigo-100 rounded-lg">
                        <FileText className="w-5 h-5 text-indigo-600" />
                    </div>
                    <span>Class Notes & Resources</span>
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {notes.length === 0 ? (
                        <div className="col-span-full bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
                            <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                <FileText className="w-8 h-8 text-gray-300" />
                            </div>
                            <h3 className="text-lg font-medium text-gray-900 mb-1">No notes available</h3>
                            <p className="text-gray-500">The teacher hasn't uploaded any resources for this subject yet.</p>
                        </div>
                    ) : (
                        notes.map((note) => (
                            <div
                                key={note.id}
                                className="group bg-white p-5 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md hover:border-student-primary/30 transition-all duration-300 flex flex-col justify-between h-full"
                            >
                                <div className="flex items-start gap-4 mb-4">
                                    <div className="p-3 bg-blue-50 text-blue-600 rounded-xl group-hover:bg-student-primary group-hover:text-white transition-colors duration-300">
                                        <File className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-800 line-clamp-2 leading-snug group-hover:text-student-primary transition-colors" title={note.title}>
                                            {note.title}
                                        </h3>
                                        <div className="flex items-center gap-1.5 mt-1.5 text-xs text-gray-500">
                                            <Clock className="w-3.5 h-3.5" />
                                            <span>{new Date(note.uploaded_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex gap-2 w-full mt-2">
                                    <button
                                        onClick={() => setSelectedPdf(getDownloadUrl(note.file_url))}
                                        className="flex-1 flex items-center justify-center py-2.5 px-4 bg-student-primary text-white rounded-xl hover:bg-opacity-90 font-medium text-sm transition-all duration-300 gap-2 border border-transparent shadow-sm group/btn"
                                    >
                                        <Eye className="w-4 h-4 transition-transform group-hover/btn:scale-110" />
                                        <span>View</span>
                                    </button>
                                    <a
                                        href={getDownloadUrl(note.file_url)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center justify-center px-4 bg-gray-50 text-gray-600 rounded-xl hover:bg-gray-100 hover:text-student-primary font-medium transition-all duration-300 border border-gray-200"
                                        download
                                        title="Download Resource"
                                    >
                                        <Download className="w-5 h-5" />
                                    </a>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* PDF Viewer Modal */}
            {selectedPdf && (
                <div className="fixed inset-0 bg-black/70 z-50 flex flex-col p-4 sm:p-6 backdrop-blur-sm transition-opacity">
                    <div className="flex justify-end mb-4">
                        <button
                            onClick={() => setSelectedPdf(null)}
                            className="bg-white/20 hover:bg-white/30 text-white rounded-full p-2 transition-colors flex items-center gap-2 px-4 shadow-lg"
                        >
                            <span className="font-medium">Close Viewer</span>
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                    <div className="flex-1 w-full max-w-6xl mx-auto bg-white rounded-2xl overflow-hidden shadow-2xl relative">
                        <div className="bg-indigo-50 border-b border-indigo-100 p-3 text-center text-sm text-indigo-800 font-medium">
                            💡 Use your browser's PDF viewer tools to zoom and read. If you copy text from the PDF, use the Ask AI button below!
                        </div>

                        <div className="flex-1 w-full relative">
                            {selectedPdf.endsWith('.pdf') ? (
                                <iframe
                                    src={`${selectedPdf}`}
                                    className="w-full h-[70vh] border-0 bg-white"
                                    title="PDF Viewer"
                                    id="pdf-viewer-iframe"
                                />
                            ) : (
                                <div className="flex items-center justify-center h-full w-full relative z-10 bg-gray-50 p-8 text-center flex-1">
                                    <div>
                                        <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                                        <h3 className="text-xl font-bold text-gray-700 mb-2">Browser View Not Supported</h3>
                                        <p className="text-gray-500 mb-6">This file type cannot be previewed in the browser.</p>
                                        <a
                                            href={selectedPdf}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            download
                                            className="inline-flex items-center gap-2 bg-student-primary text-white px-6 py-3 rounded-xl font-medium hover:bg-opacity-90 transition"
                                        >
                                            <Download className="w-5 h-5" />
                                            Download File Instead
                                        </a>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Persistent Ask AI button when a PDF is open */}
                        <div className="border-t border-gray-100 bg-white p-4 flex justify-between items-center shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] relative z-20">
                            <div className="flex items-center gap-2">
                                <div className="hidden sm:block text-sm text-gray-500 max-w-md">
                                    Copy any tricky text from the document, then click "Ask AI" to get an instant explanation from your AI Tutor.
                                </div>
                            </div>
                            <button
                                onClick={async () => {
                                    try {
                                        // Try to read clipboard
                                        const text = await navigator.clipboard.readText();
                                        if (text && text.trim().length > 0) {
                                            handleAskAI(text.trim());
                                        } else {
                                            alert("Please copy some text from the PDF first!");
                                        }
                                    } catch (err) {
                                        // Fallback if clipboard API is blocked
                                        const text = prompt("Paste the text you want explained:");
                                        if (text && text.trim().length > 0) {
                                            handleAskAI(text.trim());
                                        }
                                    }
                                }}
                                className="bg-indigo-600 text-white shadow-md rounded-xl px-5 py-2.5 flex items-center gap-2 hover:bg-indigo-700 transition font-medium text-sm whitespace-nowrap border border-indigo-500"
                            >
                                <MessageSquare className="w-4 h-4" />
                                Ask AI Tutor
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Context Tooltip for document-level selection */}
            {selectionRect && (
                <div
                    className="fixed z-[70] animate-in fade-in zoom-in duration-200 pointer-events-auto"
                    style={{
                        left: `${selectionRect.x}px`,
                        top: `${selectionRect.y}px`,
                        transform: 'translate(-50%, -100%)'
                    }}
                >
                    <button
                        onMouseDown={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                        }}
                        onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();

                            // Get text from session storage (iframe message) or window selection
                            const iframeText = window.sessionStorage.getItem('currentSelection');
                            const selectionText = window.getSelection()?.toString().trim();
                            const text = iframeText || selectionText;

                            if (text) {
                                handleAskAI(text);
                                setSelectionRect(null);
                                window.getSelection()?.removeAllRanges();
                                window.sessionStorage.removeItem('currentSelection');
                            }
                        }}
                        className="bg-indigo-600 text-white shadow-xl rounded-full px-4 py-2 flex items-center gap-2 hover:bg-indigo-700 transition font-medium text-sm whitespace-nowrap border border-indigo-500 ring-4 ring-indigo-600/20"
                    >
                        <MessageSquare className="w-4 h-4" />
                        Ask AI
                    </button>
                    <div className="w-3 h-3 bg-indigo-600 absolute -bottom-1 left-1/2 transform -translate-x-1/2 rotate-45 border-r border-b border-indigo-500"></div>
                </div>
            )}

            {/* AI Explanation Modal */}
            {askAiText && (
                <div className="fixed inset-0 bg-black/60 z-[60] flex items-center justify-center p-4 sm:p-6 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="w-full max-w-2xl bg-white rounded-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">
                        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-indigo-50/50">
                            <h3 className="font-bold text-gray-900 flex items-center gap-2">
                                <div className="p-1.5 bg-indigo-100 rounded-lg">
                                    <MessageSquare className="w-5 h-5 text-indigo-600" />
                                </div>
                                Ask AI Tutor
                            </h3>
                            <button
                                onClick={() => setAskAiText('')}
                                className="text-gray-400 hover:text-gray-600 p-1.5 rounded-full hover:bg-white transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-6 overflow-y-auto flex-1 bg-gray-50/50">
                            <div className="mb-6">
                                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                                    <FileText className="w-3.5 h-3.5" /> Selected Text
                                </h4>
                                <div className="bg-white p-4 rounded-xl border border-gray-200 text-gray-700 italic border-l-4 border-l-indigo-400 text-sm shadow-sm relative">
                                    "{askAiText}"
                                </div>
                            </div>

                            <div>
                                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                                    <MessageSquare className="w-3.5 h-3.5" /> AI Explanation
                                </h4>
                                {isAskAiLoading ? (
                                    <div className="bg-white p-8 rounded-xl border border-gray-200 flex flex-col items-center justify-center text-indigo-600 gap-4 shadow-sm min-h-[200px]">
                                        <Loader2 className="w-8 h-8 animate-spin" />
                                        <div className="flex flex-col items-center text-center">
                                            <span className="text-sm font-medium">Generating explanation...</span>
                                            <span className="text-xs text-gray-400 mt-1">Analyzing context from your document</span>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="bg-white p-6 rounded-xl border border-gray-200 text-gray-800 shadow-sm min-h-[200px]">
                                        <div className="prose prose-sm max-w-none prose-indigo prose-p:leading-relaxed prose-pre:bg-gray-50 prose-pre:border prose-pre:border-gray-200 text-gray-700">
                                            <ReactMarkdown
                                                remarkPlugins={[[remarkMath]]}
                                                rehypePlugins={[[rehypeKatex]]}
                                            >
                                                {askAiResponse}
                                            </ReactMarkdown>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="p-4 border-t border-gray-100 bg-white flex justify-end">
                            <button
                                onClick={() => setAskAiText('')}
                                className="px-6 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-medium text-sm transition-colors border border-gray-200"
                            >
                                Close Definition
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
