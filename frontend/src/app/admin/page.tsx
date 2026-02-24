'use client';

import { useEffect, useState } from 'react';
import { Users, BookOpen, GraduationCap, Building2, Activity, AlertCircle } from 'lucide-react';
import api from '@/lib/api';

interface Stats {
    total_students: number;
    total_teachers: number;
    total_subjects: number;
    total_degrees: number;
    total_departments: number;
    exam_mode: boolean;
}

export default function AdminDashboard() {
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);
    const [examMode, setExamMode] = useState(false);
    const [updating, setUpdating] = useState(false);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const [usersRes, settingsRes, subjectsRes] = await Promise.all([
                api.get('/api/admin/users'),
                api.get('/api/admin/settings'),
                api.get('/api/admin/subjects')
            ]);

            const users = usersRes.data;
            const settings = settingsRes.data;
            const subjects = subjectsRes.data;

            setStats({
                total_students: users.filter((u: any) => u.role === 'student').length,
                total_teachers: users.filter((u: any) => u.role === 'teacher').length,
                total_subjects: subjects.length,
                total_degrees: 0,
                total_departments: 0,
                exam_mode: settings.exam_mode === 'true'
            });

            setExamMode(settings.exam_mode === 'true');
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleExamMode = async () => {
        setUpdating(true);
        try {
            await api.patch('/api/admin/settings', {
                exam_mode: !examMode
            });
            setExamMode(!examMode);
        } catch (error) {
            console.error('Failed to update exam mode:', error);
        } finally {
            setUpdating(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="loading-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Admin Dashboard</h1>
                    <p className="text-gray-500 mt-1">Manage your academic institution</p>
                </div>

                {/* Exam Mode Toggle */}
                <div className="card flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <AlertCircle className={`w-5 h-5 ${examMode ? 'text-red-500' : 'text-gray-400'}`} />
                        <span className="text-sm font-medium">Exam Mode</span>
                    </div>
                    <button
                        onClick={toggleExamMode}
                        disabled={updating}
                        className={`relative w-12 h-6 rounded-full transition-colors ${examMode ? 'bg-red-500' : 'bg-gray-200'
                            }`}
                    >
                        <span className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${examMode ? 'left-7' : 'left-1'
                            }`} />
                    </button>
                </div>
            </div>

            {/* Exam Mode Warning */}
            {examMode && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                    <div>
                        <p className="font-medium text-red-800">Exam Mode is Active</p>
                        <p className="text-sm text-red-600">AI Tutor is disabled for all students during examination period.</p>
                    </div>
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="card card-hover">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                            <Users className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Total Students</p>
                            <p className="text-2xl font-bold text-gray-800">{stats?.total_students || 0}</p>
                        </div>
                    </div>
                </div>

                <div className="card card-hover">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                            <GraduationCap className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Total Teachers</p>
                            <p className="text-2xl font-bold text-gray-800">{stats?.total_teachers || 0}</p>
                        </div>
                    </div>
                </div>

                <div className="card card-hover">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                            <BookOpen className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">Total Subjects</p>
                            <p className="text-2xl font-bold text-gray-800">{stats?.total_subjects || 0}</p>
                        </div>
                    </div>
                </div>

                <div className="card card-hover">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                            <Activity className="w-6 h-6 text-orange-600" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-500">System Status</p>
                            <p className="text-lg font-bold text-green-600">Healthy</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <a href="/admin/degrees" className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center">
                        <GraduationCap className="w-8 h-8 text-admin-primary mx-auto mb-2" />
                        <span className="text-sm font-medium">Add Degree</span>
                    </a>
                    <a href="/admin/departments" className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center">
                        <Building2 className="w-8 h-8 text-admin-primary mx-auto mb-2" />
                        <span className="text-sm font-medium">Add Department</span>
                    </a>
                    <a href="/admin/subjects" className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center">
                        <BookOpen className="w-8 h-8 text-admin-primary mx-auto mb-2" />
                        <span className="text-sm font-medium">Add Subject</span>
                    </a>
                    <a href="/admin/teachers" className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center">
                        <Users className="w-8 h-8 text-admin-primary mx-auto mb-2" />
                        <span className="text-sm font-medium">Register Teacher</span>
                    </a>
                </div>
            </div>
        </div>
    );
}
