import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import './index.css'

class GlobalErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ContestMate Global Error]', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-600 flex items-center justify-center text-3xl mb-4 shadow-xl">
            🏆
          </div>
          <h1 className="text-xl font-bold mb-2">ContestMate 화면을 불러오는 중 문제가 발생했습니다</h1>
          <p className="text-sm text-slate-400 mb-6 max-w-md">
            캐시 또는 임시 상태로 인해 화면 표시가 지연되었습니다. 아래 버튼을 눌러 초기화 및 새로고침해주세요.
          </p>
          <button
            onClick={() => {
              localStorage.clear();
              window.location.reload();
            }}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-bold text-sm shadow-lg shadow-indigo-600/30 transition-all"
          >
            데이터 초기화 후 다시 시도
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <GlobalErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </GlobalErrorBoundary>
  </React.StrictMode>,
)
