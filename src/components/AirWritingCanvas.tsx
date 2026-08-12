import { Crosshair, PenLine, WandSparkles } from 'lucide-react';
import type { GestureState, Point } from '@/types';

interface AirWritingCanvasProps {
  trajectory: Point[];
  strokes?: Point[][];
  gestureState: GestureState;
  recognizedWord: string;
}

export function AirWritingCanvas({
  strokes = [],
  gestureState,
  recognizedWord,
}: AirWritingCanvasProps) {
  const isActive = gestureState === 'writing' || gestureState === 'processing';

  // Convert pixel stroke coordinates to SVG path string
  const renderStrokePath = (pts: Point[]) => {
    if (!pts || pts.length === 0) return '';
    const d = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${(p.x / 1280) * 360} ${(p.y / 720) * 160}`).join(' ');
    return d;
  };

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

        <svg viewBox="0 0 360 160" preserveAspectRatio="none" className="trajectory-svg" aria-label="Air writing trajectory">
          {strokes && strokes.map((s, idx) => (
            <g key={idx}>
              <path d={renderStrokePath(s)} className="trajectory-glow" style={{ stroke: '#00e5ff', strokeWidth: 6 }} />
              <path d={renderStrokePath(s)} className="trajectory-line" style={{ stroke: '#fff', strokeWidth: 3 }} />
            </g>
          ))}
        </svg>

        <div className="crosshair"><Crosshair size={16} /><span>fingertip</span></div>
        <div className="canvas-empty-copy">
          <WandSparkles size={17} />
          <span>{recognizedWord ? `Recognized “${recognizedWord}”` : 'Write a complete word in the air'}</span>
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
