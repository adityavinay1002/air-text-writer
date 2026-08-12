import { Play, Plus, Star } from 'lucide-react';
import type { Movie } from '@/types';

interface MovieCardProps { movie: Movie; featured?: boolean; }

export function MovieCard({ movie, featured }: MovieCardProps) { return <article className={`movie-card ${featured ? 'featured' : ''}`}><div className="poster" style={{ background: `linear-gradient(145deg, ${movie.accent} 0%, #111827 78%)` }}><div className="poster-noise" /><div className="poster-title">{movie.poster}</div><div className="poster-actions"><button aria-label={`Play ${movie.title}`}><Play size={15} fill="currentColor" /></button><button aria-label={`Add ${movie.title}`}><Plus size={16} /></button></div><span className="platform-badge">{movie.platform}</span></div><div className="movie-info"><div className="movie-title-row"><h4>{movie.title}</h4><span className="rating"><Star size={11} fill="currentColor" /> {movie.rating}</span></div><p>{movie.year} <span>·</span> {movie.genre}</p></div></article>; }
