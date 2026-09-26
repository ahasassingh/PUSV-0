import React, { useEffect, useState } from 'react';
import { api, type SpecificationGapItem } from '../api/client';

export const SpecificationGapsView: React.FC = () => {
  const [gaps, setGaps] = useState<SpecificationGapItem[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>('');

  useEffect(() => {
    api.getGaps({ severity: severityFilter || undefined })
      .then(setGaps)
      .catch(console.error);
  }, [severityFilter]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-fail">SAFETY INTEGRITY GUARDRAIL</span>
              <span className="badge badge-muted">SPECIFICATION GAP ENGINE</span>
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff' }}>
              Unmasked Specification Ambiguities & Missing Thresholds
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>
              CIVIC-AI strictly refuses to hallucinate safety-critical operating boundaries, timeouts, or degraded modes. 
              Gaps are isolated for human engineering sign-off.
            </p>
          </div>

          <span className="badge badge-fail" style={{ fontSize: '13px', padding: '6px 14px' }}>
            {gaps.length} Unresolved Gaps
          </span>
        </div>
      </div>

      {/* Severity Filter Bar */}
      <div className="glass-panel" style={{ padding: '14px 20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)' }}>SEVERITY:</span>
        <button
          className="btn-secondary"
          style={{ padding: '4px 10px', fontSize: '12px', borderColor: !severityFilter ? 'var(--accent-cyan)' : 'var(--border-subtle)' }}
          onClick={() => setSeverityFilter('')}
        >
          All Severities ({gaps.length})
        </button>
        {['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
          <button
            key={sev}
            className="btn-secondary"
            style={{
              padding: '4px 10px',
              fontSize: '12px',
              borderColor: severityFilter === sev ? (sev === 'CRITICAL' ? 'var(--status-fail)' : 'var(--accent-cyan)') : 'var(--border-subtle)',
              color: severityFilter === sev ? '#ffffff' : 'var(--text-main)'
            }}
            onClick={() => setSeverityFilter(sev)}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Gaps List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {gaps.map((gap) => (
          <div 
            key={gap.id}
            className="glass-panel"
            style={{
              padding: '20px',
              borderLeft: `4px solid ${gap.severity === 'CRITICAL' ? 'var(--status-fail)' : gap.severity === 'HIGH' ? '#f97316' : '#f59e0b'}`
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="badge font-mono" style={{
                  background: gap.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                  color: gap.severity === 'CRITICAL' ? '#f87171' : '#fcd34d',
                  fontSize: '12px'
                }}>
                  {gap.severity}
                </span>
                <span className="badge badge-muted font-mono">{gap.gap_type}</span>
                <span className="badge badge-cyan font-mono">{gap.requirement_code}</span>
              </div>
              <span className="badge badge-muted font-mono" style={{ fontSize: '11px' }}>
                ECU: {gap.affected_ecu_name}
              </span>
            </div>

            <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#ffffff', marginBottom: '8px' }}>
              {gap.description}
            </h3>

            <div style={{ background: 'var(--bg-secondary)', padding: '10px 14px', borderRadius: '6px', fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>
              <span style={{ color: 'var(--text-faint)', fontSize: '11px', textTransform: 'uppercase', display: 'block', marginBottom: '2px' }}>Source Requirement Extract:</span>
              "{gap.requirement_text}"
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', borderTop: '1px solid var(--border-subtle)', paddingTop: '10px' }}>
              <div style={{ color: '#93c5fd' }}>
                <strong>Recommendation:</strong> {gap.suggested_action}
              </div>
              <div className="font-mono" style={{ color: 'var(--text-faint)' }}>
                Parameter: {gap.missing_parameter || 'Unspecified'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
