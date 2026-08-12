import { ArrowRight, Film, LoaderCircle } from 'lucide-react';
import type { Movie } from '@/types';
import { MovieCard } from '@/components/MovieCard';

interface SearchResultsProps {
  movies: Movie[];
  query: string;
  isLoading?: boolean;
}

export function SearchResults({ movies, query, isLoading = false }: SearchResultsProps) {
  return (
    <section className="results-section">
      <div className="section-title-row results-heading">
        <div>
          <div className="eyebrow"><Film size={13} /> Curated for you</div>
          <h3>{query ? `Results for “${query}”` : 'Featured on AirWrite TV'}</h3>
        </div>
        <button className="view-all">View all <ArrowRight size={15} /></button>
      </div>

      {isLoading ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', color: '#38bdf8', gap: '10px' }}>
          <LoaderCircle size={24} className="animate-spin" />
          <span>Searching TV & movie databases...</span>
        </div>
      ) : movies.length > 0 ? (
        <div className="movie-grid">
          {movies.map((movie, index) => (
            <MovieCard movie={movie} featured={index === 0} key={`${movie.title}-${index}`} />
          ))}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '180px', color: '#94a3b8', gap: '8px', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', padding: '24px' }}>
          <Film size={32} />
          <strong style={{ color: '#e2e8f0' }}>No titles found for “{query}”</strong>
          <small>Try writing another show or movie title in the air</small>
        </div>
      )}
    </section>
  );
}
