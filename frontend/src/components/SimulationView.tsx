import React, { useEffect, useState } from 'react';
import { api, type TestCaseItem } from '../api/client';
import { 
  Play, AlertTriangle, CheckCircle2, Sliders, Activity 
} from 'lucide-react';

export const SimulationView: React.FC = () => {
  const [testCases, setTestCases] = useState<TestCaseItem[]>([]);
  const [selectedTcId, setSelectedTcId] = useState<string>('tc_cmp_001');
  const [egoSpeed, setEgoSpeed] = useState<number>(40);
  const [targetDist, setTargetDist] = useState<number>(14.5);
  const [relSpeed, setRelSpeed] = useState<number>(11.1);
  const [roadFriction, setRoadFriction] = useState<number>(0.45);
  
  const [simResult, setSimResult] = useState<any | null>(null);
  const [running, setRunning] = useState<boolean>(false);

  useEffect(() => {
    api.getTestCases().then((tcs) => {
      setTestCases(tcs);
      if (tcs.length > 0) {
        const demo = tcs.find(t => t.code === 'TC-CMP-001') || tcs[0];
        setSelectedTcId(demo.id);
      }
    }).catch(console.error);
  }, []);

  const handleRun = async () => {
    setRunning(true);
    setSimResult(null);
    try {
      const res = await api.runSimulation(selectedTcId, {
        ego_speed_kph: egoSpeed,
        target_distance_m: targetDist,
        relative_speed_mps: relSpeed,
        road_friction_mu: roadFriction
      });
      setSimResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  const selectedTc = testCases.find(t => t.id === selectedTcId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-cyan">EXECUTION CONSOLE</span>
              <span className="badge badge-muted">DETERMINISTIC SIMULATION ENGINE</span>
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff' }}>
              Multi-ECU Automotive Software Simulation
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>
              Deterministic verification against physics models (TTC, friction degradation, CAN latency). 
              Strictly enforces engineering rules: tests with unapproved missing thresholds are <strong style={{ color: 'var(--status-blocked)' }}>BLOCKED</strong>.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              className="btn-secondary"
              onClick={() => {
                const cmp = testCases.find(t => t.code === 'TC-CMP-001');
                if (cmp) {
                  setSelectedTcId(cmp.id);
                  setEgoSpeed(40);
                  setTargetDist(12.0);
                  setRoadFriction(0.45);
                }
              }}
            >
              Flagship Pune Demo (TC-CMP-001)
            </button>
            <button 
              className="btn-secondary"
              onClick={() => {
                const brk = testCases.find(t => t.code === 'TC-BRK-001');
                if (brk) {
                  setSelectedTcId(brk.id);
                  setEgoSpeed(80);
                  setTargetDist(40.0);
                  setRoadFriction(0.85);
                }
              }}
            >
              Baseline Pass Demo (TC-BRK-001)
            </button>
          </div>
        </div>
      </div>

      {/* Main Layout: Controls & Telemetry */}
      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '20px' }}>
        {/* Left Column: Test & Parameter Controls */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={16} color="var(--accent-cyan)" /> Simulation Parameters
          </h3>

          {/* Test Case Dropdown */}
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '6px', display: 'block' }}>
              Select Test Case
            </label>
            <select
              value={selectedTcId}
              onChange={(e) => setSelectedTcId(e.target.value)}
              style={{
                width: '100%',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-strong)',
                color: '#ffffff',
                padding: '8px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                fontFamily: 'var(--font-mono)'
              }}
            >
              {testCases.map((tc) => (
                <option key={tc.id} value={tc.id}>
                  {tc.code} - {tc.title.slice(0, 38)}...
                </option>
              ))}
            </select>
          </div>

          {/* Selected Test Summary */}
          {selectedTc && (
            <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '6px', fontSize: '12px' }}>
              <div style={{ fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '4px' }}>
                {selectedTc.title}
              </div>
              <div style={{ color: 'var(--text-muted)', lineHeight: 1.4, marginBottom: '8px' }}>
                {selectedTc.scenario}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {selectedTc.ecu_under_test.map((e) => (
                  <span key={e} className="badge badge-muted font-mono" style={{ fontSize: '10px' }}>{e}</span>
                ))}
              </div>
            </div>
          )}

          {/* Sliders */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Ego Vehicle Speed:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>{egoSpeed} km/h</span>
              </div>
              <input 
                type="range" min="10" max="120" step="5" 
                value={egoSpeed} 
                onChange={(e) => setEgoSpeed(Number(e.target.value))} 
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Target Distance:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>{targetDist} m</span>
              </div>
              <input 
                type="range" min="3" max="80" step="0.5" 
                value={targetDist} 
                onChange={(e) => setTargetDist(Number(e.target.value))} 
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Relative Closing Speed:</span>
                <span className="font-mono" style={{ fontWeight: 600 }}>{relSpeed} m/s</span>
              </div>
              <input 
                type="range" min="2" max="30" step="0.5" 
                value={relSpeed} 
                onChange={(e) => setRelSpeed(Number(e.target.value))} 
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Road Friction (&mu;):</span>
                <span className="font-mono" style={{ fontWeight: 600, color: roadFriction < 0.5 ? 'var(--status-fail)' : 'var(--status-pass)' }}>
                  {roadFriction} ({roadFriction < 0.5 ? 'Wet / Monsoon' : 'Dry Asphalt'})
                </span>
              </div>
              <input 
                type="range" min="0.25" max="0.90" step="0.05" 
                value={roadFriction} 
                onChange={(e) => setRoadFriction(Number(e.target.value))} 
                style={{ width: '100%' }}
              />
            </div>
          </div>

          <button 
            className="btn-primary" 
            disabled={running}
            onClick={handleRun}
            style={{ width: '100%', justifyContent: 'center', marginTop: '6px' }}
          >
            <Play size={16} /> {running ? 'Simulating Physics...' : 'Execute Test Run'}
          </button>
        </div>

        {/* Right Column: Execution Outcome & Telemetry Timeline */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={16} color="var(--accent-cyan)" /> Real-Time Execution Telemetry
          </h3>

          {!simResult && (
            <div style={{ padding: '60px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
              Click <strong>Execute Test Run</strong> to evaluate multi-ECU response against deterministic physics models.
            </div>
          )}

          {simResult && (
            <>
              {/* Result Status Banner */}
              <div style={{
                padding: '16px',
                borderRadius: '6px',
                border: `1px solid ${simResult.status === 'PASS' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`,
                background: simResult.status === 'PASS' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <div style={{
                    fontWeight: 700,
                    fontSize: '14px',
                    color: simResult.status === 'PASS' ? 'var(--status-pass)' : 'var(--status-blocked)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    {simResult.status === 'PASS' ? (
                      <>
                        <CheckCircle2 size={18} /> TEST EXECUTION STATUS: PASS
                      </>
                    ) : (
                      <>
                        <AlertTriangle size={18} /> TEST EXECUTION STATUS: BLOCKED
                      </>
                    )}
                  </div>
                  {simResult.blocked_reason && (
                    <div style={{ fontSize: '13px', color: '#fef08a', marginTop: '4px', fontWeight: 500 }}>
                      Blocker: {simResult.blocked_reason}
                    </div>
                  )}
                </div>

                <span className="badge badge-muted font-mono" style={{ fontSize: '12px' }}>
                  {simResult.status === 'PASS' ? 'DETERMINISTIC VERIFIED' : 'SAFETY REFUSAL'}
                </span>
              </div>

              {/* Execution Metrics (if pass) */}
              {simResult.status === 'PASS' && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Initial Speed</div>
                    <div className="font-mono" style={{ fontSize: '16px', fontWeight: 700 }}>{simResult.metrics.initial_speed_kph} km/h</div>
                  </div>
                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Computed TTC</div>
                    <div className="font-mono" style={{ fontSize: '16px', fontWeight: 700, color: 'var(--accent-cyan)' }}>{simResult.metrics.time_to_collision_sec} s</div>
                  </div>
                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Stopping Dist</div>
                    <div className="font-mono" style={{ fontSize: '16px', fontWeight: 700, color: 'var(--status-pass)' }}>{simResult.metrics.stopping_distance_m} m</div>
                  </div>
                  <div style={{ background: 'var(--bg-secondary)', padding: '12px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Residual Margin</div>
                    <div className="font-mono" style={{ fontSize: '16px', fontWeight: 700 }}>+{simResult.metrics.residual_distance_m} m</div>
                  </div>
                </div>
              )}

              {/* Telemetry Timeline Table */}
              {simResult.telemetry_points && simResult.telemetry_points.length > 0 && (
                <div>
                  <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '8px' }}>
                    Timeline Data Log
                  </h4>
                  <div style={{ overflowX: 'auto', maxHeight: '250px' }}>
                    <table className="eng-table font-mono" style={{ fontSize: '12px' }}>
                      <thead>
                        <tr>
                          <th>Time (ms)</th>
                          <th>Ego Speed (km/h)</th>
                          <th>Brake Pressure (bar)</th>
                          <th>Time-To-Collision (s)</th>
                          <th>State Machine</th>
                        </tr>
                      </thead>
                      <tbody>
                        {simResult.telemetry_points.map((pt: any, idx: number) => (
                          <tr key={idx}>
                            <td style={{ color: 'var(--accent-cyan)' }}>+{pt.time_ms} ms</td>
                            <td>{pt.ego_speed}</td>
                            <td style={{ color: pt.brake_pressure > 0 ? '#60a5fa' : 'var(--text-muted)' }}>{pt.brake_pressure}</td>
                            <td>{pt.ttc}s</td>
                            <td>
                              <span className={`badge ${pt.state === 'STANDSTILL' ? 'badge-pass' : pt.state === 'BRAKING' ? 'badge-cyan' : 'badge-muted'}`}>
                                {pt.state}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Log Trace */}
              <div>
                <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '8px' }}>
                  Execution Diagnostic Trace
                </h4>
                <div style={{ background: 'var(--bg-primary)', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-subtle)', fontFamily: 'var(--font-mono)', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {simResult.log_trace.map((line: string, idx: number) => (
                    <div key={idx} style={{ color: line.includes('BLOCKED') ? 'var(--status-blocked)' : line.includes('PASS') ? 'var(--status-pass)' : 'var(--text-muted)' }}>
                      &gt; {line}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
