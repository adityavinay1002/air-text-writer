import { Delete, Eraser, Search } from 'lucide-react';

interface ControlButtonsProps { onClear: () => void; onBackspace: () => void; onSearch: () => void; }

export function ControlButtons({ onClear, onBackspace, onSearch }: ControlButtonsProps) { return <div className="control-row"><button onClick={onClear}><Eraser size={15} /> Clear</button><button onClick={onBackspace}><Delete size={15} /> Backspace</button><button className="control-search" onClick={onSearch}><Search size={15} /> Search now</button></div>; }
