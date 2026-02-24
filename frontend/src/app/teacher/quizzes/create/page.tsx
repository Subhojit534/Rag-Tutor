'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Trash2, Save, ArrowLeft, CheckCircle } from 'lucide-react';
import api from '@/lib/api';

interface Subject {
    id: number;
    name: string;
    code: string;
}

interface Question {
    id: number; // temp id for UI
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    correct_option: string;
    marks: number;
    explanation: string;
}

export default function CreateQuiz() {
    const router = useRouter();
    const [subjects, setSubjects] = useState<Subject[]>([]);
    const [loading, setLoading] = useState(false);

    // Quiz Details
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [subjectId, setSubjectId] = useState('');
    const [duration, setDuration] = useState(30);

    // Questions
    const [questions, setQuestions] = useState<Question[]>([
        {
            id: 1,
            question_text: '',
            option_a: '',
            option_b: '',
            option_c: '',
            option_d: '',
            correct_option: 'A',
            marks: 1,
            explanation: ''
        }
    ]);

    useEffect(() => {
        fetchSubjects();
    }, []);

    const fetchSubjects = async () => {
        try {
            const response = await api.get('/api/teacher/subjects');
            setSubjects(response.data);
            if (response.data.length > 0) {
                setSubjectId(response.data[0].id.toString());
            }
        } catch (error) {
            console.error('Failed to fetch subjects');
        }
    };

    const addQuestion = () => {
        setQuestions([
            ...questions,
            {
                id: questions.length + 1,
                question_text: '',
                option_a: '',
                option_b: '',
                option_c: '',
                option_d: '',
                correct_option: 'A',
                marks: 1,
                explanation: ''
            }
        ]);
    };

    const removeQuestion = (index: number) => {
        if (questions.length === 1) return;
        const newQuestions = [...questions];
        newQuestions.splice(index, 1);
        setQuestions(newQuestions);
    };

    const updateQuestion = (index: number, field: keyof Question, value: any) => {
        const newQuestions = [...questions];
        newQuestions[index] = { ...newQuestions[index], [field]: value };
        setQuestions(newQuestions);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!subjectId) {
            alert('Please select a subject');
            return;
        }

        setLoading(true);
        try {
            const payload = {
                title,
                description,
                subject_id: parseInt(subjectId),
                duration_minutes: duration,
                questions: questions.map(q => ({
                    question_text: q.question_text,
                    option_a: q.option_a,
                    option_b: q.option_b,
                    option_c: q.option_c,
                    option_d: q.option_d,
                    correct_option: q.correct_option,
                    marks: q.marks,
                    explanation: q.explanation
                }))
            };

            await api.post('/api/quizzes/', payload);
            alert('Quiz created successfully!');
            router.push('/teacher/quizzes');
        } catch (error: any) {
            console.error('Quiz creation error:', error);
            const detail = error.response?.data?.detail;
            if (typeof detail === 'object') {
                alert(JSON.stringify(detail, null, 2));
            } else {
                alert(detail || 'Failed to create quiz');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6 pb-20">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <button
                        onClick={() => router.back()}
                        className="flex items-center text-gray-500 hover:text-gray-700 mb-2 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4 mr-1" />
                        Back
                    </button>
                    <h1 className="text-2xl font-bold text-gray-800">Create New Quiz</h1>
                </div>
            </div>

            {subjects.length === 0 && !loading && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <CheckCircle className="h-5 w-5 text-yellow-400" />
                        </div>
                        <div className="ml-3">
                            <p className="text-sm text-yellow-700">
                                You don't have any subjects assigned yet. Please contact an Admin to assign subjects to you before creating a quiz.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Info */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
                    <h2 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">Quiz Details</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Quiz Title</label>
                            <input
                                type="text"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="input-admin"
                                placeholder="e.g. Data Structures Mid-Term"
                                required
                            />
                        </div>

                        <div className="col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className="input-admin"
                                rows={3}
                                placeholder="Instructions for students..."
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                            <select
                                value={subjectId}
                                onChange={(e) => setSubjectId(e.target.value)}
                                className="input-admin"
                                required
                            >
                                <option value="">Select Subject</option>
                                {subjects.map(s => (
                                    <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Duration (minutes)</label>
                            <input
                                type="number"
                                value={duration}
                                onChange={(e) => setDuration(parseInt(e.target.value))}
                                className="input-admin"
                                min="5"
                                required
                            />
                        </div>
                    </div>
                </div>

                {/* Questions */}
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-gray-800">Questions ({questions.length})</h2>
                        <button
                            type="button"
                            onClick={addQuestion}
                            className="flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors font-medium"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Add Question
                        </button>
                    </div>

                    {questions.map((q, index) => (
                        <div key={q.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 relative group">
                            <div className="absolute top-4 right-4">
                                <button
                                    type="button"
                                    onClick={() => removeQuestion(index)}
                                    className="text-gray-400 hover:text-red-500 transition-colors p-1"
                                    title="Remove Question"
                                >
                                    <Trash2 className="w-5 h-5" />
                                </button>
                            </div>

                            <h3 className="text-md font-medium text-gray-700 mb-4">Question {index + 1}</h3>

                            <div className="space-y-4">
                                <div>
                                    <input
                                        type="text"
                                        value={q.question_text}
                                        onChange={(e) => updateQuestion(index, 'question_text', e.target.value)}
                                        className="input-admin"
                                        placeholder="Enter your question here..."
                                        required
                                    />
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {['A', 'B', 'C', 'D'].map((opt) => (
                                        <div key={opt} className="relative">
                                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-medium">{opt}</span>
                                            <input
                                                type="text"
                                                value={q[`option_${opt.toLowerCase()}` as keyof Question]}
                                                onChange={(e) => updateQuestion(index, `option_${opt.toLowerCase()}` as keyof Question, e.target.value)}
                                                className="input-admin pl-8"
                                                placeholder={`Option ${opt}`}
                                                required
                                            />
                                        </div>
                                    ))}
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div>
                                        <label className="block text-xs font-medium text-gray-500 mb-1">Correct Answer</label>
                                        <select
                                            value={q.correct_option}
                                            onChange={(e) => updateQuestion(index, 'correct_option', e.target.value)}
                                            className="input-admin"
                                        >
                                            <option value="A">Option A</option>
                                            <option value="B">Option B</option>
                                            <option value="C">Option C</option>
                                            <option value="D">Option D</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-medium text-gray-500 mb-1">Marks</label>
                                        <input
                                            type="number"
                                            value={q.marks}
                                            onChange={(e) => updateQuestion(index, 'marks', parseInt(e.target.value))}
                                            className="input-admin"
                                            min="1"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-medium text-gray-500 mb-1">Explanation (Optional)</label>
                                        <input
                                            type="text"
                                            value={q.explanation}
                                            onChange={(e) => updateQuestion(index, 'explanation', e.target.value)}
                                            className="input-admin"
                                            placeholder="Why is this correct?"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Submit Bar */}
                <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)] z-10 lg:pl-64">
                    <div className="max-w-4xl mx-auto flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={() => router.back()}
                            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center px-6 py-2 bg-teacher-primary text-white rounded-lg hover:bg-opacity-90 font-medium disabled:opacity-50"
                        >
                            <Save className="w-4 h-4 mr-2" />
                            {loading ? 'Publishing...' : 'Publish Quiz'}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}
