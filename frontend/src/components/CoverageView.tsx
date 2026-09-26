import React, { useEffect, useState } from 'react';
import { api, type CoverageData } from '../api/client';
import { Layers, Cpu } from 'lucide-react';

export const CoverageView: React.FC = () => {
  const [coverage, setCoverage] = useState<CoverageData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.getCoverage()
      .then(setCoverage)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !coverage) {
    return <div style={{ color: 'var(--accent-cyan)', padding: '40px', textAlign: 'center' }}>Calculating Verification Matrices...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-cyan">TRACEABILITY & AUDIT</span>
              <span className="badge badge-muted">MULTI-DIMENSIONAL VERIFICATION</span>
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff' }}>
              Automotive Test Suite Coverage Matrix
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>
              Computed directly from live application requirements, test cases, ECU bindings, and Pune operational scenarios.
            </p>
          </div>
          <span className="badge badge-pass" style={{ fontSize: '12px', padding: '6px 12px' }}>
            {coverage.summary.total_test_cases} Active Test Specifications
          </span>
        </div>
      </div>

      {/* Top 5 Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>REQUIREMENTS COVERAGE</div>
          <div className="font-mono" style={{ fontSize: '26px', fontWeight: 700, color: 'var(--accent-cyan)' }}>
            {coverage.summary.requirement_coverage_pct}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            {coverage.summary.total_requirements} total requirements
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>ECU ARCHITECTURE COVERAGE</div>
          <div className="font-mono" style={{ fontSize: '26px', fontWeight: 700, color: 'var(--status-pass)' }}>
            {coverage.summary.ecu_coverage_pct}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            8 of 8 logical ECUs tested
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>PUNE SCENARIO COVERAGE</div>
          <div className="font-mono" style={{ fontSize: '26px', fontWeight: 700, color: '#60a5fa' }}>
            {coverage.summary.scenario_coverage_pct}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            6 operational categories
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>FAULT INJECTION COVERAGE</div>
          <div className="font-mono" style={{ fontSize: '26px', fontWeight: 700, color: '#c084fc' }}>
            {coverage.summary.fault_coverage_pct}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            Sensor/bus disconnect tests
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>BOUNDARY & STRESS</div>
          <div className="font-mono" style={{ fontSize: '26px', fontWeight: 700, color: '#fbbf24' }}>
            {coverage.summary.boundary_coverage_pct}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            Edge case stress limits
          </div>
        </div>
      </div>

      {/* Grid: System Breakdown + ECU Participation */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Subsystem Coverage Breakdown */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={16} color="var(--accent-cyan)" /> Coverage by Automotive Subsystem
          </h3>

          <div style={{ overflowX: 'auto' }}>
            <table className="eng-table">
              <thead>
                <tr>
                  <th>Subsystem</th>
                  <th>Total Req</th>
                  <th>Tested Req</th>
                  <th>Coverage</th>
                </tr>
              </thead>
              <tbody>
                {coverage.by_system.map((sys) => (
                  <tr key={sys.system}>
                    <td style={{ fontWeight: 600 }}>{sys.system}</td>
                    <td className="font-mono">{sys.total_requirements}</td>
                    <td className="font-mono" style={{ color: 'var(--status-pass)' }}>{sys.covered_requirements}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '80px', height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${sys.coverage_pct}%`, height: '100%', background: sys.coverage_pct >= 80 ? 'var(--status-pass)' : 'var(--accent-cyan)' }} />
                        </div>
                        <span className="font-mono" style={{ fontSize: '12px' }}>{sys.coverage_pct}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ECU Test Participation Matrix */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={16} color="var(--accent-cyan)" /> Logical ECU Verification Participation
          </h3>

          <div style={{ overflowX: 'auto' }}>
            <table className="eng-table">
              <thead>
                <tr>
                  <th>ECU Name</th>
                  <th>Domain</th>
                  <th>Tests Linked</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {coverage.by_ecu.map((ecu) => (
                  <tr key={ecu.ecu_id}>
                    <td className="font-mono" style={{ fontWeight: 600, color: '#ffffff' }}>{ecu.ecu_name}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{ecu.domain}</td>
                    <td className="font-mono" style={{ color: 'var(--accent-cyan)' }}>{ecu.test_count} tests</td>
                    <td>
                      <span className="badge badge-pass">{ecu.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
