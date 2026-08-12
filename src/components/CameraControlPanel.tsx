import { Camera, CameraOff, Play, Square, Trash2, Hand, Sparkles, ScanLine, Activity } from 'lucide-react';
import type { CameraStatus, BackendStatus, GestureState } from '@/types';

interface CameraControlPanelProps {
  cameraStatus: CameraStatus;
  backendStatus: BackendStatus;
  gestureState: GestureState;
  onStartCamera: () => void;
  onStopCamera: () => void;
  onClearSession: () => void;
}

export function CameraControlPanel({
  cameraStatus,
  backendStatus,
  gestureState,
  onStartCamera,
  onStopCamera,
  onClearSession,
}: CameraControlPanelProps) {
  const isCameraActive = cameraStatus === 'active';
  const isStarting = cameraStatus === 'starting';
  const isStopping = cameraStatus === 'stopping';

  const gestureLabel = gestureState === 'writing' ? 'Writing in progress...' :
                       gestureState === 'processing' ? 'Processing handwriting...' :
                       gestureState === 'recognized' ? 'Recognition complete' : 'Ready to write';

  return (
    <section className="camera-panel panel-surface" style={{ flex: 1 }}>
      <div className="panel-heading">
        <div>
          <div className="eyebrow">
            <span className={`live-dot ${isCameraActive ? 'active' : 'offline'}`} />
            AirWrite Studio Control
          </div>
          <h2>Webcam & CV Engine</h2>
        </div>
        <div className="panel-heading-actions">
          {!isCameraActive ? (
            <button
              onClick={onStartCamera}
              disabled={isStarting}
              className="primary-button"
              style={{ padding: '8px 16px', display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#10b981', color: '#000', fontWeight: 600, borderRadius: '8px', border: 'none', cursor: 'pointer' }}
            >
              <Play size={15} fill="currentColor" /> {isStarting ? 'Starting...' : 'START CAMERA'}
            </button>
          ) : (
            <button
              onClick={onStopCamera}
              disabled={isStopping}
              className="secondary-button"
              style={{ padding: '8px 16px', display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#ef4444', color: '#fff', fontWeight: 600, borderRadius: '8px', border: 'none', cursor: 'pointer' }}
            >
              <Square size={14} fill="currentColor" /> {isStopping ? 'Stopping...' : 'STOP CAMERA'}
            </button>
          )}

          <button
            onClick={onClearSession}
            className="mini-icon"
            title="Clear canvas"
            style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.06)', color: '#ccc', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', cursor: 'pointer' }}
          >
            <Trash2 size={15} />
          </button>
        </div>
      </div>

      <div className="camera-stage" style={{ minHeight: '180px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
        <div className="camera-grid" />
        <div className="corner corner-tl" /><div className="corner corner-tr" />
        <div className="corner corner-bl" /><div className="corner corner-br" />

        {isCameraActive ? (
          <div style={{ textAlign: 'center', zIndex: 2 }}>
            <Activity size={36} className="text-emerald-400 animate-pulse" style={{ color: '#10b981', margin: '0 auto 10px' }} />
            <span style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', display: 'block' }}>
              CV Camera Active — Python Backend
            </span>
            <small style={{ color: '#94a3b8', marginTop: '4px', display: 'block' }}>
              OpenCV 1280x720 window active · Position writing hand in frame
            </small>
          </div>
        ) : (
          <div className="camera-ghost">
            <CameraOff size={38} strokeWidth={1.2} />
            <span>Camera Stopped</span>
            <small>Click [ START CAMERA ] to begin air-writing</small>
          </div>
        )}

        {isCameraActive && (
          <>
            <div className="tracking-frame"><ScanLine size={17} /><span>Tracking zone</span></div>
            <div className="camera-top-label"><span className="capture-indicator" /> 1080p <span className="separator">·</span> 30 FPS</div>
            <div className="camera-bottom-label"><Hand size={14} /> Hand tracking active</div>
            <div className="camera-state"><Sparkles size={15} /><span>{gestureLabel}</span></div>
          </>
        )}
      </div>

      <div className="camera-footer">
        <div className="camera-footer-status">
          <span className="success-check" style={{ background: isCameraActive ? '#10b981' : '#64748b' }}>
            <Camera size={11} color="#000" />
          </span>
          {isCameraActive ? 'Webcam active' : 'Webcam standby'}
        </div>
        <div className="camera-footer-meta">
          Backend: <strong style={{ color: backendStatus === 'connected' ? '#10b981' : '#f59e0b' }}>{backendStatus.toUpperCase()}</strong>
        </div>
      </div>
    </section>
  );
}
