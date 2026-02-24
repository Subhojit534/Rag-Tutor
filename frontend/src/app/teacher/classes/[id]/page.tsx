'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { ArrowLeft, Users, Search, Mail, Hash, FileText, Download, Plus, X, File } from 'lucide-react';


interface Student {
    id: number;
    name: string;
    email: string;
    roll_number: string;
}

interface ClassNote {
    id: number;
    title: string;
    file_url: string;
    uploaded_at: string;
}

export default function ClassDetails({ params }: { params: { id: string } }) {
    const router = useRouter();
    const { id } = params;

    const [students, setStudents] = useState<Student[]>([]);
    const [notes, setNotes] = useState<ClassNote[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [activeTab, setActiveTab] = useState<'students' | 'notes'>('students');
    const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
    const [newNoteTitle, setNewNoteTitle] = useState('');
    const [newNoteFile, setNewNoteFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        if (id) {
            fetchStudents();
            fetchNotes(); // Fetch both initially or when tab changes? Fetching both is fine for now.
        }
    }, [id]);

    const fetchStudents = async () => {
        try {
            const response = await api.get(`/api/teacher/classes/${id}/students`);
            setStudents(response.data);
        } catch (error) {
            console.error('Failed to fetch students:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchNotes = async () => {
        try {
            const response = await api.get(`/api/teacher/classes/${id}/notes`);
            setNotes(response.data);
        } catch (error) {
            console.error('Failed to fetch notes:', error);
        }
    };

    const handleFileUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newNoteFile || !newNoteTitle) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', newNoteFile);

        try {
            await api.post(`/api/teacher/classes/${id}/notes?title=${encodeURIComponent(newNoteTitle)}`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setNewNoteTitle('');
            setNewNoteFile(null);
            setIsUploadModalOpen(false);
            fetchNotes();
        } catch (error) {
            console.error('Failed to upload note:', error);
            alert('Failed to upload note');
        } finally {
            setUploading(false);
        }
    };

    const filteredStudents = students.filter(student =>
        student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.roll_number.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teacher-primary"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <button
                        onClick={() => router.back()}
                        className="flex items-center text-gray-500 hover:text-gray-700 mb-2 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4 mr-1" />
                        Back to Classes
                    </button>
                    <h1 className="text-2xl font-bold text-gray-800">Class Details</h1>
                </div>
                {activeTab === 'notes' && (
                    <button
                        onClick={() => setIsUploadModalOpen(true)}
                        className="flex items-center space-x-2 px-4 py-2 bg-teacher-primary text-white rounded-lg hover:bg-teacher-secondary transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        <span>Upload Note</span>
                    </button>
                )}
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab('students')}
                        className={`
                            whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                            ${activeTab === 'students'
                                ? 'border-teacher-primary text-teacher-primary'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                        `}
                    >
                        Students ({students.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('notes')}
                        className={`
                            whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                            ${activeTab === 'notes'
                                ? 'border-teacher-primary text-teacher-primary'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                        `}
                    >
                        Class Notes ({notes.length})
                    </button>
                </nav>
            </div>

            {activeTab === 'students' ? (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-4 border-b border-gray-100 bg-gray-50">
                        <div className="relative max-w-md">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search by name or roll number..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teacher-primary/20 focus:border-teacher-primary transition-colors"
                            />
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left max-w-full">
                            <thead className="bg-gray-50 text-gray-600 font-medium text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4">Student Name</th>
                                    <th className="px-6 py-4">Roll Number</th>
                                    <th className="px-6 py-4">Email Address</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {filteredStudents.length === 0 ? (
                                    <tr>
                                        <td colSpan={3} className="px-6 py-12 text-center text-gray-400">
                                            <div className="flex flex-col items-center">
                                                <Users className="h-8 w-8 mb-2 opacity-50" />
                                                <p>No students found</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : (
                                    filteredStudents.map((student) => (
                                        <tr key={student.id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center">
                                                    <div className="h-8 w-8 rounded-full bg-teacher-primary/10 text-teacher-primary flex items-center justify-center font-bold text-xs mr-3">
                                                        {student.name.charAt(0)}
                                                    </div>
                                                    <span className="font-medium text-gray-800">{student.name}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center text-gray-600">
                                                    <Hash className="w-3 h-3 mr-2 text-gray-400" />
                                                    <span className="font-mono text-sm">{student.roll_number}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center text-gray-600">
                                                    <Mail className="w-3 h-3 mr-2 text-gray-400" />
                                                    <span>{student.email}</span>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {notes.length === 0 ? (
                        <div className="col-span-full text-center py-12 bg-white rounded-xl shadow-sm border border-gray-100">
                            <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                            <h3 className="text-lg font-medium text-gray-900">No notes uploaded</h3>
                            <p className="text-gray-500 mt-1">Upload notes to share with your students</p>
                            <button
                                onClick={() => setIsUploadModalOpen(true)}
                                className="mt-4 px-4 py-2 bg-teacher-primary text-white text-sm rounded-lg hover:bg-teacher-secondary transition-colors"
                            >
                                Upload First Note
                            </button>
                        </div>
                    ) : (
                        notes.map((note) => (
                            <div key={note.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className="p-2 bg-blue-50 rounded-lg">
                                            <FileText className="w-6 h-6 text-teacher-primary" />
                                        </div>
                                        <div>
                                            <h3 className="font-medium text-gray-800">{note.title}</h3>
                                            <p className="text-xs text-gray-500">
                                                {new Date(note.uploaded_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>
                                    <a
                                        href={`http://localhost:8000${note.file_url}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="p-2 text-gray-400 hover:text-teacher-primary hover:bg-gray-50 rounded-lg transition-all"
                                        title="Download"
                                    >
                                        <Download className="w-5 h-5" />
                                    </a>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Upload Modal */}
            {isUploadModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 m-4 animate-scale-in">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-gray-800">Upload Class Note</h2>
                            <button
                                onClick={() => setIsUploadModalOpen(false)}
                                className="text-gray-400 hover:text-gray-600 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <form onSubmit={handleFileUpload} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Title
                                </label>
                                <input
                                    type="text"
                                    value={newNoteTitle}
                                    onChange={(e) => setNewNoteTitle(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teacher-primary/20 focus:border-teacher-primary"
                                    placeholder="e.g., Chapter 1 Notes"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    File
                                </label>
                                <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 hover:border-teacher-primary/50 transition-colors bg-gray-50">
                                    <input
                                        type="file"
                                        onChange={(e) => setNewNoteFile(e.target.files?.[0] || null)}
                                        className="hidden"
                                        id="note-file"
                                        required
                                    />
                                    <label
                                        htmlFor="note-file"
                                        className="flex flex-col items-center cursor-pointer"
                                    >
                                        <File className="w-8 h-8 text-gray-400 mb-2" />
                                        <span className="text-sm text-gray-600 font-medium">
                                            {newNoteFile ? newNoteFile.name : 'Click to select file'}
                                        </span>
                                        <span className="text-xs text-gray-400 mt-1">
                                            PDF, DOC, PPT, Images
                                        </span>
                                    </label>
                                </div>
                            </div>

                            <div className="flex justify-end space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setIsUploadModalOpen(false)}
                                    className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors font-medium"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={uploading}
                                    className="px-4 py-2 bg-teacher-primary text-white rounded-lg hover:bg-teacher-secondary transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                                >
                                    {uploading ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                                            Uploading...
                                        </>
                                    ) : (
                                        'Upload Note'
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
