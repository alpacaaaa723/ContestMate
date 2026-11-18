import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bell, CheckCircle2, AlertTriangle, ArrowRight, Clock } from 'lucide-react';
import { notificationApi } from '../services/api';

const formatNotifType = (type) => {
  switch (type) {
    case 'DEADLINE_TODAY': return '🚨 오늘 마감 알림';
    case 'DEADLINE_D1': return '🔥 마감 1일 전 알림';
    case 'DEADLINE_D3': return '⚠️ 마감 3일 전 알림';
    case 'DEADLINE_D7': return '⏰ 마감 7일 전 알림';
    case 'NEW_CONTEST': return '✨ 신규 맞춤 공모전';
    case 'TEST_MESSAGE': return '💬 텔레그램 연동 테스트';
    default: return type;
  }
};

const NotificationsPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notificationApi.getHistory()
      .then(data => setHistory(data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">알림 발송 이력</h1>
          <p className="text-xs text-slate-500 mt-1">
            텔레그램 봇을 통해 발송된 공모전 마감 및 신규 등록 알림 기록입니다.
          </p>
        </div>

        <Link
          to="/preferences"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-bold text-slate-700 transition"
        >
          <span>알림 설정 변경</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* History List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(n => (
            <div key={n} className="h-20 rounded-2xl bg-slate-200/70 animate-pulse"></div>
          ))}
        </div>
      ) : history.length > 0 ? (
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden divide-y divide-slate-100">
          {history.map((log) => (
            <div key={log.id} className="p-5 flex items-center justify-between gap-4 hover:bg-slate-50/50 transition">
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                  log.status === 'SUCCESS'
                    ? 'bg-emerald-50 text-emerald-600'
                    : 'bg-rose-50 text-rose-600'
                }`}>
                  {log.status === 'SUCCESS' ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : (
                    <AlertTriangle className="w-5 h-5" />
                  )}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-800">
                      {formatNotifType(log.notification_type)}
                    </span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                      log.status === 'SUCCESS' 
                        ? 'bg-emerald-100 text-emerald-800' 
                        : 'bg-rose-100 text-rose-800'
                    }`}>
                      {log.status}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-slate-900 mt-0.5">
                    {log.contest_title || '공모전 알림'}
                  </p>
                  {log.error_message && (
                    <p className="text-xs text-rose-500 mt-0.5">
                      오류: {log.error_message}
                    </p>
                  )}
                </div>
              </div>

              <div className="text-right shrink-0 text-xs text-slate-400 font-medium">
                <div className="flex items-center gap-1 justify-end">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{new Date(log.sent_at).toLocaleDateString('ko-KR')}</span>
                </div>
                <div className="text-[11px]">
                  {new Date(log.sent_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 space-y-3">
          <Bell className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">발송된 알림 이력이 없습니다</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            [맞춤 설정]에서 Telegram Chat ID를 등록하고 알림을 켜두시면 마감 알림과 신규 공모전 소식이 전송됩니다.
          </p>
          <Link
            to="/preferences"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold hover:bg-blue-700 transition"
          >
            <span>텔레그램 연동하러 가기</span>
          </Link>
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;
