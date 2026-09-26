import React, { useEffect, useState } from 'react';
import { api, type ScenarioItem } from '../api/client';
import { 
  MapPin, Droplets, AlertOctagon, Disc, 
  WifiOff, Compass 
} from 'lucide-react';

export const ScenariosView: React.FC = () => {
  const [scenarios, setScenarios] = useState<ScenarioItem[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string>('');

  useEffect(() => {
    api.getScenarios(categoryFilter || undefined)
      .then(setScenarios)
      .catch(console.error);
  }, [categoryFilter]);

  const categories = [
    { id: 'DENSE_TRAFFIC', label: 'Dense Traffic', icon: AlertOctagon, color: '#f59e0b' },
    { id: 'ROAD_CONDITIONS', label: 'Road Conditions', icon: Disc, color: '#ec4899' },
    { id: 'MONSOON', label: 'Monsoon Hazards', icon: Droplets, color: '#06b6d4' },
    { id: 'INTERSECTIONS', label: 'Intersections', icon: Compass, color: '#a855f7' },
    { id: 'TYRE_CONDITIONS', label: 'Tyre Conditions', icon: Disc, color: '#10b981' },
    { id: 'SENSOR_FAILURES', label: 'Sensor Failures', icon: WifiOff, color: '#ef4444' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-cyan">OPERATIONAL DESIGN DOMAIN</span>
              <span className="badge badge-muted">PUNE / INDIA REAL-WORLD CATALOG</span>
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff' }}>
              Indian Operational Environment Scenarios
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>
              Curated library of realistic road, weather, traffic, and chassis degradation stress vectors.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-pass" style={{ fontSize: '12px', padding: '6px 12px' }}>
              {scenarios.length} Scenarios Available
            </span>
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '10px' }}>
        <button
          onClick={() => setCategoryFilter('')}
          className="btn-secondary"
          style={{
            justifyContent: 'center',
            borderColor: !categoryFilter ? 'var(--accent-cyan)' : 'var(--border-subtle)',
            background: !categoryFilter ? 'rgba(6, 182, 212, 0.12)' : 'var(--bg-card)'
          }}
        >
          All Categories ({scenarios.length})
        </button>

        {categories.map((cat) => {
          const Icon = cat.icon;
          const isActive = categoryFilter === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setCategoryFilter(cat.id)}
              className="btn-secondary"
              style={{
                justifyContent: 'center',
                borderColor: isActive ? cat.color : 'var(--border-subtle)',
                background: isActive ? `${cat.color}20` : 'var(--bg-card)',
                color: isActive ? '#ffffff' : 'var(--text-main)'
              }}
            >
              <Icon size={14} color={cat.color} />
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Scenario Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '16px' }}>
        {scenarios.map((scen) => (
          <div 
            key={scen.id} 
            className="glass-panel" 
            style={{ 
              padding: '20px', 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'space-between',
              gap: '14px',
              borderLeft: `4px solid ${
                scen.category === 'MONSOON' ? '#06b6d4' :
                scen.category === 'DENSE_TRAFFIC' ? '#f59e0b' :
                scen.category === 'ROAD_CONDITIONS' ? '#ec4899' :
                scen.category === 'INTERSECTIONS' ? '#a855f7' :
                scen.category === 'TYRE_CONDITIONS' ? '#10b981' : '#ef4444'
              }`
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="badge badge-muted font-mono">{scen.code}</span>
                <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)' }}>
                  {scen.category}
                </span>
              </div>

              <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#ffffff', marginBottom: '8px', lineHeight: 1.4 }}>
                {scen.name}
              </h3>

              <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: '12px' }}>
                {scen.description}
              </p>

              {scen.pune_context && (
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', fontSize: '12px', color: '#93c5fd', background: 'rgba(59,130,246,0.1)', padding: '8px 10px', borderRadius: '4px', marginBottom: '12px' }}>
                  <MapPin size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{scen.pune_context}</span>
                </div>
              )}
            </div>

            {/* Parameter Badges */}
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', color: 'var(--text-faint)' }}>
              <div>
                Friction: <span className="font-mono" style={{ color: scen.road_friction < 0.6 ? 'var(--status-fail)' : 'var(--text-main)' }}>&mu; = {scen.road_friction}</span>
              </div>
              <div>
                Vis. Loss: <span className="font-mono">{scen.visibility_reduction_pct}%</span>
              </div>
              <div>
                Traffic: <span className="font-mono">{scen.traffic_density}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
