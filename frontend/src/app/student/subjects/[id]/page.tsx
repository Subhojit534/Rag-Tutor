'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { ArrowLeft, FileText, Download, User, BookOpen, Clock, File } from 'lucide-react';

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

    const [subject, setSubject] = useState<SubjectDetail | null>(null);
    const [notes, setNotes] = useState<ClassNote[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (id) {
            fetchData();
        }
    }, [id]);

    const fetchData = async () => {
        try {
            const [subjectRes, notesRes] = await Promise.all([
                api.get(`/api/student/subjects/${id}`),
                api.get(`/api/student/subjects/${id}/notes`)
            ]);
            setSubject(subjectRes.data);
            setNotes(notesRes.data);
        } catch (error) {
            console.error('Failed to fetch data:', error);
        } finally {
            setLoading(false);
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

                                <a
                                    href={`http://localhost:8000/uploads/${note.file_url}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center justify-center w-full py-2.5 px-4 bg-gray-50 text-gray-600 rounded-xl hover:bg-student-primary hover:text-white font-medium text-sm transition-all duration-300 gap-2 border border-gray-100 hover:border-transparent group/btn"
                                    download
                                >
                                    <Download className="w-4 h-4 transition-transform group-hover/btn:-translate-y-0.5" />
                                    <span>Download Resource</span>
                                </a>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
