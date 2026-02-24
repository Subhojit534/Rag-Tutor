'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { ArrowLeft, Search, FileText, CheckCircle, XCircle, Clock, Calendar } from 'lucide-react';

interface Attempt {
    id: number;
    quiz_id: number;
    student_id: number;
    student_name: string;
    student_roll: string;
    started_at: string;
    submitted_at: string | null;
    score: number;
    total_questions: number;
    correct_answers: number;
    is_completed: boolean;
}

export default function QuizResults({ params }: { params: { id: string } }) {
    const router = useRouter();
    const { id } = params;
    const [attempts, setAttempts] = useState<Attempt[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchAttempts = async () => {
            try {
                const response = await api.get(`/api/quizzes/teacher/${id}/attempts`);
                setAttempts(response.data);
            } catch (error) {
                console.error('Failed to fetch attempts:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAttempts();
    }, [id]);

    const filteredAttempts = attempts.filter(a =>
        a.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.student_roll.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getScoreColor = (score: number, total: number) => {
        const percentage = (score / total) * 100;
        if (percentage >= 80) return 'text-green-600';
        if (percentage >= 60) return 'text-blue-600';
        if (percentage >= 40) return 'text-yellow-600';
        return 'text-red-600';
    };

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
                        Back to Quizzes
                    </button>
                    <h1 className="text-2xl font-bold text-gray-800">Quiz Results</h1>
                    <p className="text-gray-500 mt-1">View student performance and scores</p>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-4 border-b border-gray-100 flex gap-4">
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input
                            type="text"
                            placeholder="Search by student name or roll number..."
                            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teacher-primary/20 focus:border-teacher-primary"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 text-gray-500 font-medium text-sm">
                            <tr>
                                <th className="px-6 py-4">Student</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">Submitted At</th>
                                <th className="px-6 py-4">Correct Answers</th>
                                <th className="px-6 py-4 text-right">Score</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredAttempts.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                                        <div className="flex flex-col items-center">
                                            <FileText className="w-8 h-8 text-gray-300 mb-2" />
                                            <p>No attempts found</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : (
                                filteredAttempts.map((attempt) => (
                                    <tr key={attempt.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold text-sm">
                                                    {attempt.student_name.charAt(0)}
                                                </div>
                                                <div>
                                                    <div className="font-medium text-gray-900">{attempt.student_name}</div>
                                                    <div className="text-xs text-gray-500">{attempt.student_roll}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {attempt.is_completed ? (
                                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                                    <CheckCircle className="w-3 h-3 mr-1" />
                                                    Completed
                                                </span>
                                            ) : (
                                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">
                                                    <Clock className="w-3 h-3 mr-1" />
                                                    In Progress
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {attempt.submitted_at ? (
                                                <div className="flex items-center gap-1">
                                                    <Calendar className="w-4 h-4 text-gray-400" />
                                                    {new Date(attempt.submitted_at).toLocaleDateString()}
                                                    <span className="text-gray-400 mx-1">•</span>
                                                    {new Date(attempt.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </div>
                                            ) : '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600">
                                            {attempt.correct_answers} / {attempt.total_questions}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <span className={`font-bold ${getScoreColor(attempt.score, attempt.total_questions * 4)}`}>
                                                {attempt.score}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
