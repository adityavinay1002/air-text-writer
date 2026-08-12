import { History as HistoryIcon, Trash2, Search, Calendar, Sparkles } from 'lucide-react';

export interface HistoryItem {
  id: string;
  query: string;
  timestamp: string;
  confidence?: number;
}

interface HistoryPanelProps {
  history: HistoryItem[];
  onSelectQuery: (query: string) => void;
  onClearHistory: () => void;
}

export function HistoryPanel({ history, onSelectQuery, onClearHistory }: HistoryPanelProps) {
  return (
    <section className="panel-surface" style={{ padding: '32px', borderRadius: '16px', margin: '20px 0' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ padding: '10px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '12px', color: '#10b981' }}>
            <HistoryIcon size={24} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', margin: 0 }}>
              Air-Writing Search History
            </h2>
            <p style={{ color: '#94a3b8', margin: '4px 0 0 0', fontSize: '0.95rem' }}>
              Saved in local storage for quick access
            </p>
          </div>
        </div>

        {history.length > 0 && (
          <button
            onClick={onClearHistory}
            style={{
              padding: '8px 16px',
              background: 'rgba(239, 68, 68, 0.1)',
              color: '#ef4444',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.85rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer'
            }}
          >
            <Trash2 size={14} /> Clear History
          </button>
        )}
      </div>

      {history.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {history.map((item) => (
            <div
              key={item.id}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '12px',
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justify: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={15} style={{ color: '#38bdf8' }} />
                  <strong style={{ fontSize: '1.1rem', color: '#fff', letterSpacing: '0.04em' }}>
                    {item.query}
                  </strong>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '4px', color: '#94a3b8', fontSize: '0.8rem' }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Calendar size={12} /> {item.timestamp}
                  </span>
                  {item.confidence !== undefined && (
                    <span>
                      Confidence: <strong style={{ color: '#10b981' }}>{Math.round(item.confidence * 100)}%</strong>
                    </span>
                  )}
                </div>
              </div>

              <button
                onClick={() => onSelectQuery(item.query)}
                style={{
                  padding: '8px 14px',
                  background: 'rgba(56, 189, 248, 0.1)',
                  color: '#38bdf8',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  borderRadius: '8px',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  cursor: 'pointer'
                }}
              >
                <Search size={14} /> Search Title
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '40px 20px', color: '#64748b' }}>
          <HistoryIcon size={36} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
          <p style={{ fontSize: '1rem', margin: 0, color: '#94a3b8' }}>
            No air-writing search history recorded yet.
          </p>
          <small style={{ color: '#64748b' }}>
            Confirmed air-written queries will automatically appear here.
          </small>
        </div>
      )}
    </section>
  );
}
