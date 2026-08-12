import { Check, Search, Sparkles, X } from 'lucide-react';

interface SearchBarProps {
  query: string;
  recognizedWord: string;
  onQueryChange: (value: string) => void;
  onClear: () => void;
  onSearch: () => void;
}

export function SearchBar({ query, recognizedWord, onQueryChange, onClear, onSearch }: SearchBarProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <section className="search-section">
      <div className="search-label">
        <span className="eyebrow"><Sparkles size={13} /> Your next watch</span>
        <span className="query-label">{recognizedWord ? 'Air-written query' : 'Type or write to search'}</span>
      </div>
      <div className="search-shell">
        <Search size={22} className="search-icon" />
        <input
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search movies & TV shows..."
          aria-label="Search movies & TV shows"
        />
        {recognizedWord && (
          <div className="recognized-chip">
            <Check size={13} /> <span>{recognizedWord}</span>
          </div>
        )}
        {query && (
          <button className="clear-input" onClick={onClear} aria-label="Clear search">
            <X size={16} />
          </button>
        )}
        <button className="search-submit" onClick={onSearch} aria-label="Submit search">
          <Search size={17} /> Search
        </button>
      </div>
      <div className="search-hint">
        <span>Write a title in the air or type to search</span>
        <span className="hint-key">ENTER ↵</span>
      </div>
    </section>
  );
}
