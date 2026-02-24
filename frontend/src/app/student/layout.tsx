'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import {
    LayoutDashboard,
    BookOpen,
    Brain,
    FileText,
    ClipboardList,
    MessageSquare,
    TrendingDown,
    User,
    LogOut,
    Menu,
    X,
    GraduationCap
} from 'lucide-react';
import { getUser, logout } from '@/lib/api';

interface SidebarLink {
    href: string;
    label: string;
    icon: React.ReactNode;
}

const studentLinks: SidebarLink[] = [
    { href: '/student', label: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { href: '/student/subjects', label: 'My Subjects', icon: <BookOpen className="w-5 h-5" /> },
    { href: '/student/ai-tutor', label: 'AI Tutor', icon: <Brain className="w-5 h-5" /> },
    { href: '/student/quizzes', label: 'Quizzes', icon: <ClipboardList className="w-5 h-5" /> },
    { href: '/student/assignments', label: 'Assignments', icon: <FileText className="w-5 h-5" /> },
    { href: '/student/weak-topics', label: 'Weak Topics', icon: <TrendingDown className="w-5 h-5" /> },
    { href: '/student/chat', label: 'Chat', icon: <MessageSquare className="w-5 h-5" /> },
    { href: '/student/profile', label: 'Profile', icon: <User className="w-5 h-5" /> },
];

export default function StudentLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();
    const [user, setUser] = useState<any>(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        const currentUser = getUser();
        if (!currentUser || currentUser.role !== 'student') {
            router.push('/');
            return;
        }
        setUser(currentUser);
    }, [router]);

    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-student-bg">
                <div className="loading-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-student-bg flex">
            {/* Mobile menu button */}
            <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md"
            >
                {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

            {/* Sidebar */}
            <aside className={`
        fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200
        transform transition-transform duration-200 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="p-6 border-b border-gray-100">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-student-primary rounded-xl flex items-center justify-center">
                                <GraduationCap className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <span className="font-bold text-gray-800">RAG Tutor</span>
                                <span className="block text-xs text-student-muted">Student Portal</span>
                            </div>
                        </div>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                        {studentLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                onClick={() => setSidebarOpen(false)}
                                className={`sidebar-link ${pathname === link.href ? 'active student' : ''}`}
                            >
                                {link.icon}
                                <span>{link.label}</span>
                            </Link>
                        ))}
                    </nav>

                    {/* User info */}
                    <div className="p-4 border-t border-gray-100">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 bg-student-primary/10 rounded-full flex items-center justify-center">
                                <span className="text-student-primary font-medium">
                                    {user.full_name?.charAt(0).toUpperCase()}
                                </span>
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-800 truncate">{user.full_name}</p>
                                <p className="text-xs text-gray-500 truncate">{user.email}</p>
                            </div>
                        </div>
                        <button
                            onClick={logout}
                            className="w-full flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                            <LogOut className="w-4 h-4" />
                            <span className="text-sm">Logout</span>
                        </button>
                    </div>
                </div>
            </aside>

            {/* Overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/20 z-30 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Main content */}
            <main className="flex-1 p-6 lg:p-8 overflow-auto">
                {children}
            </main>
        </div>
    );
}
