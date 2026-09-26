import React, { useEffect, useState } from 'react';
import { api, type TestCaseItem } from '../api/client';
import { 
  CheckCircle2, AlertTriangle, FileCheck, ArrowRight, X, Play 
} from 'lucide-react';

export const TestCasesView: React.FC = () => {
  const [testCases, setTestCases] = useState<TestCaseItem[]>([]);
  const [selectedTestCase, setSelectedTestCase] = useState<any | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [simulating, setSimulating] = useState<boolean>(false);

  const loadTestCases = () => {
    api.getTestCases({
      category: categoryFilter || undefined,
      status: statusFilter || undefined
    })
      .then(setTestCases)
      .catch(console.error);
  };

  useEffect(() => {
    loadTestCases();
  }, [categoryFilter, statusFilter]);

  const handleSelectTest = (id: string) => {
    api.getTestCaseDetail(id)
      .then(setSelectedTestCase)
      .catch(console.error);
  };

  const handleRunSimulation = async (tcId: string) => {
    setSimulating(true);
    try {
      await api.runSimulation(tcId);
      // Reload detail
      const updated = await api.getTestCaseDetail(tcId);
      setSelectedTestCase(updated);
      loadTestCases();
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  const categories = ['Functional', 'Boundary', 'Fault injection', 'Compound scenario', 'Inter-ECU integration', 'Environmental'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Filter Bar */}
      <div className="glass-panel" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)' }}>CATEGORY:</span>
          <button 
            className="btn-secondary"
            style={{ padding: '4px 10px', fontSize: '12px', borderColor: !categoryFilter ? 'var(--accent-cyan)' : 'var(--border-subtle)' }}
            onClick={() => setCategoryFilter('')}
          >
            All ({testCases.length})
          </button>
          {categories.map((c) => (
            <button
              key={c}
              className="btn-secondary"
              style={{
                padding: '4px 10px',
                fontSize: '12px',
                borderColor: categoryFilter === c ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                color: categoryFilter === c ? 'var(--accent-cyan)' : 'var(--text-main)'
              }}
              onClick={() => setCategoryFilter(c)}
            >
              {c}
            </button>
          ))}
        </div>

        {/* Status Filter */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className="btn-secondary"
            style={{ padding: '4px 10px', fontSize: '12px', borderColor: statusFilter === 'VALIDATED' ? 'var(--status-pass)' : 'var(--border-subtle)' }}
            onClick={() => setStatusFilter(statusFilter === 'VALIDATED' ? '' : 'VALIDATED')}
          >
            Pass Only
          </button>
          <button
            className="btn-secondary"
            style={{ padding: '4px 10px', fontSize: '12px', borderColor: statusFilter === 'BLOCKED' ? 'var(--status-blocked)' : 'var(--border-subtle)' }}
            onClick={() => setStatusFilter(statusFilter === 'BLOCKED' ? '' : 'BLOCKED')}
          >
            Blocked Only
          </button>
        </div>
      </div>

      {/* Test Cases Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileCheck size={18} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '16px', fontWeight: 600 }}>Automotive Test Case Specifications ({testCases.length})</h2>
          </div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Traceable to source software requirements and participating ECUs
          </span>
        </div>

        <div style={{ overflowX: 'auto', maxHeight: '650px' }}>
          <table className="eng-table">
            <thead>
              <tr>
                <th style={{ width: '130px' }}>Test Code</th>
                <th>Title / Scenario Description</th>
                <th style={{ width: '140px' }}>Category</th>
                <th style={{ width: '70px' }}>Priority</th>
                <th>Participating ECUs</th>
                <th style={{ width: '120px' }}>Requirements</th>
                <th style={{ width: '110px' }}>Sim Status</th>
                <th style={{ width: '110px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {testCases.map((tc) => {
                const resStatus = tc.latest_result?.status || tc.status;
                const isBlocked = resStatus === 'BLOCKED';
                return (
                  <tr 
                    key={tc.id} 
                    onClick={() => handleSelectTest(tc.id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td className="font-mono" style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>
                      {tc.code}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: '#ffffff', marginBottom: '2px' }}>{tc.title}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {tc.scenario}
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-muted" style={{ fontSize: '11px' }}>
                        {tc.category}
                      </span>
                    </td>
                    <td>
                      <span className="badge font-mono" style={{
                        background: tc.priority === 'P0' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(59, 130, 246, 0.15)',
                        color: tc.priority === 'P0' ? '#f87171' : '#60a5fa'
                      }}>
                        {tc.priority}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {tc.ecu_under_test.slice(0, 3).map((e) => (
                          <span key={e} className="badge badge-muted font-mono" style={{ fontSize: '10px' }}>{e}</span>
                        ))}
                        {tc.ecu_under_test.length > 3 && (
                          <span className="badge badge-muted font-mono" style={{ fontSize: '10px' }}>
                            +{tc.ecu_under_test.length - 3}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      {tc.requirement_ids.slice(0, 2).join(', ')}
                      {tc.requirement_ids.length > 2 && ` +${tc.requirement_ids.length - 2}`}
                    </td>
                    <td>
                      {resStatus === 'PASS' && (
                        <span className="badge badge-pass"><CheckCircle2 size={11} /> PASS</span>
                      )}
                      {isBlocked && (
                        <span className="badge badge-blocked" title={tc.latest_result?.blocked_reason}><AlertTriangle size={11} /> BLOCKED</span>
                      )}
                      {!isBlocked && resStatus !== 'PASS' && (
                        <span className="badge badge-muted">{resStatus}</span>
                      )}
                    </td>
                    <td>
                      <button 
                        className="btn-secondary" 
                        style={{ padding: '4px 10px', fontSize: '11px' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectTest(tc.id);
                        }}
                      >
                        Inspect <ArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Engineering Test Specification Modal */}
      {selectedTestCase && (
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
            maxWidth: '920px',
            maxHeight: '92vh',
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
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                  <span className="badge badge-cyan font-mono" style={{ fontSize: '13px' }}>
                    {selectedTestCase.code}
                  </span>
                  <span className="badge badge-muted">{selectedTestCase.category}</span>
                  <span className="badge font-mono" style={{
                    background: selectedTestCase.priority === 'P0' ? 'rgba(239,68,68,0.15)' : 'rgba(59,130,246,0.15)',
                    color: selectedTestCase.priority === 'P0' ? '#f87171' : '#60a5fa'
                  }}>
                    {selectedTestCase.priority}
                  </span>
                  {selectedTestCase.latest_result?.status === 'PASS' && (
                    <span className="badge badge-pass"><CheckCircle2 size={11} /> SIM: PASS</span>
                  )}
                  {selectedTestCase.latest_result?.status === 'BLOCKED' && (
                    <span className="badge badge-blocked"><AlertTriangle size={11} /> SIM: BLOCKED</span>
                  )}
                </div>
                <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#ffffff' }}>
                  {selectedTestCase.title}
                </h3>
              </div>
              <button 
                onClick={() => setSelectedTestCase(null)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              {/* Simulation Result Banner if executed */}
              {selectedTestCase.latest_result && (
                <div style={{
                  padding: '14px 18px',
                  borderRadius: '6px',
                  border: `1px solid ${selectedTestCase.latest_result.status === 'PASS' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`,
                  background: selectedTestCase.latest_result.status === 'PASS' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <div style={{
                      fontWeight: 700,
                      fontSize: '13px',
                      color: selectedTestCase.latest_result.status === 'PASS' ? 'var(--status-pass)' : 'var(--status-blocked)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      {selectedTestCase.latest_result.status === 'PASS' ? (
                        <>
                          <CheckCircle2 size={16} /> DETERMINISTIC SIMULATION PASSED
                        </>
                      ) : (
                        <>
                          <AlertTriangle size={16} /> DETERMINISTIC SIMULATION BLOCKED
                        </>
                      )}
                    </div>
                    {selectedTestCase.latest_result.blocked_reason && (
                      <div style={{ fontSize: '13px', color: '#fde68a', marginTop: '4px' }}>
                        Reason: {selectedTestCase.latest_result.blocked_reason}
                      </div>
                    )}
                  </div>
                  <span className="badge badge-muted font-mono" style={{ fontSize: '11px' }}>
                    DURATION: {selectedTestCase.latest_result.simulation_duration_ms} ms
                  </span>
                </div>
              )}

              {/* Traceability: Participating ECUs & Requirements */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '8px' }}>
                    ECUs Under Test (Multi-ECU Coordination)
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {selectedTestCase.ecu_under_test.map((e: string) => (
                      <span key={e} className="badge badge-cyan font-mono" style={{ fontSize: '11px' }}>{e}</span>
                    ))}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '8px' }}>
                    Source Requirement Traceability
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {selectedTestCase.requirement_ids.map((r: string) => (
                      <span key={r} className="badge badge-muted font-mono" style={{ fontSize: '11px' }}>{r}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Scenario Context */}
              <div>
                <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '6px' }}>
                  Operational Scenario Context
                </h4>
                <div style={{ padding: '12px 14px', background: 'var(--bg-primary)', borderRadius: '6px', border: '1px solid var(--border-subtle)', fontSize: '13px', lineHeight: 1.5 }}>
                  {selectedTestCase.scenario}
                </div>
              </div>

              {/* Preconditions */}
              <div>
                <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '6px' }}>
                  Preconditions
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {selectedTestCase.preconditions.map((p: string, idx: number) => (
                    <div key={idx} style={{ fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-main)' }}>
                      <span className="font-mono" style={{ color: 'var(--accent-cyan)', fontSize: '11px' }}>0{idx + 1}.</span> {p}
                    </div>
                  ))}
                </div>
              </div>

              {/* Input Signals */}
              {selectedTestCase.input_signals && selectedTestCase.input_signals.length > 0 && (
                <div>
                  <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '6px' }}>
                    Test Input Signals
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {selectedTestCase.input_signals.map((sig: any, idx: number) => (
                      <div key={idx} className="badge badge-muted font-mono" style={{ padding: '6px 10px', fontSize: '11px' }}>
                        {sig.signal} = <span style={{ color: 'var(--accent-cyan)' }}>{sig.value} {sig.unit}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Execution Steps */}
              <div>
                <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '8px' }}>
                  Test Execution Procedure
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {selectedTestCase.steps.map((step: string, idx: number) => (
                    <div key={idx} style={{ padding: '8px 12px', background: 'var(--bg-secondary)', borderRadius: '4px', fontSize: '13px', display: 'flex', gap: '10px' }}>
                      <span className="font-mono" style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Step {idx + 1}:</span>
                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expected Results */}
              <div>
                <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-faint)', letterSpacing: '0.05em', marginBottom: '8px' }}>
                  Expected Automotive System Responses
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {selectedTestCase.expected_results.map((exp: string, idx: number) => (
                    <div key={idx} style={{ padding: '8px 12px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '4px', fontSize: '13px', display: 'flex', gap: '8px', color: '#6ee7b7' }}>
                      <CheckCircle2 size={15} style={{ flexShrink: 0, marginTop: '2px' }} />
                      <span>{exp}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Pass/Fail Criteria & Safety Notes */}
              <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                  Pass/Fail Acceptance Criteria
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  {selectedTestCase.pass_fail_criteria}
                </div>
                {selectedTestCase.safety_notes && (
                  <div style={{ marginTop: '8px', fontSize: '12px', color: '#fbbf24' }}>
                    Safety Note: {selectedTestCase.safety_notes}
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer with Simulation Run Button */}
            <div style={{
              padding: '16px 24px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'var(--bg-secondary)'
            }}>
              <div style={{ fontSize: '12px', color: 'var(--text-faint)' }}>
                Deterministic simulation engine ready for test execution.
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button className="btn-secondary" onClick={() => setSelectedTestCase(null)}>
                  Close
                </button>
                <button 
                  className="btn-primary" 
                  disabled={simulating}
                  onClick={() => handleRunSimulation(selectedTestCase.id)}
                >
                  <Play size={14} /> {simulating ? 'Simulating...' : 'Run Simulation'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
