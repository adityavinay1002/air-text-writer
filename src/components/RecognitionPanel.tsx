import { CheckCircle2, AlertTriangle, Sparkles, Image as ImageIcon } from 'lucide-react';
import type { GestureState } from '@/types';

interface RecognitionPanelProps {
  gestureState: GestureState;
  recognizedWord: string;
  confidence: number;
  croppedImageBase64?: string;
}

export function RecognitionPanel({
  gestureState,
  recognizedWord,
  confidence,
  croppedImageBase64,
}: RecognitionPanelProps) {
  const isProcessing = gestureState === 'processing';
  const isLowConfidence = gestureState === 'low_confidence' && !recognizedWord;
  const isRecognized = Boolean(recognizedWord) && !isProcessing;

  return (
    <section className="panel-surface" style={{ padding: '20px', borderRadius: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div className="panel-heading" style={{ margin: 0 }}>
        <div>
          <div className="eyebrow"><Sparkles size={13} /> Recognition Engine</div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>TrOCR Result Panel</h2>
        </div>
        <div className="eyebrow" style={{ fontSize: '0.75rem', padding: '4px 8px', background: 'rgba(255,255,255,0.06)', borderRadius: '6px' }}>
          microsoft/trocr-small-handwritten
        </div>
      </div>

      <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)', padding: '16px', minHeight: '130px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          {isRecognized ? (
            <div>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#10b981', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                <CheckCircle2 size={16} /> RECOGNIZED HANDWRITING
              </div>
              <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#fff', margin: '4px 0', letterSpacing: '0.05em' }}>
                {recognizedWord}
              </h1>
              <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                Confidence: <strong style={{ color: '#38bdf8' }}>{Math.round(confidence * 100)}%</strong>
              </div>
            </div>
          ) : isLowConfidence ? (
            <div>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#f59e0b', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase' }}>
                <AlertTriangle size={16} /> LOW CONFIDENCE / UNRECOGNIZED
              </div>
              <p style={{ color: '#cbd5e1', marginTop: '6px', fontSize: '0.9rem' }}>
                Handwriting was unclear or ambiguous. Please write again cleanly.
              </p>
            </div>
          ) : isProcessing ? (
            <div>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#38bdf8', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase' }}>
                PROCESSING HANDWRITING...
              </div>
              <p style={{ color: '#94a3b8', marginTop: '6px', fontSize: '0.9rem' }}>
                Running Microsoft TrOCR Vision Transformer...
              </p>
            </div>
          ) : (
            <div>
              <div style={{ color: '#64748b', fontSize: '0.85rem', textTransform: 'uppercase', fontWeight: 600 }}>
                STANDBY
              </div>
              <p style={{ color: '#94a3b8', marginTop: '4px', fontSize: '0.9rem' }}>
                Air-write a title and confirm with ✌️ gesture
              </p>
            </div>
          )}
        </div>

        {croppedImageBase64 ? (
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.7rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>
              Cropped Handwriting
            </span>
            <img
              src={`data:image/png;base64,${croppedImageBase64}`}
              alt="Cropped Handwriting Preview"
              style={{ maxHeight: '70px', maxWidth: '160px', borderRadius: '8px', border: '1px solid rgba(56, 189, 248, 0.4)', background: '#fff' }}
            />
          </div>
        ) : (
          <div style={{ width: '80px', height: '60px', borderRadius: '8px', border: '1px stroke rgba(255,255,255,0.05)', background: 'rgba(255,255,255,0.02)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569' }}>
            <ImageIcon size={24} />
          </div>
        )}
      </div>
    </section>
  );
}
