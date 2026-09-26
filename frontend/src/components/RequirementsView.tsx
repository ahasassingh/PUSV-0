import React, { useEffect, useState, useRef } from 'react';
import { api, type RequirementItem, type RequirementUploadResult, type TestGenerationResponse } from '../api/client';
import { 
  FileText, Search, AlertTriangle, CheckCircle2, 
  HelpCircle, X, UploadCloud, FileCheck, AlertCircle, File,
  Sparkles, CheckSquare, Square, ShieldCheck, RefreshCw
} from 'lucide-react';

export const RequirementsView: React.FC = () => {
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [selectedReq, setSelectedReq] = useState<any | null>(null);
  const [systemFilter, setSystemFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [sourceFilter, setSourceFilter] = useState<string>('');
  const [search, setSearch] = useState<string>('');

  // Bulk selection & Generation Modal
  const [selectedReqIds, setSelectedReqIds] = useState<string[]>([]);
  const [showGenModal, setShowGenModal] = useState<boolean>(false);
  const [genLoading, setGenLoading] = useState<boolean>(false);
  const [genError, setGenError] = useState<string | null>(null);
  const [genResult, setGenResult] = useState<TestGenerationResponse | null>(null);
  const [genCategories, setGenCategories] = useState<string[]>([
    'FUNCTIONAL', 'BOUNDARY', 'NEGATIVE', 'FAULT_INJECTION', 'TIMING', 'INTEGRATION'
  ]);
  const [testsPerReq, setTestsPerReq] = useState<number>(3);
  const [genProvider, setGenProvider] = useState<string>('mock');

  // Upload state
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [uploadLoading, setUploadLoading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<RequirementUploadResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadRequirements = () => {
    api.getRequirements({
      system: systemFilter || undefined,
      status: statusFilter || undefined,
      search: search || undefined
    })
      .then((data) => {
        if (sourceFilter) {
          setRequirements(data.filter(r => (r.source_type || 'seed') === sourceFilter));
        } else {
          setRequirements(data);
        }
      })
      .catch(console.error);
  };

  useEffect(() => {
    loadRequirements();
  }, [systemFilter, statusFilter, sourceFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadRequirements();
  };

  const handleSelectReq = (reqId: string) => {
    api.getRequirementDetail(reqId)
      .then(setSelectedReq)
      .catch(console.error);
  };

  const handleFileUpload = async (file: File) => {
    setUploadError(null);
    setUploadResult(null);
    setUploadLoading(true);

    try {
      const result = await api.uploadRequirementDocument(file);
      setUploadResult(result);
      loadRequirements();
    } catch (err: any) {
      setUploadError(err.message || 'Document upload and parsing failed');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleToggleReqSelect = (reqCode: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedReqIds(prev => 
      prev.includes(reqCode) ? prev.filter(id => id !== reqCode) : [...prev, reqCode]
    );
  };

  const handleToggleSelectAll = () => {
    if (selectedReqIds.length === requirements.length) {
      setSelectedReqIds([]);
    } else {
      setSelectedReqIds(requirements.map(r => r.req_code));
    }
  };

  const handleOpenGenerationModal = (reqCode?: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (reqCode) {
      setSelectedReqIds([reqCode]);
    }
    setGenError(null);
    setGenResult(null);
    setShowGenModal(true);
  };

  const handleRunGeneration = async () => {
    if (selectedReqIds.length === 0) return;
    setGenLoading(true);
    setGenError(null);

    try {
      const response = await api.generateTestCases({
        requirement_ids: selectedReqIds,
        categories: genCategories,
        tests_per_requirement: testsPerReq,
        provider: genProvider
      });
      setGenResult(response);
      loadRequirements();
    } catch (err: any) {
      setGenError(err.message || 'Test generation failed');
    } finally {
      setGenLoading(false);
    }
  };

  const systems = ['Braking', 'ADAS', 'TPMS', 'Suspension', 'Communication', 'Diagnostics'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Top Section: Drag & Drop Document Ingestion Panel */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <UploadCloud size={18} color="var(--accent-cyan)" />
              Automotive Requirements Document Ingestion
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-faint)', marginTop: '2px' }}>
              Deterministic extraction & normalization for PDF, DOCX, and TXT specifications (Max 10 MB).
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
            <span className="badge badge-muted">Deterministic Regex</span>
            <span className="badge badge-muted">Zero Hallucination</span>
            <span className="badge badge-cyan">ISO 26262 ASIL Support</span>
          </div>
        </div>

        {/* Drag and Drop Zone */}
        <div 
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${isDragging ? 'var(--accent-cyan)' : 'var(--border-subtle)'}`,
            borderRadius: '8px',
            padding: '24px 20px',
            textAlign: 'center',
            cursor: 'pointer',
            background: isDragging ? 'rgba(6, 182, 212, 0.08)' : 'rgba(15, 23, 42, 0.4)',
            transition: 'all 0.2s ease'
          }}
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])} 
            accept=".pdf,.docx,.txt"
            style={{ display: 'none' }} 
          />
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
            <UploadCloud size={28} color={isDragging ? 'var(--accent-cyan)' : 'var(--text-muted)'} />
            <div style={{ fontSize: '13px', fontWeight: 500, color: '#ffffff' }}>
              {uploadLoading ? 'Extracting & Normalizing Requirements...' : 'Drag & drop requirement document here, or click to browse'}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>
              Supports .PDF (selectable text), .DOCX (paragraphs & tables), .TXT (line-structured)
            </div>
          </div>
        </div>

        {/* Upload Error Banner */}
        {uploadError && (
          <div style={{
            marginTop: '12px',
            padding: '10px 14px',
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '12px',
            color: '#fca5a5'
          }}>
            <AlertCircle size={16} />
            <span><strong>Upload Error:</strong> {uploadError}</span>
          </div>
        )}

        {/* Upload Success Banner */}
        {uploadResult && (
          <div style={{
            marginTop: '12px',
            padding: '12px 16px',
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            borderRadius: '6px',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            fontSize: '12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--status-pass)', fontWeight: 600 }}>
                <FileCheck size={16} />
                Document Ingestion Complete: {uploadResult.filename}
              </div>
              <span className="badge badge-pass">{uploadResult.status}</span>
            </div>
            <div style={{ display: 'flex', gap: '16px', color: 'var(--text-muted)', fontSize: '11px', marginTop: '2px' }}>
              <span>Detected: <strong style={{ color: '#ffffff' }}>{uploadResult.requirements_detected}</strong></span>
              <span>Imported: <strong style={{ color: 'var(--accent-cyan)' }}>{uploadResult.requirements_imported}</strong></span>
              <span>Duplicates: <strong style={{ color: uploadResult.duplicates > 0 ? '#fca5a5' : '#ffffff' }}>{uploadResult.duplicates}</strong></span>
              <span>Specification Gaps: <strong style={{ color: uploadResult.specification_gaps > 0 ? '#f59e0b' : 'var(--status-pass)' }}>{uploadResult.specification_gaps}</strong></span>
            </div>
            {uploadResult.warnings.length > 0 && (
              <div style={{ marginTop: '4px', fontSize: '11px', color: '#f59e0b' }}>
                Warnings: {uploadResult.warnings.join(' | ')}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel" style={{ padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>SYSTEM:</span>
          <button 
            className={`btn-secondary ${!systemFilter ? 'active' : ''}`}
            style={{ padding: '3px 8px', fontSize: '11px', borderColor: !systemFilter ? 'var(--accent-cyan)' : 'var(--border-subtle)' }}
            onClick={() => setSystemFilter('')}
          >
            All
          </button>
          {systems.map((s) => (
            <button
              key={s}
              className="btn-secondary"
              style={{ 
                padding: '3px 8px', 
                fontSize: '11px',
                borderColor: systemFilter === s ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                color: systemFilter === s ? 'var(--accent-cyan)' : 'var(--text-main)'
              }}
              onClick={() => setSystemFilter(s)}
            >
              {s}
            </button>
          ))}
          
          <div style={{ marginLeft: '10px', display: 'flex', gap: '6px', alignItems: 'center' }}>
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

          <div style={{ marginLeft: '10px', display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>ORIGIN:</span>
            {[
              { id: '', label: 'All' },
              { id: 'seed', label: 'Seed' },
              { id: 'uploaded_document', label: 'Imported' }
            ].map((src) => (
              <button
                key={src.id}
                className="btn-secondary"
                style={{
                  padding: '3px 8px',
                  fontSize: '11px',
                  borderColor: sourceFilter === src.id ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                  color: sourceFilter === src.id ? 'var(--accent-cyan)' : 'var(--text-faint)'
                }}
                onClick={() => setSourceFilter(src.id)}
              >
                {src.label}
              </button>
            ))}
          </div>
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search ID, text, source..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-strong)',
                color: '#ffffff',
                padding: '6px 12px 6px 30px',
                borderRadius: '6px',
                fontSize: '12px',
                width: '220px'
              }}
            />
            <Search size={14} style={{ position: 'absolute', left: '10px', top: '8px', color: 'var(--text-faint)' }} />
          </div>
          <button type="submit" className="btn-primary" style={{ padding: '5px 12px', fontSize: '11px' }}>
            Filter
          </button>
        </form>
      </div>

      {/* Requirements Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText size={18} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '15px', fontWeight: 600 }}>Vehicle Software Specifications ({requirements.length})</h2>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {selectedReqIds.length > 0 && (
              <span style={{ fontSize: '12px', color: 'var(--accent-cyan)', fontWeight: 500 }}>
                {selectedReqIds.length} selected
              </span>
            )}
            <button
              className="btn-primary"
              disabled={selectedReqIds.length === 0}
              onClick={() => handleOpenGenerationModal()}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                fontSize: '12px',
                background: selectedReqIds.length > 0 ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.05)',
                color: selectedReqIds.length > 0 ? '#000000' : 'var(--text-faint)',
                cursor: selectedReqIds.length > 0 ? 'pointer' : 'not-allowed'
              }}
            >
              <Sparkles size={14} />
              Generate Test Cases ({selectedReqIds.length})
            </button>
          </div>
        </div>

        <div style={{ overflowX: 'auto', maxHeight: '600px' }}>
          <table className="eng-table">
            <thead>
              <tr>
                <th style={{ width: '40px', textAlign: 'center' }}>
                  <button
                    onClick={handleToggleSelectAll}
                    style={{ background: 'transparent', border: 'none', color: 'var(--accent-cyan)', cursor: 'pointer', padding: 0 }}
                    title="Select All Requirements"
                  >
                    {selectedReqIds.length > 0 && selectedReqIds.length === requirements.length ? (
                      <CheckSquare size={16} />
                    ) : (
                      <Square size={16} />
                    )}
                  </button>
                </th>
                <th style={{ width: '130px' }}>Req Code</th>
                <th>System / Subsystem</th>
                <th style={{ width: '150px' }}>Source Traceability</th>
                <th style={{ width: '90px' }}>Safety</th>
                <th>Requirement Specification</th>
                <th style={{ width: '130px' }}>Completeness</th>
                <th style={{ width: '90px' }}>Gaps</th>
                <th style={{ width: '70px' }}>Origin</th>
                <th style={{ width: '120px' }}>AI Actions</th>
              </tr>
            </thead>
            <tbody>
              {requirements.map((req) => {
                const isSelected = selectedReqIds.includes(req.req_code);
                return (
                  <tr 
                    key={req.id} 
                    onClick={() => handleSelectReq(req.id)}
                    style={{ cursor: 'pointer', background: isSelected ? 'rgba(6, 182, 212, 0.05)' : undefined }}
                  >
                    <td style={{ textAlign: 'center' }} onClick={(e) => handleToggleReqSelect(req.req_code, e)}>
                      <button
                        style={{ background: 'transparent', border: 'none', color: isSelected ? 'var(--accent-cyan)' : 'var(--text-faint)', cursor: 'pointer', padding: 0 }}
                      >
                        {isSelected ? <CheckSquare size={16} /> : <Square size={16} />}
                      </button>
                    </td>
                    <td className="font-mono" style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>
                      {req.req_code}
                    </td>
                    <td>
                      <div style={{ fontWeight: 500 }}>{req.system}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>{req.subsystem || '—'}</div>
                    </td>
                    <td>
                      {req.source_traceability?.source_document ? (
                        <div style={{ fontSize: '11px' }}>
                          <div style={{ fontWeight: 500, color: '#e2e8f0', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <File size={12} color="var(--accent-cyan)" />
                            {req.source_traceability.source_document}
                          </div>
                          <div style={{ color: 'var(--text-faint)', fontSize: '10px' }}>
                            {req.source_traceability.source_page ? `Page ${req.source_traceability.source_page}` : ''}
                            {req.source_traceability.source_location ? ` • ${req.source_traceability.source_location}` : ''}
                          </div>
                        </div>
                      ) : (
                        <span className="badge badge-muted font-mono" style={{ fontSize: '10px' }}>
                          {req.ecu_name}
                        </span>
                      )}
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
                    <td style={{ maxWidth: '380px', lineHeight: 1.4 }}>
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
                    <td>
                      <span className="badge badge-muted" style={{ fontSize: '10px' }}>
                        {req.source_type === 'uploaded_document' ? 'DOC' : 'SEED'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-secondary"
                        onClick={(e) => handleOpenGenerationModal(req.req_code, e)}
                        style={{
                          padding: '3px 8px',
                          fontSize: '11px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          borderColor: 'var(--accent-cyan)',
                          color: 'var(--accent-cyan)'
                        }}
                        title="Generate structured test cases with AI"
                      >
                        <Sparkles size={11} /> Generate
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Requirement Detail Modal with Source Traceability */}
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
                <span className="badge badge-muted">{selectedReq.system} / {selectedReq.subsystem || 'General'}</span>
                <span className="badge badge-muted">ASIL: {selectedReq.safety_relevance}</span>
                <span className="badge badge-muted">Origin: {selectedReq.source_type === 'uploaded_document' ? 'Uploaded Doc' : 'Seed'}</span>
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

              {/* Source Traceability Card */}
              {selectedReq.source_traceability?.source_document && (
                <div style={{
                  padding: '14px 18px',
                  background: 'rgba(6, 182, 212, 0.08)',
                  border: '1px solid rgba(6, 182, 212, 0.25)',
                  borderRadius: '6px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--accent-cyan)', fontWeight: 600, letterSpacing: '0.05em' }}>
                      Document Traceability Matrix
                    </div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#ffffff', marginTop: '4px' }}>
                      Document: {selectedReq.source_traceability.source_document}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Page: {selectedReq.source_traceability.source_page ?? 'N/A'} • 
                      Section: {selectedReq.source_traceability.source_section ?? 'N/A'} • 
                      Location: {selectedReq.source_traceability.source_location ?? 'N/A'}
                    </div>
                  </div>
                  <span className="badge badge-cyan font-mono">TRACEABLE</span>
                </div>
              )}

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
                  Automotive Test Cases ({selectedReq.test_cases?.length || 0})
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
                    Phase 3 AI test case generation ready for this requirement.
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div style={{
              padding: '14px 24px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'var(--bg-secondary)'
            }}>
              <button 
                className="btn-primary"
                onClick={() => {
                  const code = selectedReq.req_code;
                  setSelectedReq(null);
                  handleOpenGenerationModal(code);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 14px',
                  fontSize: '12px'
                }}
              >
                <Sparkles size={14} /> Generate Test Cases
              </button>
              <button className="btn-secondary" onClick={() => setSelectedReq(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Phase 3 AI Test Case Generation Modal */}
      {showGenModal && (
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
            maxWidth: '720px',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            border: '1px solid var(--border-strong)',
            boxShadow: '0 20px 40px rgba(0,0,0,0.6)'
          }}>
            {/* Header */}
            <div style={{
              padding: '16px 22px',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'var(--bg-secondary)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={18} color="var(--accent-cyan)" />
                <h3 style={{ fontSize: '16px', fontWeight: 600 }}>AI Automotive Test Case Generator</h3>
                <span className="badge badge-cyan">PHASE 3</span>
              </div>
              <button
                onClick={() => setShowGenModal(false)}
                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Body */}
            <div style={{ padding: '22px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '18px' }}>
              
              {/* Notice */}
              <div style={{
                padding: '10px 14px',
                background: 'rgba(6, 182, 212, 0.08)',
                border: '1px solid rgba(6, 182, 212, 0.25)',
                borderRadius: '6px',
                fontSize: '12px',
                color: '#e2e8f0',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                <ShieldCheck size={18} color="var(--accent-cyan)" />
                <span>
                  <strong>Engineering Rule:</strong> AI proposes test cases. Deterministic validators enforce zero hallucinated thresholds or timing.
                </span>
              </div>

              {/* Target Requirements */}
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                  TARGET REQUIREMENTS ({selectedReqIds.length})
                </label>
                <div style={{
                  padding: '8px 12px',
                  background: 'var(--bg-secondary)',
                  borderRadius: '6px',
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '6px',
                  maxHeight: '80px',
                  overflowY: 'auto'
                }}>
                  {selectedReqIds.map(id => (
                    <span key={id} className="badge badge-cyan font-mono" style={{ fontSize: '11px' }}>
                      {id}
                    </span>
                  ))}
                </div>
              </div>

              {/* Categories */}
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
                  TARGET TEST CATEGORIES
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                  {['FUNCTIONAL', 'BOUNDARY', 'NEGATIVE', 'FAULT_INJECTION', 'TIMING', 'INTEGRATION'].map(cat => {
                    const isChecked = genCategories.includes(cat);
                    return (
                      <button
                        key={cat}
                        type="button"
                        onClick={() => {
                          setGenCategories(prev => 
                            prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]
                          );
                        }}
                        style={{
                          padding: '8px 10px',
                          borderRadius: '6px',
                          border: isChecked ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                          background: isChecked ? 'rgba(6, 182, 212, 0.12)' : 'var(--bg-secondary)',
                          color: isChecked ? 'var(--accent-cyan)' : 'var(--text-muted)',
                          fontSize: '11px',
                          fontWeight: 600,
                          cursor: 'pointer',
                          textAlign: 'left',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                      >
                        {isChecked ? <CheckCircle2 size={13} /> : <div style={{ width: 13, height: 13, border: '1px solid var(--border-subtle)', borderRadius: 2 }} />}
                        {cat.replace('_', ' ')}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Config Row */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                    TESTS PER REQUIREMENT
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={6}
                    value={testsPerReq}
                    onChange={(e) => setTestsPerReq(parseInt(e.target.value) || 1)}
                    style={{
                      width: '100%',
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-strong)',
                      color: '#ffffff',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      fontSize: '13px'
                    }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                    AI GENERATOR PROVIDER
                  </label>
                  <select
                    value={genProvider}
                    onChange={(e) => setGenProvider(e.target.value)}
                    style={{
                      width: '100%',
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-strong)',
                      color: '#ffffff',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      fontSize: '13px'
                    }}
                  >
                    <option value="mock">MOCK (Deterministic Anti-Hallucination)</option>
                    <option value="gemini">Gemini (gemini-1.5-pro)</option>
                  </select>
                </div>
              </div>

              {/* Error */}
              {genError && (
                <div style={{
                  padding: '10px 14px',
                  background: 'rgba(239, 68, 68, 0.12)',
                  border: '1px solid rgba(239, 68, 68, 0.4)',
                  borderRadius: '6px',
                  fontSize: '12px',
                  color: '#fca5a5'
                }}>
                  {genError}
                </div>
              )}

              {/* Generation Result Banner */}
              {genResult && (
                <div style={{
                  padding: '14px',
                  background: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '6px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  fontSize: '12px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontWeight: 600, color: 'var(--status-pass)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <CheckCircle2 size={16} /> Run {genResult.run_id} Completed
                    </div>
                    <span className="badge badge-muted">Provider: {genResult.provider.toUpperCase()}</span>
                  </div>
                  <div style={{ display: 'flex', gap: '16px', color: 'var(--text-muted)', fontSize: '11px' }}>
                    <span>Generated: <strong style={{ color: 'var(--accent-cyan)' }}>{genResult.generated_tests_count}</strong></span>
                    <span>Valid: <strong style={{ color: 'var(--status-pass)' }}>{genResult.validation_summary.VALID}</strong></span>
                    <span>Requires Review: <strong style={{ color: '#f59e0b' }}>{genResult.validation_summary.REQUIRES_REVIEW}</strong></span>
                    <span>Invalid: <strong style={{ color: '#ef4444' }}>{genResult.validation_summary.INVALID}</strong></span>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div style={{
              padding: '14px 22px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '10px',
              background: 'var(--bg-secondary)'
            }}>
              <button
                className="btn-secondary"
                onClick={() => setShowGenModal(false)}
              >
                Close
              </button>
              <button
                className="btn-primary"
                disabled={genLoading || selectedReqIds.length === 0}
                onClick={handleRunGeneration}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 18px',
                  fontSize: '12px'
                }}
              >
                {genLoading ? <RefreshCw size={14} className="spin" /> : <Sparkles size={14} />}
                {genLoading ? 'Generating & Validating...' : 'Generate Test Cases'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
