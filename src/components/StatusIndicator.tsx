import { Check, LoaderCircle, Radio, Sparkles, Wifi, AlertTriangle } from 'lucide-react';
import type { GestureState, ConnectionStatus } from '@/types';

interface StatusIndicatorProps {
  gestureState: GestureState;
  recognizedWord: string;
  connectionStatus: ConnectionStatus;
}

const stateCopy: Record<GestureState, { label: string; copy: string }> = {
  ready: { label: 'READY', copy: 'Show your writing hand to begin' },
  writing: { label: 'WRITING', copy: 'Writing in progress…' },
  processing: { label: 'PROCESSING', copy: 'Recognizing your word…' },
  recognized: { label: 'RECOGNIZED', copy: 'Word recognized' },
  low_confidence: { label: 'UNRECOGNIZED', copy: 'Low confidence / Unclear handwriting. Please try again.' },
};

export function StatusIndicator({ gestureState, recognizedWord, connectionStatus }: StatusIndicatorProps) {
  const state = stateCopy[gestureState] || stateCopy.ready;
  const Icon = gestureState === 'processing' ? LoaderCircle :
               gestureState === 'recognized' ? Check :
               gestureState === 'writing' ? Sparkles :
               gestureState === 'low_confidence' ? AlertTriangle : Radio;

  return (
    <section className={`status-card status-${gestureState}`}>
      <div className="status-icon">
        <Icon size={19} className={gestureState === 'processing' ? 'animate-spin' : ''} />
      </div>
      <div className="status-copy">
        <span className="eyebrow">Live status</span>
        <strong>{state.label}{recognizedWord && gestureState === 'recognized' ? ` · ${recognizedWord}` : ''}</strong>
        <p>{state.copy}{recognizedWord && gestureState === 'recognized' ? `: ${recognizedWord}` : ''}</p>
      </div>
      <div className="status-connection">
        <Wifi size={14} />
        <span>{connectionStatus === 'connected' ? 'CONNECTED' : connectionStatus === 'connecting' ? 'CONNECTING' : 'OFFLINE'}</span>
      </div>
    </section>
  );
}
