import React, { useEffect, useState } from 'react';
import { api, type DashboardStats } from '../api/client';
import { 
  AlertTriangle, Cpu, FileText, CheckCircle2, 
  XCircle, Zap, Activity, ArrowRight, Gauge, Layers 
} from 'lucide-react';

interface Props {
  onNavigate: (tab: string) => void;
}

export const DashboardView: React.FC<Props> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboardStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <div style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>LOADING PUSV-01 TELEMETRY...</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Platform Header Card */}
      <div className="glass-panel" style={{ padding: '24px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: 0, right: 0, width: '300px', height: '100%', background: 'radial-gradient(circle at top right, rgba(6,182,212,0.12), transparent 70%)', pointerEvents: 'none' }} />
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <span className="badge badge-cyan">REFERENCE VEHICLE: {stats.vehicle_name}</span>
              <span className="badge badge-muted">VERSION: {stats.sw_version}</span>
              <span className="badge badge-muted">CLASS: {stats.vehicle_class}</span>
              <span className="badge" style={{ background: 'rgba(59,130,246,0.15)', color: '#60a5fa', border: '1px solid rgba(59,130,246,0.3)' }}>
                NON-PROPRIETARY REFERENCE ARCHITECTURE
              </span>
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: 700, letterSpacing: '-0.02em', color: '#ffffff', marginBottom: '8px' }}>
              CIVIC-AI Validation Console
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '14px', maxWidth: '750px', lineHeight: 1.5 }}>
              Automated multi-ECU automotive software verification platform. Maps vehicle requirements through 
              topological ECU dependency graphs, injects high-density Indian & Pune operational edge cases, 
              and executes deterministic compliance simulations.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn-secondary" onClick={() => onNavigate('scenarios')}>
              <Layers size={15} /> Pune Scenario Catalog
            </button>
            <button className="btn-primary" onClick={() => onNavigate('tests')}>
              <Zap size={15} /> View Test Suite ({stats.test_cases_count})
            </button>
          </div>
        </div>
      </div>

      {/* KPI Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px' }}>
            <span>REQUIREMENTS</span>
            <FileText size={16} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#ffffff' }}>
            {stats.requirements_count}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            Braking, ADAS, TPMS, Road, Bus, Diag
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px' }}>
            <span>GENERATED TESTS</span>
            <Activity size={16} color="#60a5fa" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#ffffff' }}>
            {stats.test_cases_count}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            Multi-ECU & Compound Scenarios
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px' }}>
            <span>VALIDATED (PASS)</span>
            <CheckCircle2 size={16} color="var(--status-pass)" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--status-pass)' }}>
            {stats.validated_tests_count}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            Verified deterministic compliance
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px' }}>
            <span>EXECUTION BLOCKED</span>
            <AlertTriangle size={16} color="var(--status-blocked)" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--status-blocked)' }}>
            {stats.blocked_tests_count}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            Refused: Missing safety thresholds
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px' }}>
            <span>SPECIFICATION GAPS</span>
            <XCircle size={16} color="var(--status-fail)" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--status-fail)' }}>
            {stats.specification_gaps_count}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            Missing timeout / bounds flagged
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '8px' }}>
            <span>LOGICAL ECUs</span>
            <Cpu size={16} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#ffffff' }}>
            {stats.ecus_count}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
            PUSV-01 Topology Active
          </div>
        </div>
      </div>

      {/* Coverage & Verification Matrices */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        {/* Multidimensional Coverage */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Gauge size={16} color="var(--accent-cyan)" /> Computed Verification Coverage
            </h3>
            <span className="badge badge-cyan">REAL APPLICATION DATA</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Requirement Traceability Coverage</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{stats.coverage.requirement_coverage_pct}%</span>
              </div>
              <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${stats.coverage.requirement_coverage_pct}%`, height: '100%', background: 'var(--accent-cyan)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>ECU Architecture Coverage (8 of 8)</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--status-pass)' }}>{stats.coverage.ecu_coverage_pct}%</span>
              </div>
              <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${stats.coverage.ecu_coverage_pct}%`, height: '100%', background: 'var(--status-pass)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Pune ODD Scenario Coverage</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{stats.coverage.scenario_coverage_pct}%</span>
              </div>
              <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${stats.coverage.scenario_coverage_pct}%`, height: '100%', background: '#38bdf8' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Fault Injection Coverage</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{stats.coverage.fault_coverage_pct}%</span>
              </div>
              <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${stats.coverage.fault_coverage_pct}%`, height: '100%', background: '#a855f7' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Boundary & Negative Stress Coverage</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{stats.coverage.boundary_coverage_pct}%</span>
              </div>
              <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${stats.coverage.boundary_coverage_pct}%`, height: '100%', background: '#f59e0b' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Primary Demo Highlight Banner */}
        <div className="glass-panel" style={{ padding: '20px', borderLeft: '4px solid var(--accent-cyan)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span className="badge badge-cyan">FLAGSHIP BENCHMARK SCENARIO</span>
            <span className="badge badge-blocked">COMPOUND MULTI-ECU TEST</span>
          </div>

          <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
            Pune Monsoon Emergency Stop: Motorcycle Cut-in + Pothole Shock + Low Tyre Pressure
          </h3>

          <p style={{ color: 'var(--text-muted)', fontSize: '13px', lineHeight: 1.5, marginBottom: '16px' }}>
            Stress tests simultaneous interaction across 6 ECUs: ADAS optical spray blur handling, 
            wheel-slip ABS threshold adaptation on wet asphalt (mu=0.45), pothole shock suppression, 
            and Front-Right under-inflation stability balancing.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
            <span className="badge badge-muted">ADAS_ECU</span>
            <span className="badge badge-muted">BRAKE_ECU</span>
            <span className="badge badge-muted">VEHICLE_DYNAMICS_ECU</span>
            <span className="badge badge-muted">TPMS_ECU</span>
            <span className="badge badge-muted">GATEWAY_ECU</span>
          </div>

          <button className="btn-primary" onClick={() => onNavigate('simulation')} style={{ width: '100%', justifyContent: 'center' }}>
            Launch Deterministic Simulation Console <ArrowRight size={15} />
          </button>
        </div>
      </div>

      {/* Recent Generation Jobs */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={16} color="var(--accent-cyan)" /> Recent Verification & Generation Jobs
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table className="eng-table">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Target Requirement</th>
                <th>Pune Scenario</th>
                <th>Tests Synthesized</th>
                <th>Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_jobs.map((job) => (
                <tr key={job.id}>
                  <td className="font-mono" style={{ color: 'var(--accent-cyan)' }}>{job.id}</td>
                  <td className="font-mono" style={{ fontWeight: 600 }}>{job.requirement_code}</td>
                  <td>{job.scenario_name}</td>
                  <td className="font-mono">{job.tests_generated} test cases</td>
                  <td>
                    <span className="badge badge-pass">{job.status}</span>
                  </td>
                  <td style={{ color: 'var(--text-faint)', fontSize: '12px' }}>
                    {new Date(job.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
