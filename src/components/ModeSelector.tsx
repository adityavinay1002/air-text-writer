import { Image, Route, Sparkles } from 'lucide-react';
import type { RecognitionMode } from '@/types';

interface ModeSelectorProps { selectedMode: RecognitionMode; onModeChange: (mode: RecognitionMode) => void; }

export function ModeSelector({ selectedMode, onModeChange }: ModeSelectorProps) {
  return <section className="mode-section"><div className="section-title-row"><div><div className="eyebrow">Recognition method</div><h3>Choose your input mode</h3></div><span className="recommended"><Sparkles size={12} /> Mode 2 recommended</span></div><div className="mode-grid"><button className={`mode-card ${selectedMode === 'image' ? 'selected' : ''}`} onClick={() => onModeChange('image')}><div className="mode-icon"><Image size={19} /></div><div className="mode-copy"><span className="mode-number">MODE 01</span><strong>Image-based recognition</strong><p>Uses the captured hand image to understand your written word.</p></div><span className="mode-radio" /></button><button className={`mode-card ${selectedMode === 'trajectory' ? 'selected' : ''}`} onClick={() => onModeChange('trajectory')}><div className="mode-icon trajectory"><Route size={19} /></div><div className="mode-copy"><span className="mode-number">MODE 02 <em>Recommended</em></span><strong>Trajectory-based recognition</strong><p>Reads the path of your fingertip for precise, fluid results.</p></div><span className="mode-radio" /></button></div></section>;
}
