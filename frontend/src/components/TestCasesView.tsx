import React, { useEffect, useState } from 'react';
import { api, type TestCaseItem } from '../api/client';
import { 
  CheckCircle2, AlertTriangle, FileCheck, ArrowRight, X, Play,
  Sparkles, ShieldCheck, FileText
} from 'lucide-react';

export const TestCasesView: React.FC = () => {
  const [testCases, setTestCases] = useState<TestCaseItem[]>([]);
  const [selectedTestCase, setSelectedTestCase] = useState<any | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [originFilter, setOriginFilter] = useState<string>(''); // '', 'AI_GENERATED', 'SEEDED'
  const [valStatusFilter, setValStatusFilter] = useState<string>(''); // '', 'VALID', 'REQUIRES_REVIEW', 'INVALID'
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
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>SIM:</span>
            <button
              className="btn-secondary"
              style={{ padding: '3px 8px', fontSize: '11px', borderColor: statusFilter === 'VALIDATED' ? 'var(--status-pass)' : 'var(--border-subtle)' }}
              onClick={() => setStatusFilter(statusFilter === 'VALIDATED' ? '' : 'VALIDATED')}
            >
              Pass
            </button>
            <button
              className="btn-secondary"
              style={{ padding: '3px 8px', fontSize: '11px', borderColor: statusFilter === 'BLOCKED' ? 'var(--status-blocked)' : 'var(--border-subtle)' }}
              onClick={() => setStatusFilter(statusFilter === 'BLOCKED' ? '' : 'BLOCKED')}
            >
              Blocked
            </button>
          </div>

          {/* Origin Filter */}
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>ORIGIN:</span>
            <button
              className="btn-secondary"
              style={{
                padding: '3px 8px',
                fontSize: '11px',
                borderColor: originFilter === 'AI_GENERATED' ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                color: originFilter === 'AI_GENERATED' ? 'var(--accent-cyan)' : 'var(--text-faint)'
              }}
              onClick={() => setOriginFilter(originFilter === 'AI_GENERATED' ? '' : 'AI_GENERATED')}
            >
              <Sparkles size={11} style={{ display: 'inline', marginRight: '3px' }} /> AI Generated
            </button>
            <button
              className="btn-secondary"
              style={{
                padding: '3px 8px',
                fontSize: '11px',
                borderColor: originFilter === 'SEEDED' ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                color: originFilter === 'SEEDED' ? 'var(--accent-cyan)' : 'var(--text-faint)'
              }}
              onClick={() => setOriginFilter(originFilter === 'SEEDED' ? '' : 'SEEDED')}
            >
              Seeded
            </button>
          </div>

          {/* Validation Status Filter */}
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>VALIDATION:</span>
            {['VALID', 'REQUIRES_REVIEW'].map(v => (
              <button
                key={v}
                className="btn-secondary"
                style={{
                  padding: '3px 8px',
                  fontSize: '11px',
                  borderColor: valStatusFilter === v ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                  color: valStatusFilter === v ? 'var(--accent-cyan)' : 'var(--text-faint)'
                }}
                onClick={() => setValStatusFilter(valStatusFilter === v ? '' : v)}
              >
                {v === 'VALID' ? 'Valid' : 'Requires Review'}
              </button>
            ))}
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
                <th style={{ width: '130px' }}>Category</th>
                <th style={{ width: '65px' }}>Priority</th>
                <th>Participating ECUs</th>
                <th style={{ width: '110px' }}>Origin / AI</th>
                <th style={{ width: '120px' }}>Deterministic Validation</th>
                <th style={{ width: '95px' }}>Sim Status</th>
                <th style={{ width: '90px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {testCases
                .filter(tc => {
                  if (originFilter === 'AI_GENERATED') return tc.is_ai_generated || !!tc.generation_provider;
                  if (originFilter === 'SEEDED') return !tc.generation_provider && !tc.code.startsWith('TC-AI-');
                  return true;
                })
                .filter(tc => {
                  if (valStatusFilter) return (tc.validation_status || 'VALID') === valStatusFilter;
                  return true;
                })
                .map((tc) => {
                  const resStatus = tc.latest_result?.status || tc.status;
                  const isBlocked = resStatus === 'BLOCKED';
                  const isAi = tc.is_ai_generated || !!tc.generation_provider || tc.code.startsWith('TC-AI-');
                  const valStatus = tc.validation_status || (tc.specification_gaps?.length > 0 ? 'REQUIRES_REVIEW' : 'VALID');

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
                      <td>
                        {isAi ? (
                          <div>
                            <span className="badge badge-cyan" style={{ fontSize: '10px', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                              <Sparkles size={10} /> AI GENERATED
                            </span>
                            <div style={{ fontSize: '10px', color: 'var(--text-faint)', marginTop: '2px' }}>
                              Prov: {(tc.generation_provider || 'mock').toUpperCase()}
                            </div>
                          </div>
                        ) : (
                          <span className="badge badge-muted" style={{ fontSize: '10px' }}>
                            SEEDED
                          </span>
                        )}
                      </td>
                      <td>
                        {valStatus === 'VALID' && (
                          <span className="badge badge-pass" style={{ fontSize: '10px' }}>
                            <ShieldCheck size={11} /> VALID
                          </span>
                        )}
                        {valStatus === 'REQUIRES_REVIEW' && (
                          <span className="badge badge-fail" style={{ fontSize: '10px', background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                            <AlertTriangle size={11} /> REQUIRES REVIEW
                          </span>
                        )}
                        {valStatus === 'INVALID' && (
                          <span className="badge badge-fail" style={{ fontSize: '10px' }}>
                            INVALID
                          </span>
                        )}
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
                  {selectedTestCase.validation_status === 'VALID' && (
                    <span className="badge badge-pass"><ShieldCheck size={11} /> DETERMINISTICALLY VALIDATED</span>
                  )}
                  {selectedTestCase.validation_status === 'REQUIRES_REVIEW' && (
                    <span className="badge" style={{ background: 'rgba(245,158,11,0.15)', color: '#fbbf24', border: '1px solid rgba(245,158,11,0.3)' }}>
                      <AlertTriangle size={11} /> REQUIRES ENGINEERING REVIEW
                    </span>
                  )}
                  {(selectedTestCase.is_ai_generated || selectedTestCase.generation_provider) && (
                    <span className="badge badge-cyan">
                      <Sparkles size={11} /> AI GENERATED ({selectedTestCase.generation_provider || 'MOCK'})
                    </span>
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
              
              {/* Phase 3 Validation Finding Banner */}
              {selectedTestCase.validation_findings && selectedTestCase.validation_findings.length > 0 && (
                <div style={{
                  padding: '12px 16px',
                  background: selectedTestCase.validation_status === 'REQUIRES_REVIEW' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  border: `1px solid ${selectedTestCase.validation_status === 'REQUIRES_REVIEW' ? 'rgba(245, 158, 11, 0.35)' : 'rgba(239, 68, 68, 0.35)'}`,
                  borderRadius: '6px',
                  fontSize: '12px'
                }}>
                  <div style={{
                    fontWeight: 700,
                    color: selectedTestCase.validation_status === 'REQUIRES_REVIEW' ? '#fbbf24' : '#f87171',
                    marginBottom: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <ShieldCheck size={16} /> Deterministic Validation Findings:
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-main)', lineHeight: 1.5 }}>
                    {selectedTestCase.validation_findings.map((f: any, idx: number) => (
                      <li key={idx}>
                        <strong style={{ color: 'var(--accent-cyan)' }}>[{f.code}]:</strong> {f.message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Source Document Traceability Card */}
              {selectedTestCase.traceability?.source_document && (
                <div style={{
                  padding: '12px 16px',
                  background: 'rgba(6, 182, 212, 0.08)',
                  border: '1px solid rgba(6, 182, 212, 0.25)',
                  borderRadius: '6px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '12px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={16} color="var(--accent-cyan)" />
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Source Requirement Document: </span>
                      <strong style={{ color: '#ffffff' }}>{selectedTestCase.traceability.source_document}</strong>
                      {selectedTestCase.traceability.source_page && (
                        <span style={{ color: 'var(--accent-cyan)', marginLeft: '6px' }}>
                          (Page {selectedTestCase.traceability.source_page})
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="badge badge-cyan font-mono">
                    Req: {selectedTestCase.traceability.requirement_id || selectedTestCase.requirement_ids[0]}
                  </span>
                </div>
              )}

              {/* Specification Gaps preserved */}
              {selectedTestCase.specification_gaps && selectedTestCase.specification_gaps.length > 0 && (
                <div style={{
                  padding: '12px 16px',
                  background: 'rgba(239, 68, 68, 0.08)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '6px'
                }}>
                  <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#f87171', fontWeight: 700, marginBottom: '6px' }}>
                    Specification Gaps Acknowledged by AI (Zero Hallucination)
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {selectedTestCase.specification_gaps.map((gap: string) => (
                      <span key={gap} className="badge badge-fail font-mono" style={{ fontSize: '11px' }}>
                        {gap}
                      </span>
                    ))}
                  </div>
                </div>
              )}

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
