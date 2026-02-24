'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Save, ArrowLeft, Upload, File } from 'lucide-react';

interface Subject {
    id: number;
    name: string;
    code: string;
}

export default function EditAssignment({ params }: { params: { id: string } }) {
    const router = useRouter();
    const { id } = params;

    const [subjects, setSubjects] = useState<Subject[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    // Assignment Details
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [subjectId, setSubjectId] = useState('');
    const [dueDate, setDueDate] = useState('');
    const [maxMarks, setMaxMarks] = useState(100);
    const [currentAttachment, setCurrentAttachment] = useState<string | null>(null);

    useEffect(() => {
        const init = async () => {
            await Promise.all([fetchSubjects(), fetchAssignment()]);
            setLoading(false);
        };
        init();
    }, [id]);

    const fetchSubjects = async () => {
        try {
            const response = await api.get('/api/teacher/subjects');
            setSubjects(response.data);
        } catch (error) {
            console.error('Failed to fetch subjects');
        }
    };

    const fetchAssignment = async () => {
        try {
            // Need to fetch details. The current backend GET /teacher only lists summaries. 
            // We might not have a dedicated Detail endpoint for teacher, but we can iterate the list or 
            // assume we can use the student one? No, that's secured.
            // Let's check backend... router doesn't seem to have valid GET /teacher/{id} for assignment details explicitly?
            // Actually router has:
            // @router.get("/teacher", ...) -> list
            // @router.get("/teacher/{assignment_id}/submissions", ...) -> submissions
            // @router.patch("/teacher/{assignment_id}", ...) -> update
            // It seems we MISSING a GET /teacher/{assignment_id} endpoint for details!
            // I will have to add that to backend first.
            // Wait, I can try to find it in the list if I fetch all? 
            // Better to add the endpoint. But for now to avoid blocking, I will ADD specific endpoint to backend in same step
            // Or I can use the list endpoint and filter. Given the list is light, I'll filter for now to avoid complex backend edits if not strictly needed immediately, 
            // BUT a dedicated endpoint is better.
            // Let's try fetching all and filtering because `get_teacher_assignments` returns full objects usually.

            const response = await api.get('/api/assignments/teacher');
            const assignment = response.data.find((a: any) => a.id === parseInt(id));

            if (assignment) {
                setTitle(assignment.title);
                setDescription(assignment.description || '');
                setSubjectId(assignment.subject_id.toString());
                setMaxMarks(assignment.max_marks);
                // format date for input datetime-local: YYYY-MM-DDThh:mm
                const d = new Date(assignment.due_date);
                setDueDate(d.toISOString().slice(0, 16));
                setCurrentAttachment(assignment.attachment_url);
            } else {
                throw new Error("Assignment not found in list");
            }

        } catch (error) {
            console.error(error);
            alert('Failed to load assignment details');
            router.push('/teacher/assignments');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        try {
            const payload = {
                title,
                description,
                due_date: new Date(dueDate).toISOString(),
                max_marks: maxMarks
            };

            await api.patch(`/api/assignments/teacher/${id}`, payload);
            alert('Assignment updated successfully!');
            router.push('/teacher/assignments');
        } catch (error: any) {
            console.error('Update error:', error);
            const detail = error.response?.data?.detail;
            alert(detail || 'Failed to update assignment');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teacher-primary"></div>
            </div>
        );
    }

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
                    <h1 className="text-2xl font-bold text-gray-800">Edit Assignment</h1>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
                    <h2 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">Assignment Details</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                            <input
                                type="text"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="input-admin"
                                required
                            />
                        </div>

                        <div className="col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className="input-admin"
                                rows={5}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                            <select
                                value={subjectId}
                                disabled
                                className="input-admin bg-gray-50 cursor-not-allowed"
                            >
                                <option value="">Select Subject</option>
                                {subjects.map(s => (
                                    <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                                ))}
                            </select>
                            <p className="text-xs text-gray-500 mt-1">Subject cannot be changed after creation.</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                            <input
                                type="datetime-local"
                                value={dueDate}
                                onChange={(e) => setDueDate(e.target.value)}
                                className="input-admin"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Max Marks</label>
                            <input
                                type="number"
                                value={maxMarks}
                                onChange={(e) => setMaxMarks(parseInt(e.target.value))}
                                className="input-admin"
                                min="1"
                                required
                            />
                        </div>
                    </div>
                </div>

                {/* Attachment Section - Read Only for now as Update needs file upload handling specific logic we can skip for basic edit */}
                {currentAttachment && (
                    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center">
                        <File className="w-5 h-5 text-gray-400 mr-3" />
                        <span className="text-sm text-gray-600 truncate flex-1">{currentAttachment}</span>
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">Current Attachment</span>
                    </div>
                )}


                <div className="flex justify-end gap-3">
                    <button
                        type="button"
                        onClick={() => router.back()}
                        className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center px-6 py-2 bg-teacher-primary text-white rounded-lg hover:bg-opacity-90 font-medium disabled:opacity-50"
                    >
                        <Save className="w-4 h-4 mr-2" />
                        {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </form>
        </div>
    );
}
