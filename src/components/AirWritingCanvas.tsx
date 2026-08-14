import { Crosshair, PenLine, WandSparkles } from 'lucide-react';
import type { GestureState, Point } from '@/types';

interface AirWritingCanvasProps {
  trajectory?: Point[];
  strokes?: Point[][];
  gestureState: GestureState;
  recognizedWord: string;
  croppedImageBase64?: string;
}

export function AirWritingCanvas({
  strokes = [],
  gestureState,
  recognizedWord,
  croppedImageBase64,
}: AirWritingCanvasProps) {
  const isActive = gestureState === 'writing' || gestureState === 'processing';

  // Convert pixel stroke coordinates to SVG path string
  const renderStrokePath = (pts: Point[]) => {
    if (!pts || pts.length === 0) return '';
    const d = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${(p.x / 1280) * 360} ${(p.y / 720) * 160}`).join(' ');
    return d;
  };

  const hasStrokes = strokes && strokes.length > 0;

  return (
    <section className="writing-panel panel-surface">
      <div className="panel-heading">
        <div>
          <div className="eyebrow"><PenLine size={13} /> Input visualization</div>
          <h2>Trajectory canvas</h2>
        </div>
        <div className={`canvas-state ${isActive ? 'active' : ''}`}>
          <span /> {isActive ? 'Capturing' : 'Standing by'}
        </div>
      </div>
      
      <div className="trajectory-canvas">
        <div className="canvas-grid" />
        <div className="axis-label x">x-axis</div>
        <div className="axis-label y">y-axis</div>

        {hasStrokes && (
          <svg viewBox="0 0 360 160" preserveAspectRatio="none" className="trajectory-svg" aria-label="Air writing trajectory">
            {strokes.map((s, idx) => (
              <g key={idx}>
                <path
                  d={renderStrokePath(s)}
                  className="trajectory-glow"
                  style={{ stroke: '#00e5ff', strokeWidth: 6, fill: 'none' }}
                />
                <path
                  d={renderStrokePath(s)}
                  className="trajectory-line"
                  style={{ stroke: '#ffffff', strokeWidth: 3, fill: 'none', strokeDasharray: 'none', animation: 'none' }}
                />
              </g>
            ))}
          </svg>
        )}

        {!hasStrokes && croppedImageBase64 && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
            <img
              src={`data:image/png;base64,${croppedImageBase64}`}
              alt="Handwriting Canvas Capture"
              style={{ maxHeight: '120px', maxWidth: '80%', borderRadius: '8px', border: '1px solid rgba(0, 229, 255, 0.3)', boxShadow: '0 0 20px rgba(0, 229, 255, 0.15)', background: '#fff' }}
            />
          </div>
        )}

        <div className="crosshair"><Crosshair size={16} /><span>fingertip</span></div>
        <div className="canvas-empty-copy">
          <WandSparkles size={17} />
          <span>{recognizedWord ? `Recognized “${recognizedWord}”` : hasStrokes ? 'Strokes captured' : 'Write a complete word in the air'}</span>
        </div>
      </div>

      <div className="canvas-footer">
        <div><span className="metric-label">STROKES</span><strong>{strokes.length}</strong></div>
        <div><span className="metric-label">MODE</span><strong>TrOCR Image</strong></div>
        <div><span className="metric-label">LATENCY</span><strong>18ms</strong></div>
      </div>
    </section>
  );
}
