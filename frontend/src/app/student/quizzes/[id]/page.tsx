'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { ArrowLeft, Clock, AlertTriangle, CheckCircle, Award } from 'lucide-react';

interface Question {
    id: number;
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    marks: number;
}

interface QuizAttempt {
    attempt_id: number;
    quiz: {
        id: number;
        title: string;
        description: string;
        duration_minutes: number;
        total_marks: number;
        questions: Question[];
    };
}

interface QuizResult {
    quiz_id: number;
    quiz_title: string;
    score: number;
    total_marks: number;
    correct_answers: number;
    total_questions: number;
    percentage: number;
    responses: {
        question_id: number;
        question_text: string;
        selected_option: string | null;
        correct_option: string;
        is_correct: boolean;
        marks: number;
        explanation: string | null;
    }[];
}

export default function TakeQuiz({ params }: { params: { id: string } }) {
    const router = useRouter();
    const { id } = params;

    const [loading, setLoading] = useState(true);
    const [quizData, setQuizData] = useState<QuizAttempt | null>(null);
    const [resultData, setResultData] = useState<QuizResult | null>(null);
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [submitting, setSubmitting] = useState(false);
    const [timeLeft, setTimeLeft] = useState<number | null>(null);

    useEffect(() => {
        startQuiz();
    }, [id]);

    useEffect(() => {
        if (timeLeft === null || timeLeft <= 0 || resultData) return;

        const timer = setInterval(() => {
            setTimeLeft(prev => {
                if (prev === null || prev <= 1) {
                    clearInterval(timer);
                    handleSubmit(); // Auto-submit
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [timeLeft, resultData]);

    const startQuiz = async () => {
        try {
            const response = await api.get(`/api/quizzes/student/${id}/start`);
            setQuizData(response.data);
            setTimeLeft(response.data.quiz.duration_minutes * 60);
        } catch (error: any) {
            console.error('Failed to start quiz:', error);
            if (error.response?.status === 400 && error.response.data.detail === "Quiz already completed") {
                // Fetch result instead
                fetchResult();
            } else {
                alert('Failed to start quiz');
                router.push('/student/quizzes');
            }
        } finally {
            if (!resultData) setLoading(false);
        }
    };

    const fetchResult = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/api/quizzes/student/${id}/result`);
            setResultData(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch result:', error);
            alert('Failed to load quiz result');
            router.push('/student/quizzes');
        }
    };

    const handleOptionSelect = (questionId: number, option: string) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: option
        }));
    };

    const handleSubmit = async () => {
        if (!quizData || submitting || resultData) return;

        setSubmitting(true);
        try {
            const formattedAnswers = Object.entries(answers).map(([qId, option]) => ({
                question_id: parseInt(qId),
                selected_option: option
            }));

            await api.post(`/api/quizzes/student/${id}/submit`, {
                answers: formattedAnswers
            });

            // Fetch result after submit
            fetchResult();

        } catch (error) {
            console.error('Submission failed:', error);
            alert('Failed to submit quiz');
            setSubmitting(false);
        }
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    if (loading) return <div className="p-8 text-center flex items-center justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teacher-primary mr-3"></div> Loading...</div>;

    // --- RESULT VIEW ---
    if (resultData) {
        return (
            <div className="max-w-4xl mx-auto pb-20 space-y-6">
                <button
                    onClick={() => router.push('/student/quizzes')}
                    className="flex items-center text-gray-500 hover:text-gray-700 mb-2 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4 mr-1" />
                    Back to Quizzes
                </button>

                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">{resultData.quiz_title} - Result</h1>
                    <div className="flex justify-center items-center gap-8 mt-6">
                        <div className="text-center">
                            <div className="text-4xl font-bold text-teacher-primary mb-1">{resultData.score}/{resultData.total_marks}</div>
                            <div className="text-sm text-gray-500 font-medium">Your Score</div>
                        </div>
                        <div className="h-12 w-px bg-gray-200"></div>
                        <div className="text-center">
                            <div className="text-4xl font-bold text-green-600 mb-1">{resultData.percentage}%</div>
                            <div className="text-sm text-gray-500 font-medium">Percentage</div>
                        </div>
                        <div className="h-12 w-px bg-gray-200"></div>
                        <div className="text-center">
                            <div className="text-4xl font-bold text-blue-600 mb-1">{resultData.correct_answers}/{resultData.total_questions}</div>
                            <div className="text-sm text-gray-500 font-medium">Correct Answers</div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <h2 className="text-xl font-bold text-gray-800">Detailed Review</h2>
                    {resultData.responses.map((resp, index) => (
                        <div key={resp.question_id} className={`bg-white p-6 rounded-xl shadow-sm border-l-4 ${resp.is_correct ? 'border-l-green-500' : 'border-l-red-500'
                            } border-y border-r border-gray-100`}>
                            <div className="flex justify-between items-start mb-3">
                                <h3 className="font-semibold text-lg text-gray-800 flex items-start">
                                    <span className="bg-gray-100 text-gray-600 rounded px-2 py-0.5 text-sm mr-3 mt-1">Q{index + 1}</span>
                                    {resp.question_text}
                                </h3>
                                <div className="flex items-center">
                                    {resp.is_correct ? (
                                        <span className="flex items-center text-green-600 text-sm font-bold bg-green-50 px-2 py-1 rounded">
                                            <CheckCircle className="w-4 h-4 mr-1" />
                                            Correct (+{resp.marks})
                                        </span>
                                    ) : (
                                        <span className="flex items-center text-red-600 text-sm font-bold bg-red-50 px-2 py-1 rounded">
                                            <AlertTriangle className="w-4 h-4 mr-1" />
                                            Incorrect (0/{resp.marks})
                                        </span>
                                    )}
                                </div>
                            </div>

                            <div className="pl-12 space-y-2">
                                <div className="text-sm">
                                    <span className="font-medium text-gray-700">Your Answer: </span>
                                    <span className={resp.is_correct ? 'text-green-600 font-bold' : 'text-red-500 font-bold'}>
                                        {resp.selected_option || 'Not Answered'}
                                    </span>
                                </div>
                                {!resp.is_correct && (
                                    <div className="text-sm">
                                        <span className="font-medium text-gray-700">Correct Answer: </span>
                                        <span className="text-green-600 font-bold">{resp.correct_option}</span>
                                    </div>
                                )}
                                {resp.explanation && (
                                    <div className="mt-3 bg-blue-50 p-3 rounded-lg text-sm text-blue-800">
                                        <span className="font-bold">Explanation:</span> {resp.explanation}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // --- QUIZ TAKING VIEW ---
    if (!quizData) return <div className="p-8 text-center">Quiz not found</div>;

    return (
        <div className="max-w-4xl mx-auto pb-20">
            {/* Header */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6 sticky top-0 z-10 flex justify-between items-center">
                <div>
                    <h1 className="text-xl font-bold text-gray-800">{quizData.quiz.title}</h1>
                    <p className="text-sm text-gray-500">Total Marks: {quizData.quiz.total_marks}</p>
                </div>
                <div className={`flex items-center text-lg font-mono font-bold px-4 py-2 rounded-lg ${(timeLeft || 0) < 60 ? 'bg-red-100 text-red-600' : 'bg-blue-50 text-blue-600'
                    }`}>
                    <Clock className="w-5 h-5 mr-2" />
                    {timeLeft !== null ? formatTime(timeLeft) : '--:--'}
                </div>
            </div>

            <div className="space-y-6">
                {quizData.quiz.questions.map((q, index) => (
                    <div key={q.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="font-semibold text-lg text-gray-800 flex items-start">
                                <span className="bg-gray-100 text-gray-600 rounded px-2 py-0.5 text-sm mr-3 mt-1">Q{index + 1}</span>
                                {q.question_text}
                            </h3>
                            <span className="text-sm font-medium text-gray-500 whitespace-nowrap ml-4">{q.marks} marks</span>
                        </div>

                        <div className="space-y-3 pl-2">
                            {['A', 'B', 'C', 'D'].map((optKey) => {
                                // @ts-ignore
                                const optText = q[`option_${optKey.toLowerCase()}`];
                                const isSelected = answers[q.id] === optKey;

                                return (
                                    <div
                                        key={optKey}
                                        onClick={() => handleOptionSelect(q.id, optKey)}
                                        className={`flex items-center p-3 rounded-lg border cursor-pointer transition-all ${isSelected
                                                ? 'border-blue-500 bg-blue-50'
                                                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                            }`}
                                    >
                                        <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-3 ${isSelected ? 'border-blue-500' : 'border-gray-300'
                                            }`}>
                                            {isSelected && <div className="w-3 h-3 rounded-full bg-blue-500" />}
                                        </div>
                                        <span className="text-gray-700 font-medium mr-2">{optKey}.</span>
                                        <span className="text-gray-600">{optText}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                ))}
            </div>

            <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-200 flex justify-end md:static md:bg-transparent md:border-0 md:p-0 md:mt-8">
                <button
                    onClick={() => {
                        if (confirm('Are you sure you want to submit?')) {
                            handleSubmit();
                        }
                    }}
                    disabled={submitting}
                    className="px-8 py-3 bg-green-600 text-white rounded-xl shadow-lg hover:bg-green-700 transition-all font-bold text-lg flex items-center"
                >
                    <CheckCircle className="w-5 h-5 mr-2" />
                    {submitting ? 'Submitting...' : 'Submit Quiz'}
                </button>
            </div>
        </div>
    );
}
