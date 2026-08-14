import { Play, Sparkles, CheckCircle2, Search, HelpCircle, Hand } from 'lucide-react';

export function HowItWorks() {
  const steps = [
    {
      step: '01',
      title: 'Start the CV Camera',
      desc: 'Click [ START CAMERA ] in the AirWrite Studio. Python initializes your webcam and hand tracking.',
      icon: Play,
      badge: 'SETUP'
    },
    {
      step: '02',
      title: 'Air-Write Title (☝️ WRITE)',
      desc: 'Extend your index finger to write in the air. Glowing strokes accumulate on the trajectory canvas.',
      icon: Hand,
      badge: '☝️ GESTURE'
    },
    {
      step: '03',
      title: 'Pause Between Strokes (🖐️ PEN_UP)',
      desc: 'Show open palm (🖐️) to pause stroke recording / complete letter. Make a fist (✊) to clear.',
      icon: Sparkles,
      badge: '🖐️ GESTURE'
    },
    {
      step: '04',
      title: 'Confirm & Recognize (✌️ CONFIRM)',
      desc: 'Extend index and middle fingers to confirm. Microsoft TrOCR Vision-Transformer reads your handwriting.',
      icon: CheckCircle2,
      badge: '✌️ GESTURE'
    },
    {
      step: '05',
      title: 'Automated Search Results',
      desc: 'The recognized text automatically populates the search bar and loads real streaming movies.',
      icon: Search,
      badge: 'TV SEARCH'
    }
  ];

  return (
    <section className="panel-surface" style={{ padding: '32px', borderRadius: '16px', margin: '20px 0' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <div style={{ padding: '10px', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '12px', color: '#38bdf8' }}>
          <HelpCircle size={24} />
        </div>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff', margin: 0 }}>
            How AirWrite TV Search Works
          </h2>
          <p style={{ color: '#94a3b8', margin: '4px 0 0 0', fontSize: '0.95rem' }}>
            Follow these simple steps for hands-free TV discovery
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        {steps.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.step}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '12px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                justify: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8', letterSpacing: '0.05em' }}>
                    STEP {item.step}
                  </span>
                  <span style={{ fontSize: '0.7rem', padding: '2px 8px', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', borderRadius: '4px', fontWeight: 600 }}>
                    {item.badge}
                  </span>
                </div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#fff', marginBottom: '8px' }}>
                  {item.title}
                </h3>
                <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5, margin: 0 }}>
                  {item.desc}
                </p>
              </div>
              <div style={{ marginTop: '16px', color: '#64748b' }}>
                <Icon size={20} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
