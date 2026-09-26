import React, { useEffect, useState } from 'react';
import { api, type RequirementItem } from '../api/client';
import { 
  FileText, Search, AlertTriangle, CheckCircle2, 
  HelpCircle, ChevronRight, X 
} from 'lucide-react';

export const RequirementsView: React.FC = () => {
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [selectedReq, setSelectedReq] = useState<any | null>(null);
  const [systemFilter, setSystemFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [search, setSearch] = useState<string>('');

  const loadRequirements = () => {
    api.getRequirements({
      system: systemFilter || undefined,
      status: statusFilter || undefined,
      search: search || undefined
    })
      .then(setRequirements)
      .catch(console.error);
  };

  useEffect(() => {
    loadRequirements();
  }, [systemFilter, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadRequirements();
  };

  const handleSelectReq = (reqId: string) => {
    api.getRequirementDetail(reqId)
      .then(setSelectedReq)
      .catch(console.error);
  };

  const systems = ['Braking', 'ADAS', 'TPMS', 'Suspension', 'Communication', 'Diagnostics'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Filter Bar */}
      <div className="glass-panel" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)' }}>SYSTEM:</span>
          <button 
            className={`btn-secondary ${!systemFilter ? 'active' : ''}`}
            style={{ padding: '4px 10px', fontSize: '12px', borderColor: !systemFilter ? 'var(--accent-cyan)' : 'var(--border-subtle)' }}
            onClick={() => setSystemFilter('')}
          >
            All
          </button>
          {systems.map((s) => (
            <button
              key={s}
              className="btn-secondary"
              style={{ 
                padding: '4px 10px', 
                fontSize: '12px',
                borderColor: systemFilter === s ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                color: systemFilter === s ? 'var(--accent-cyan)' : 'var(--text-main)'
              }}
              onClick={() => setSystemFilter(s)}
            >
              {s}
            </button>
          ))}
          
          <div style={{ marginLeft: '12px', display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>STATUS:</span>
            {['COMPLETE', 'INCOMPLETE', 'AMBIGUOUS'].map((st) => (
              <button
                key={st}
                className="btn-secondary"
                style={{
                  padding: '3px 8px',
                  fontSize: '11px',
                  borderColor: statusFilter === st ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                  color: statusFilter === st ? 'var(--accent-cyan)' : 'var(--text-faint)'
                }}
                onClick={() => setStatusFilter(statusFilter === st ? '' : st)}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search ID, text, ECU..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-strong)',
                color: '#ffffff',
                padding: '7px 12px 7px 32px',
                borderRadius: '6px',
                fontSize: '13px',
                width: '240px'
              }}
            />
            <Search size={15} style={{ position: 'absolute', left: '10px', top: '9px', color: 'var(--text-faint)' }} />
          </div>
          <button type="submit" className="btn-primary" style={{ padding: '6px 12px', fontSize: '12px' }}>
            Filter
          </button>
        </form>
      </div>

      {/* Requirements Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText size={18} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '16px', fontWeight: 600 }}>Vehicle Software Specifications ({requirements.length})</h2>
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Showing verified functional and safety requirements
          </span>
        </div>

        <div style={{ overflowX: 'auto', maxHeight: '650px' }}>
          <table className="eng-table">
            <thead>
              <tr>
                <th style={{ width: '130px' }}>Req Code</th>
                <th>System / Subsystem</th>
                <th style={{ width: '150px' }}>Logical ECU</th>
                <th style={{ width: '90px' }}>Safety</th>
                <th>Requirement Specification</th>
                <th style={{ width: '130px' }}>Completeness</th>
                <th style={{ width: '90px' }}>Gaps</th>
                <th style={{ width: '80px' }}>Tests</th>
                <th style={{ width: '50px' }}></th>
              </tr>
            </thead>
            <tbody>
              {requirements.map((req) => (
                <tr 
                  key={req.id} 
                  onClick={() => handleSelectReq(req.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td className="font-mono" style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>
                    {req.req_code}
                  </td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{req.system}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>{req.subsystem}</div>
                  </td>
                  <td>
                    <span className="badge badge-muted font-mono" style={{ fontSize: '11px' }}>
                      {req.ecu_name}
                    </span>
                  </td>
                  <td>
                    <span className="badge" style={{ 
                      background: req.safety_relevance.includes('ASIL-D') ? 'rgba(239, 68, 68, 0.15)' : 'rgba(59, 130, 246, 0.15)',
                      color: req.safety_relevance.includes('ASIL-D') ? '#f87171' : '#60a5fa',
                      border: '1px solid rgba(255,255,255,0.1)'
                    }}>
                      {req.safety_relevance}
                    </span>
                  </td>
                  <td style={{ maxWidth: '420px', lineHeight: 1.4 }}>
                    <div style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {req.original_text}
                    </div>
                  </td>
                  <td>
                    {req.completeness_status === 'COMPLETE' && (
                      <span className="badge badge-pass"><CheckCircle2 size={11} /> COMPLETE</span>
                    )}
                    {req.completeness_status === 'INCOMPLETE' && (
                      <span className="badge badge-fail"><AlertTriangle size={11} /> INCOMPLETE</span>
                    )}
                    {req.completeness_status === 'AMBIGUOUS' && (
                      <span className="badge badge-blocked"><HelpCircle size={11} /> AMBIGUOUS</span>
                    )}
                  </td>
                  <td>
                    {req.gaps.length > 0 ? (
                      <span className="badge badge-fail" style={{ fontSize: '11px' }}>
                        {req.gaps.length} GAP{req.gaps.length > 1 ? 'S' : ''}
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)', fontSize: '12px' }}>—</span>
                    )}
                  </td>
                  <td className="font-mono" style={{ color: req.test_count > 0 ? 'var(--status-pass)' : 'var(--text-faint)' }}>
                    {req.test_count} TC
                  </td>
                  <td>
                    <ChevronRight size={16} color="var(--text-faint)" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Requirement Detail Modal */}
      {selectedReq && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(5, 8, 15, 0.85)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 9999,
          padding: '20px'
        }}>
          <div className="glass-panel" style={{
            width: '100%',
            maxWidth: '850px',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            border: '1px solid var(--border-strong)',
            boxShadow: '0 20px 40px rgba(0,0,0,0.6)'
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '18px 24px',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'var(--bg-secondary)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span className="badge badge-cyan font-mono" style={{ fontSize: '13px' }}>
                  {selectedReq.req_code}
                </span>
                <span className="badge badge-muted">{selectedReq.system} / {selectedReq.subsystem}</span>
                <span className="badge badge-muted">ASIL: {selectedReq.safety_relevance}</span>
              </div>
              <button 
                onClick={() => setSelectedReq(null)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '8px' }}>
                  Source Automotive Requirement Text
                </h4>
                <div style={{
                  padding: '14px',
                  background: 'var(--bg-primary)',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '14px',
                  lineHeight: 1.6,
                  color: '#ffffff'
                }}>
                  {selectedReq.original_text}
                </div>
              </div>

              {/* Specification Gaps Alert (if any) */}
              {selectedReq.gaps && selectedReq.gaps.length > 0 && (
                <div style={{
                  padding: '16px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.35)',
                  borderRadius: '6px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--status-fail)', fontWeight: 600, fontSize: '13px', marginBottom: '10px' }}>
                    <AlertTriangle size={16} /> SPECIFICATION GAP DETECTED ({selectedReq.gaps.length})
                  </div>
                  {selectedReq.gaps.map((gap: any) => (
                    <div key={gap.id} style={{ fontSize: '13px', marginBottom: '8px' }}>
                      <div style={{ fontWeight: 600, color: '#fca5a5' }}>
                        [{gap.severity}] {gap.gap_type}: {gap.description}
                      </div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '2px' }}>
                        Action: {gap.suggested_action}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Normalized Data Matrix */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '4px' }}>Logical ECU</div>
                  <div className="font-mono" style={{ fontSize: '14px', fontWeight: 600, color: 'var(--accent-cyan)' }}>
                    {selectedReq.ecu_name}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '4px' }}>Quantitative Threshold</div>
                  <div className="font-mono" style={{ fontSize: '13px', color: selectedReq.threshold ? 'var(--status-pass)' : 'var(--status-fail)' }}>
                    {selectedReq.threshold || 'UNDEFINED (GAP)'}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '4px' }}>Timing / Latency Bound</div>
                  <div className="font-mono" style={{ fontSize: '13px', color: selectedReq.timing_constraint ? 'var(--status-pass)' : 'var(--status-fail)' }}>
                    {selectedReq.timing_constraint || 'UNDEFINED (GAP)'}
                  </div>
                </div>
              </div>

              {/* Input Signals & Dependencies */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '8px' }}>Input Signals & Sensors</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {selectedReq.inputs.map((inp: string) => (
                      <span key={inp} className="badge badge-muted font-mono" style={{ fontSize: '11px' }}>{inp}</span>
                    ))}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '8px' }}>Output Demands & Actuators</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {selectedReq.outputs.map((out: string) => (
                      <span key={out} className="badge badge-cyan font-mono" style={{ fontSize: '11px' }}>{out}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Linked Test Cases */}
              <div>
                <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '10px' }}>
                  Generated Automotive Test Cases ({selectedReq.test_cases?.length || 0})
                </h4>
                {selectedReq.test_cases && selectedReq.test_cases.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {selectedReq.test_cases.map((tc: any) => (
                      <div key={tc.id} style={{
                        padding: '10px 14px',
                        background: 'var(--bg-secondary)',
                        borderRadius: '6px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span className="badge badge-cyan font-mono">{tc.code}</span>
                          <span style={{ fontSize: '13px', fontWeight: 500 }}>{tc.title}</span>
                          <span className="badge badge-muted">{tc.category}</span>
                        </div>
                        <span className={`badge ${tc.status === 'VALIDATED' ? 'badge-pass' : tc.status === 'BLOCKED' ? 'badge-blocked' : 'badge-muted'}`}>
                          {tc.status}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ color: 'var(--text-faint)', fontSize: '13px' }}>
                    No test cases generated yet for this requirement.
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div style={{
              padding: '14px 24px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              justifyContent: 'flex-end',
              background: 'var(--bg-secondary)'
            }}>
              <button className="btn-secondary" onClick={() => setSelectedReq(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
