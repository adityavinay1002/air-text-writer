import { useState, useEffect, useRef, useCallback } from 'react';
import { Header, type NavTab } from '@/components/Header';
import { CameraPanel } from '@/components/CameraPanel';
import { RecognitionPanel } from '@/components/RecognitionPanel';
import { AirWritingCanvas } from '@/components/AirWritingCanvas';
import { SearchBar } from '@/components/SearchBar';
import { ModeSelector } from '@/components/ModeSelector';
import { StatusIndicator } from '@/components/StatusIndicator';
import { GestureGuide } from '@/components/GestureGuide';
import { SearchResults } from '@/components/SearchResults';
import { ControlButtons } from '@/components/ControlButtons';
import { HowItWorks } from '@/components/HowItWorks';
import { HistoryPanel, type HistoryItem } from '@/components/HistoryPanel';
import { API_ENDPOINTS } from '@/config';
import type { AirWriteSession, Movie, Point } from '@/types';

const defaultMovies: Movie[] = [
  { title: 'Avatar', year: '2009', genre: 'Sci-fi · Action', platform: '4K UHD', accent: '#4b8d9b', poster: 'https://static.tvmaze.com/uploads/images/medium_portrait/633/1582667.jpg', rating: '8.0' },
  { title: 'Avatar: The Way of Water', year: '2022', genre: 'Sci-fi · Adventure', platform: 'Premium', accent: '#256f85', poster: 'https://static.tvmaze.com/uploads/images/medium_portrait/595/1489366.jpg', rating: '7.6' },
  { title: 'Dune: Part Two', year: '2024', genre: 'Sci-fi · Drama', platform: 'New', accent: '#a36b3d', poster: 'https://static.tvmaze.com/uploads/images/medium_portrait/168/420181.jpg', rating: '8.7' },
  { title: 'Interstellar', year: '2014', genre: 'Sci-fi · Drama', platform: '4K UHD', accent: '#31567b', poster: 'https://static.tvmaze.com/uploads/images/medium_portrait/79/199224.jpg', rating: '8.7' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('search');
  const [session, setSession] = useState<AirWriteSession>({
    gestureState: 'ready',
    backendStatus: 'disconnected',
    cameraStatus: 'stopped',
    recognizedWord: '',
    recognitionConfidence: 0.0,
    searchQuery: '',
    selectedMode: 'image',
  });

  const [strokes, setStrokes] = useState<Point[][]>([]);
  const [movies, setMovies] = useState<Movie[]>(defaultMovies);
  const [isLoadingSearch, setIsLoadingSearch] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>(() => {
    try {
      const saved = localStorage.getItem('airwrite_search_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const wsRef = useRef<WebSocket | null>(null);

  const saveHistoryItem = (query: string, confidence?: number) => {
    if (!query || !query.trim()) return;
    const newItem: HistoryItem = {
      id: Date.now().toString(),
      query: query.toUpperCase(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      confidence
    };
    setHistory((prev) => {
      const updated = [newItem, ...prev.filter((i) => i.query !== newItem.query)].slice(0, 20);
      try {
        localStorage.setItem('airwrite_search_history', JSON.stringify(updated));
      } catch (e) {
        console.warn('Failed to save history to localStorage:', e);
      }
      return updated;
    });
  };

  const handleClearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem('airwrite_search_history');
    } catch (e) {
      console.warn('Failed to clear history from localStorage:', e);
    }
  };

  const updateSession = <K extends keyof AirWriteSession>(key: K, value: AirWriteSession[K]) => {
    setSession((current) => ({ ...current, [key]: value }));
  };

  const fetchMovies = useCallback(async (query: string) => {
    if (!query || !query.trim()) {
      setMovies(defaultMovies);
      return;
    }

    setIsLoadingSearch(true);
    console.log(`[AirWrite] Search request sent for: '${query}'`);
    try {
      const res = await fetch(API_ENDPOINTS.SEARCH(query));
      if (res.ok) {
        const data = await res.json();
        console.log(`[AirWrite] Search results received for '${query}':`, data.count);
        if (data.movies && data.movies.length > 0) {
          setMovies(data.movies);
        } else {
          setMovies([]);
        }
      }
    } catch (e) {
      console.warn('[AirWrite] Backend REST search error:', e);
    } finally {
      setIsLoadingSearch(false);
    }
  }, []);

  // Backend Health Checker Loop
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(API_ENDPOINTS.HEALTH);
        if (res.ok) {
          const data = await res.json();
          setSession((prev) => ({
            ...prev,
            backendStatus: 'connected',
            cameraStatus: data.camera_active ? 'active' : 'stopped'
          }));
        } else {
          setSession((prev) => ({ ...prev, backendStatus: 'disconnected' }));
        }
      } catch {
        setSession((prev) => ({ ...prev, backendStatus: 'disconnected' }));
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket Connection Manager
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimer: any = null;

    const connectWS = () => {
      if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
        return;
      }

      console.log(`[AirWrite] Connecting to backend WebSocket at ${API_ENDPOINTS.WEBSOCKET}...`);
      ws = new WebSocket(API_ENDPOINTS.WEBSOCKET);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[AirWrite] Backend connected & WebSocket established!');
        setSession((prev) => ({ ...prev, backendStatus: 'connected' }));
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);

          if (msg.type === 'init') {
            console.log('[AirWrite] WebSocket Handshake received:', msg);
            setSession((prev) => ({
              ...prev,
              backendStatus: 'connected',
              cameraStatus: msg.camera_active ? 'active' : 'stopped',
              gestureState: msg.gesture_state || 'ready'
            }));
          } else if (msg.type === 'camera_status') {
            console.log('[AirWrite] Camera status update:', msg.camera_active);
            setSession((prev) => ({
              ...prev,
              cameraStatus: msg.camera_active ? 'active' : 'stopped'
            }));
          } else if (msg.type === 'status') {
            console.log(`[AirWrite] Gesture: ${msg.gesture_state}`);
            setSession((prev) => ({
              ...prev,
              gestureState: msg.gesture_state
            }));
            if (msg.strokes) {
              setStrokes(msg.strokes.map((s: number[][]) => s.map(([x, y]) => ({ x, y }))));
            }
          } else if (msg.type === 'trajectory_update') {
            if (msg.strokes) {
              setStrokes(msg.strokes.map((s: number[][]) => s.map(([x, y]) => ({ x, y }))));
            }
          } else if (msg.type === 'recognition_result') {
            console.log('[AirWrite] Recognition result received:', msg);
            if (msg.status === 'RECOGNIZED' && msg.text) {
              const text = msg.text.toUpperCase();
              const conf = msg.confidence || 0.85;
              setSession((prev) => ({
                ...prev,
                recognizedWord: text,
                searchQuery: text,
                recognitionConfidence: conf,
                gestureState: 'recognized',
                croppedImageBase64: msg.cropped_image_base64
              }));
              saveHistoryItem(text, conf);
              fetchMovies(text);
            } else if (msg.status === 'LOW_CONFIDENCE') {
              setSession((prev) => ({
                ...prev,
                gestureState: 'low_confidence',
                croppedImageBase64: msg.cropped_image_base64
              }));
            }
          } else if (msg.type === 'clear') {
            setStrokes([]);
            setSession((prev) => ({
              ...prev,
              recognizedWord: '',
              croppedImageBase64: undefined,
              gestureState: 'ready'
            }));
          }
        } catch (e) {
          console.error('[AirWrite] Error parsing WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        wsRef.current = null;
        console.warn('[AirWrite] WebSocket disconnected. Reconnecting in 3s...');
        setSession((prev) => ({ ...prev, backendStatus: 'disconnected' }));
        reconnectTimer = setTimeout(connectWS, 3000);
      };

      ws.onerror = (err) => {
        console.error('[AirWrite] WebSocket connection error:', err);
        setSession((prev) => ({ ...prev, backendStatus: 'error' }));
        ws?.close();
      };
    };

    connectWS();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, [fetchMovies]);

  // REST Camera Controls
  const handleStartCamera = async () => {
    console.log('[AirWrite] START CAMERA clicked');
    updateSession('cameraStatus', 'starting');
    try {
      console.log(`[AirWrite] Sending POST request to ${API_ENDPOINTS.CAMERA_START}...`);
      const res = await fetch(API_ENDPOINTS.CAMERA_START, { method: 'POST' });
      const data = await res.json();
      console.log('[AirWrite] Backend camera start response received:', data);
      console.log('[AirWrite] camera_active value:', data.camera_active);
      if (res.ok && (data.status === 'started' || data.status === 'already_running' || data.camera_active)) {
        console.log(`[AirWrite] Stream URL loading: ${API_ENDPOINTS.CAMERA_STREAM}`);
        updateSession('cameraStatus', 'active');
      } else {
        console.error('[AirWrite] Failed to start camera:', data.message || data.status);
        updateSession('cameraStatus', 'stopped');
      }
    } catch (e) {
      console.error('[AirWrite] Failed to start camera via REST:', e);
      updateSession('cameraStatus', 'stopped');
    }
  };

  const handleStopCamera = async () => {
    console.log('[AirWrite] STOP CAMERA clicked');
    updateSession('cameraStatus', 'stopping');
    try {
      console.log(`[AirWrite] Sending POST request to ${API_ENDPOINTS.CAMERA_STOP}...`);
      const res = await fetch(API_ENDPOINTS.CAMERA_STOP, { method: 'POST' });
      const data = await res.json();
      console.log('[AirWrite] Backend camera stop response received:', data);
      if (res.ok) {
        updateSession('cameraStatus', 'stopped');
      }
    } catch (e) {
      console.error('[AirWrite] Failed to stop camera via REST:', e);
      updateSession('cameraStatus', 'stopped');
    }
  };

  const handleClearSession = async () => {
    console.log('[AirWrite] Clear session requested');
    setStrokes([]);
    setSession((prev) => ({
      ...prev,
      searchQuery: '',
      recognizedWord: '',
      gestureState: 'ready',
      croppedImageBase64: undefined
    }));
    setMovies(defaultMovies);

    try {
      await fetch(API_ENDPOINTS.SESSION_CLEAR, { method: 'POST' });
    } catch (e) {
      console.warn('[AirWrite] Failed to send clear request to REST backend:', e);
    }
  };

  const handleManualSearch = () => {
    if (session.searchQuery) {
      console.log('[AirWrite] Manual search executed for:', session.searchQuery);
      saveHistoryItem(session.searchQuery);
      setSession((prev) => ({ ...prev, gestureState: 'recognized', recognizedWord: prev.searchQuery.toUpperCase() }));
      fetchMovies(session.searchQuery);
    }
  };

  const handleSelectHistoryQuery = (query: string) => {
    setActiveTab('search');
    updateSession('searchQuery', query.toUpperCase());
    updateSession('recognizedWord', query.toUpperCase());
    fetchMovies(query);
  };

  const handleBackspace = () => {
    updateSession('searchQuery', session.searchQuery.slice(0, -1));
  };

  return (
    <div className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      
      <Header
        backendStatus={session.backendStatus}
        cameraStatus={session.cameraStatus}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      
      <main className="app-main">
        <div className="welcome-row">
          <div>
            <p className="overline">AIRWRITE OS <span /> REWORK 06</p>
            <h1>Write what you want to watch in the air.</h1>
            <p className="welcome-copy">Hands-free discovery with live camera, MediaPipe tracking & Microsoft TrOCR.</p>
          </div>
          <div className="session-time">
            <span>BACKEND STATUS</span>
            <strong style={{ color: session.backendStatus === 'connected' ? '#10b981' : '#f59e0b' }}>
              {session.backendStatus.toUpperCase()}
            </strong>
          </div>
        </div>

        {/* Tab View Routing */}
        {activeTab === 'how-it-works' ? (
          <HowItWorks />
        ) : activeTab === 'history' ? (
          <HistoryPanel
            history={history}
            onSelectQuery={handleSelectHistoryQuery}
            onClearHistory={handleClearHistory}
          />
        ) : (
          <>
            {/* Studio Grid: Live Camera Stream & Air-Writing Canvas */}
            <div className="studio-grid">
              <CameraPanel
                cameraStatus={session.cameraStatus}
                gestureState={session.gestureState}
                onStartCamera={handleStartCamera}
                onStopCamera={handleStopCamera}
              />

              <AirWritingCanvas
                trajectory={session.trajectory}
                strokes={strokes}
                gestureState={session.gestureState}
                recognizedWord={session.recognizedWord}
              />
            </div>

            {/* TrOCR Recognition Result Card */}
            <RecognitionPanel
              gestureState={session.gestureState}
              recognizedWord={session.recognizedWord}
              confidence={session.recognitionConfidence}
              croppedImageBase64={session.croppedImageBase64}
            />

            {/* Main Search Bar */}
            <SearchBar
              query={session.searchQuery}
              recognizedWord={session.recognizedWord}
              onQueryChange={(value) => updateSession('searchQuery', value.toUpperCase())}
              onClear={handleClearSession}
              onSearch={handleManualSearch}
            />

            <div className="workspace-grid">
              <div>
                <ModeSelector
                  selectedMode={session.selectedMode}
                  onModeChange={(mode) => updateSession('selectedMode', mode)}
                />
                <ControlButtons
                  onClear={handleClearSession}
                  onBackspace={handleBackspace}
                  onSearch={handleManualSearch}
                />
              </div>
              <div>
                <StatusIndicator
                  gestureState={session.gestureState}
                  recognizedWord={session.recognizedWord}
                  connectionStatus={session.backendStatus === 'connected' ? 'connected' : 'connecting'}
                />
                <GestureGuide />
              </div>
            </div>

            {/* Real Movie/TV Search Results */}
            <SearchResults
              movies={movies}
              query={session.searchQuery}
              isLoading={isLoadingSearch}
            />
          </>
        )}
      </main>

      <footer className="app-footer">
        <span><span className="footer-mark" /> AirWrite TV Search</span>
        <span>Built for the future of hands-free discovery <span className="footer-separator">·</span> v1.0.0</span>
      </footer>
    </div>
  );
}
