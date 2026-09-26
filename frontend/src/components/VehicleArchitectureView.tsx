import React, { useEffect, useState } from 'react';
import { api, type ECUItem } from '../api/client';
import { Radio, Zap, Network } from 'lucide-react';

export const VehicleArchitectureView: React.FC = () => {
  const [ecus, setEcus] = useState<ECUItem[]>([]);
  const [selectedEcu, setSelectedEcu] = useState<ECUItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getECUs()
      .then((ecuData) => {
        setEcus(ecuData);
        if (ecuData.length > 0) {
          // Default select ADAS_ECU
          const adas = ecuData.find(e => e.name === 'ADAS_ECU') || ecuData[0];
          setSelectedEcu(adas);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div style={{ color: 'var(--accent-cyan)', padding: '40px', textAlign: 'center' }}>Loading PUSV-01 Architecture Map...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Banner */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-cyan">VEHICLE TOPOLOGY</span>
              <span className="badge badge-muted">PUSV-01 COMPACT SEDAN</span>
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff' }}>
              Distributed Logical ECU Network & Signal Bus
            </h2>
          </div>
          <div style={{ display: 'flex', gap: '12px', fontSize: '13px', color: 'var(--text-muted)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--accent-cyan)' }} /> CAN-FD 2 Mbps
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#60a5fa' }} /> Ethernet 100BASE-T1
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#a855f7' }} /> LIN / Analog
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Interactive Topology Map + ECU Inspector */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px' }}>
        {/* ECU Grid Map */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Network size={16} color="var(--accent-cyan)" /> Logical ECUs (Click to Inspect)
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {ecus.map((ecu) => {
              const isSelected = selectedEcu?.id === ecu.id;
              return (
                <div
                  key={ecu.id}
                  onClick={() => setSelectedEcu(ecu)}
                  style={{
                    background: isSelected ? 'rgba(6, 182, 212, 0.12)' : 'var(--bg-secondary)',
                    border: isSelected ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease-in-out',
                    boxShadow: isSelected ? '0 0 16px rgba(6, 182, 212, 0.2)' : 'none'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div className="font-mono" style={{ fontSize: '14px', fontWeight: 700, color: isSelected ? 'var(--accent-cyan)' : '#ffffff' }}>
                      {ecu.name}
                    </div>
                    <span className="badge badge-muted" style={{ fontSize: '10px' }}>
                      {ecu.safety_integrity_level}
                    </span>
                  </div>

                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '10px' }}>
                    {ecu.subsystem} ({ecu.domain})
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-faint)' }}>
                    <span>{ecu.sensors.length} Sensors</span>
                    <span>{ecu.actuators.length} Actuators</span>
                    <span>{ecu.signals_produced.length} Signals</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Central Gateway Architecture Note */}
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '12px 16px', borderRadius: '6px', border: '1px solid var(--border-subtle)', fontSize: '12px', color: 'var(--text-muted)' }}>
            <span style={{ fontWeight: 600, color: '#ffffff' }}>GATEWAY_ECU Routing Backbone:</span> Safety frames between Chassis CAN-FD and Body CAN are arbitrated with guaranteed deterministic routing latency &le; 5 ms.
          </div>
        </div>

        {/* Selected ECU Inspector Panel */}
        {selectedEcu && (
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <span className="badge badge-cyan font-mono" style={{ fontSize: '13px' }}>
                  {selectedEcu.name}
                </span>
                <span className="badge badge-muted">Bus: {selectedEcu.bus_type}</span>
                <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
                  {selectedEcu.safety_integrity_level}
                </span>
              </div>
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#ffffff' }}>
                {selectedEcu.subsystem} Subsystem
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '6px', lineHeight: 1.5 }}>
                {selectedEcu.description}
              </p>
            </div>

            {/* Connected Sensors */}
            <div>
              <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Direct Physical Sensors ({selectedEcu.sensors.length})
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {selectedEcu.sensors.map((s) => (
                  <div key={s.id} style={{ padding: '10px 12px', background: 'var(--bg-secondary)', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Radio size={14} color="var(--accent-cyan)" />
                      <span style={{ fontSize: '13px', fontWeight: 500 }}>{s.name}</span>
                    </div>
                    <span className="badge badge-muted font-mono" style={{ fontSize: '10px' }}>{s.type}</span>
                  </div>
                ))}
                {selectedEcu.sensors.length === 0 && (
                  <div style={{ fontSize: '12px', color: 'var(--text-faint)' }}>Receives perception via CAN/Ethernet bus</div>
                )}
              </div>
            </div>

            {/* Actuators Controlled */}
            <div>
              <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Controlled Actuators ({selectedEcu.actuators.length})
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {selectedEcu.actuators.map((a) => (
                  <div key={a.id} style={{ padding: '10px 12px', background: 'var(--bg-secondary)', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Zap size={14} color="#f59e0b" />
                      <span style={{ fontSize: '13px', fontWeight: 500 }}>{a.name}</span>
                    </div>
                    <span className="badge badge-muted font-mono" style={{ fontSize: '10px' }}>{a.type}</span>
                  </div>
                ))}
                {selectedEcu.actuators.length === 0 && (
                  <div style={{ fontSize: '12px', color: 'var(--text-faint)' }}>Transmits demand signals to downstream control units</div>
                )}
              </div>
            </div>

            {/* Transmitted CAN Signals */}
            <div>
              <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Published CAN / CAN-FD Signals ({selectedEcu.signals_produced.length})
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {selectedEcu.signals_produced.map((sig) => (
                  <div key={sig.id} className="badge badge-cyan font-mono" style={{ padding: '6px 10px', fontSize: '11px' }}>
                    {sig.name} ({sig.cycle_ms}ms)
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
