import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/common/Sidebar';
import Navbar from './components/common/Navbar';
import DashboardPage from './pages/DashboardPage';
import ContestListPage from './pages/ContestListPage';
import CalendarPage from './pages/CalendarPage';
import BookmarksPage from './pages/BookmarksPage';
import PreferencesPage from './pages/PreferencesPage';
import NotificationsPage from './pages/NotificationsPage';
import InstallPrompt from './components/common/InstallPrompt';
import BottomNav from './components/common/BottomNav';

function App() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm md:hidden animate-fadeIn"
          onClick={() => setMobileMenuOpen(false)}
        >
          <div 
            className="w-72 max-w-[85vw] h-full bg-white shadow-2xl animate-in slide-in-from-left duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            <Sidebar isMobile={true} onClose={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar onMobileMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)} />
        
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 pb-24 md:pb-8">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/contests" element={<ContestListPage />} />
            <Route path="/calendar" element={<CalendarPage />} />
            <Route path="/bookmarks" element={<BookmarksPage />} />
            <Route path="/preferences" element={<PreferencesPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
          </Routes>
        </main>
      </div>

      {/* Mobile Bottom Navigation Bar */}
      <BottomNav />

      {/* PWA App Install Prompt */}
      <InstallPrompt />
    </div>
  );
}

export default App;
