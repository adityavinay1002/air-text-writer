import { Camera, CameraOff, Hand, Maximize2, MoreHorizontal, ScanLine, Sparkles, Play, Square } from 'lucide-react';
import type { CameraStatus, GestureState } from '@/types';
import { API_ENDPOINTS } from '@/config';

interface CameraPanelProps {
  cameraStatus: CameraStatus;
  gestureState: GestureState;
  onStartCamera: () => void;
  onStopCamera: () => void;
}

export function CameraPanel({
  cameraStatus,
  gestureState,
  onStartCamera,
  onStopCamera,
}: CameraPanelProps) {
  const isCameraActive = cameraStatus === 'active';
  const isStarting = cameraStatus === 'starting';
  const isStopping = cameraStatus === 'stopping';

  const stateLabel = gestureState === 'writing' ? 'Writing in progress' :
                     gestureState === 'processing' ? 'Processing handwriting' :
                     gestureState === 'recognized' ? 'Word recognized' : 'Ready to write';

  return (
    <section className="camera-panel panel-surface">
      <div className="panel-heading">
        <div>
          <div className="eyebrow">
            <span className={`live-dot ${isCameraActive ? 'active' : 'offline'}`} />
            Live Backend Stream
          </div>
          <h2>Air-writing studio</h2>
        </div>
        <div className="panel-heading-actions">
          {!isCameraActive ? (
            <button
              onClick={onStartCamera}
              disabled={isStarting}
              className="primary-button"
              style={{ padding: '6px 14px', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#10b981', color: '#000', fontWeight: 600, borderRadius: '6px', border: 'none', cursor: 'pointer' }}
            >
              <Play size={14} fill="currentColor" /> {isStarting ? 'Starting...' : 'START CAMERA'}
            </button>
          ) : (
            <button
              onClick={onStopCamera}
              disabled={isStopping}
              className="secondary-button"
              style={{ padding: '6px 14px', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#ef4444', color: '#fff', fontWeight: 600, borderRadius: '6px', border: 'none', cursor: 'pointer' }}
            >
              <Square size={13} fill="currentColor" /> {isStopping ? 'Stopping...' : 'STOP CAMERA'}
            </button>
          )}
          <button className="mini-icon"><Maximize2 size={15} /></button>
          <button className="mini-icon"><MoreHorizontal size={16} /></button>
        </div>
      </div>

      <div className="camera-stage" style={{ position: 'relative', overflow: 'hidden', minHeight: '260px' }}>
        {isCameraActive ? (
          <img
            src={API_ENDPOINTS.CAMERA_STREAM}
            alt="Live OpenCV CV Feed"
            onLoad={() => console.log(`[AirWrite UI] Live Stream frame loaded: ${API_ENDPOINTS.CAMERA_STREAM}`)}
            onError={(e) => console.error(`[AirWrite UI] Stream load error from ${API_ENDPOINTS.CAMERA_STREAM}:`, e)}
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', borderRadius: '10px' }}
          />
        ) : (
          <div className="camera-ghost">
            <CameraOff size={38} strokeWidth={1.2} />
            <span>Camera Stopped</span>
            <small>Click [ START CAMERA ] to open live Python feed</small>
          </div>
        )}

        <div className="camera-grid" />
        <div className="corner corner-tl" /><div className="corner corner-tr" />
        <div className="corner corner-bl" /><div className="corner corner-br" />

        {isCameraActive && (
          <>
            <div className="tracking-frame"><ScanLine size={17} /><span>Tracking zone</span></div>
            <div className="camera-top-label"><span className="capture-indicator" /> 1080p <span className="separator">·</span> 30 FPS</div>
            <div className="camera-bottom-label"><Hand size={14} /> Hand tracking active</div>
            <div className="camera-state"><Sparkles size={15} /><span>{stateLabel}</span></div>
          </>
        )}
      </div>

      <div className="camera-footer">
        <div className="camera-footer-status">
          <span className="success-check" style={{ background: isCameraActive ? '#10b981' : '#64748b' }}>
            <Camera size={11} color="#000" />
          </span>
          {isCameraActive ? 'Python OpenCV Feed Connected' : 'Camera Standby'}
        </div>
        <div className="camera-footer-meta">Frame quality <strong>Excellent</strong></div>
      </div>
    </section>
  );
}
