import { useState } from 'react';
import { 
  Activity, FileText, Cpu, Layers, Zap, Play, 
  Gauge, AlertTriangle, FileSpreadsheet 
} from 'lucide-react';
import { DashboardView } from './components/DashboardView';
import { RequirementsView } from './components/RequirementsView';
import { VehicleArchitectureView } from './components/VehicleArchitectureView';
import { ScenariosView } from './components/ScenariosView';
import { TestCasesView } from './components/TestCasesView';
import { SimulationView } from './components/SimulationView';
import { CoverageView } from './components/CoverageView';
import { SpecificationGapsView } from './components/SpecificationGapsView';
import { ReportsView } from './components/ReportsView';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'requirements', label: 'Requirements', icon: FileText },
    { id: 'architecture', label: 'Vehicle Architecture', icon: Cpu },
    { id: 'scenarios', label: 'Scenarios', icon: Layers },
    { id: 'tests', label: 'Test Cases', icon: Zap },
    { id: 'simulation', label: 'Simulation', icon: Play },
    { id: 'coverage', label: 'Coverage', icon: Gauge },
    { id: 'gaps', label: 'Specification Gaps', icon: AlertTriangle },
    { id: 'reports', label: 'Reports', icon: FileSpreadsheet },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-primary)' }}>
      {/* Top Engineering Nav Header */}
      <header style={{
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-subtle)',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          height: '64px',
          borderBottom: '1px solid #141c2c'
        }}>
          {/* Logo & Product Title */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #0284c7 0%, #06b6d4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: '0 0 14px var(--accent-cyan-glow)'
            }}>
              <Activity size={20} />
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '17px', fontWeight: 800, letterSpacing: '-0.02em', color: '#ffffff' }}>
                  CIVIC-AI
                </span>
                <span className="badge badge-cyan font-mono" style={{ fontSize: '10px' }}>
                  B2B AUTOMOTIVE VALIDATION
                </span>
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>
                Context-Aware Intelligent Vehicle Inspection & Compliance AI
              </div>
            </div>
          </div>

          {/* Reference Vehicle Telemetry Ribbon */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--bg-card)', padding: '5px 12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--status-pass)' }} className="pulse-indicator" />
              <span className="font-mono" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                PUSV-01 [SW: PUSV-SW-0.1]
              </span>
            </div>

            <button 
              className="btn-primary" 
              style={{ padding: '6px 14px', fontSize: '12px' }}
              onClick={() => setActiveTab('simulation')}
            >
              <Play size={13} /> Pune Monsoon Demo
            </button>
          </div>
        </div>

        {/* Sub-Navigation Tabs */}
        <div style={{ display: 'flex', gap: '2px', overflowX: 'auto', paddingTop: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  borderBottom: isActive ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                  padding: '10px 16px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: isActive ? 'var(--accent-cyan)' : 'var(--text-muted)',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '13px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  whiteSpace: 'nowrap'
                }}
              >
                <Icon size={15} color={isActive ? 'var(--accent-cyan)' : 'var(--text-faint)'} />
                {item.label}
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Body */}
      <main style={{ flex: 1, padding: '24px', maxWidth: '1600px', width: '100%', margin: '0 auto' }}>
        {activeTab === 'dashboard' && <DashboardView onNavigate={(tab) => setActiveTab(tab)} />}
        {activeTab === 'requirements' && <RequirementsView />}
        {activeTab === 'architecture' && <VehicleArchitectureView />}
        {activeTab === 'scenarios' && <ScenariosView />}
        {activeTab === 'tests' && <TestCasesView />}
        {activeTab === 'simulation' && <SimulationView />}
        {activeTab === 'coverage' && <CoverageView />}
        {activeTab === 'gaps' && <SpecificationGapsView />}
        {activeTab === 'reports' && <ReportsView />}
      </main>

      {/* Engineering Footer */}
      <footer style={{
        background: 'var(--bg-secondary)',
        borderTop: '1px solid var(--border-subtle)',
        padding: '12px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '11px',
        color: 'var(--text-faint)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span>PUSV-01: Pune Urban Safety Vehicle (Fictional Reference Platform)</span>
          <span>&bull;</span>
          <span>ISO 26262 ASIL-D Compliant Architecture Model</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span>Deterministic Verification Mode: <strong style={{ color: 'var(--status-pass)' }}>ACTIVE</strong></span>
          <span>FastAPI + SQLite Engine: <strong style={{ color: 'var(--accent-cyan)' }}>ONLINE</strong></span>
        </div>
      </footer>
    </div>
  );
}

export default App;
