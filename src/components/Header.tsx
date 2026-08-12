import { Aperture, ChevronDown, CircleHelp, Radio, Camera } from 'lucide-react';
import type { BackendStatus, CameraStatus } from '@/types';

export type NavTab = 'search' | 'how-it-works' | 'history';

interface HeaderProps {
  backendStatus: BackendStatus;
  cameraStatus: CameraStatus;
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
}

export function Header({ backendStatus, cameraStatus, activeTab, onTabChange }: HeaderProps) {
  const isBackendConnected = backendStatus === 'connected';
  const isCameraActive = cameraStatus === 'active';

  return (
    <header className="app-header">
      <div className="brand-lockup" onClick={() => onTabChange('search')} style={{ cursor: 'pointer' }}>
        <div className="brand-mark"><Aperture size={21} strokeWidth={1.8} /></div>
        <div>
          <div className="brand-name">AIRWRITE <span>TV</span></div>
          <div className="brand-tagline">Cinematic search, reimagined</div>
        </div>
      </div>

      <nav className="main-nav" aria-label="Main navigation">
        <button
          className={`nav-link ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => onTabChange('search')}
        >
          Search
        </button>
        <button
          className={`nav-link ${activeTab === 'how-it-works' ? 'active' : ''}`}
          onClick={() => onTabChange('how-it-works')}
        >
          How it works
        </button>
        <button
          className={`nav-link ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => onTabChange('history')}
        >
          History
        </button>
      </nav>

      <div className="header-actions">
        <div className={`connection-pill ${isBackendConnected ? 'connected' : ''}`}>
          <span className="status-dot" />
          <Radio size={14} />
          {isBackendConnected ? 'Backend Connected' : 'Connecting Backend...'}
        </div>
        <div
          className={`connection-pill ${isCameraActive ? 'connected' : ''}`}
          style={{ borderColor: isCameraActive ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.3)' }}
        >
          <Camera size={14} />
          {isCameraActive ? 'Camera Active' : 'Camera Stopped'}
        </div>
        <button className="icon-button" onClick={() => onTabChange('how-it-works')} aria-label="Help">
          <CircleHelp size={18} />
        </button>
        <button className="profile-button"><span>AW</span><ChevronDown size={14} /></button>
      </div>
    </header>
  );
}
