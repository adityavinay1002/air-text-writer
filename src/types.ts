export type GestureState = 'ready' | 'writing' | 'processing' | 'recognized' | 'low_confidence';
export type BackendStatus = 'connected' | 'connecting' | 'reconnecting' | 'disconnected' | 'error';
export type CameraStatus = 'active' | 'stopped' | 'starting' | 'stopping';
export type RecognitionMode = 'image' | 'trajectory';

export interface Point {
  x: number;
  y: number;
}

export interface Movie {
  title: string;
  year: string;
  genre: string;
  platform: string;
  accent: string;
  poster: string;
  rating: string;
}

export interface AirWriteSession {
  gestureState: GestureState;
  backendStatus: BackendStatus;
  cameraStatus: CameraStatus;
  recognizedWord: string;
  recognitionConfidence: number;
  searchQuery: string;
  selectedMode: RecognitionMode;
  croppedImageBase64?: string;
  pointCount?: number;
  strokeCount?: number;
}
