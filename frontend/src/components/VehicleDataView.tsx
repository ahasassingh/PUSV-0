import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  AlertCircle,
  Compass,
  Gauge,
  ShieldCheck,
  RefreshCw,
  CheckCircle2,
  XCircle,
  FileText
} from 'lucide-react';

interface TelemetrySource {
  type: string;
  simulator?: string;
  provider: string;
  version?: string;
  session_id?: string;
}

interface Acceleration {
  longitudinal_g?: number;
  lateral_g?: number;
  vertical_g?: number;
}

interface VehicleDynamics {
  speed_kmh: number;
  rpm?: number;
  gear?: number;
  throttle?: number;
  brake?: number;
  steering_angle_deg?: number;
  acceleration?: Acceleration;
}

interface WheelState {
  slip?: number;
  load_n?: number;
  pressure_bar?: number;
  suspension_travel?: number;
  tyre_temperature_c?: number;
  brake_temperature_c?: number;
}

interface WheelsMap {
  FL?: WheelState;
  FR?: WheelState;
  RL?: WheelState;
  RR?: WheelState;
}

interface EnvironmentState {
  road_wetness?: number;
  road_roughness?: number;
  traffic_density?: number;
  front_obstacle_distance_m?: number;
  pedestrian_distance_m?: number;
  motorcycle_distance_m?: number;
  traffic_signal?: string;
}

interface SensorConfidences {
  camera_confidence?: number;
  radar_confidence?: number;
}

interface VehicleState {
  schema_version: string;
  timestamp: number;
  source: TelemetrySource;
  vehicle: VehicleDynamics;
  wheels?: WheelsMap;
  environment?: EnvironmentState;
  sensors?: SensorConfidences;
  provenance?: Record<string, string>;
}

export function VehicleDataView() {
  const [currentData, setCurrentData] = useState<VehicleState | null>(null);
  const [currentStateId, setCurrentStateId] = useState<string | null>(null);
  const [importedAt, setImportedAt] = useState<string | null>(null);
  const [statusState, setStatusState] = useState<'VALID' | 'INVALID' | 'PROCESSING' | 'NO_DATA'>('NO_DATA');
  const [errors, setErrors] = useState<Array<{ field: string; message: string }>>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchCurrentState = async () => {
    try {
      const res = await fetch('/api/v1/vehicle-data/current');
      if (!res.ok) return;
      const data = await res.json();
      if (data.status === 'AVAILABLE' && data.vehicle_state) {
        setCurrentData(data.vehicle_state);
        setCurrentStateId(data.vehicle_state_id);
        setImportedAt(data.imported_at);
        setStatusState('VALID');
        setErrors([]);
      } else {
        setStatusState('NO_DATA');
      }
    } catch (err) {
      console.error('Failed to fetch current vehicle state', err);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/v1/vehicle-data/history?limit=5');
      if (res.ok) {
        const hist = await res.json();
        setHistory(hist);
      }
    } catch (err) {
      console.error('Failed to fetch history', err);
    }
  };

  useEffect(() => {
    fetchCurrentState();
    fetchHistory();
  }, []);

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setStatusState('PROCESSING');
    setErrors([]);
    setWarnings([]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/vehicle-data/import', {
        method: 'POST',
        body: formData,
      });

      const result = await res.json();

      if (res.ok && result.status === 'VALID') {
        setStatusState('VALID');
        setWarnings(result.warnings || []);
        await fetchCurrentState();
        await fetchHistory();
      } else {
        setStatusState('INVALID');
        setErrors(result.errors || [{ field: 'upload', message: 'Failed to validate uploaded vehicle state' }]);
      }
    } catch (err: any) {
      setStatusState('INVALID');
      setErrors([{ field: 'network', message: err?.message || 'Network error communicating with validation service' }]);
    } finally {
      setIsUploading(false);
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const getProvenanceBadge = (fieldKey: string) => {
    if (!currentData?.provenance) return null;
    const prov = currentData.provenance[fieldKey];
    if (!prov) return null;

    if (prov.toLowerCase().includes('assetto') || prov.toLowerCase().includes('simulator')) {
      return (
        <span className="badge badge-cyan font-mono" style={{ fontSize: '9px', padding: '2px 6px' }}>
          SIMULATOR: {prov.toUpperCase()}
        </span>
      );
    } else if (prov.toLowerCase().includes('synthetic')) {
      return (
        <span className="badge badge-amber font-mono" style={{ fontSize: '9px', padding: '2px 6px' }}>
          SYNTHETIC
        </span>
      );
    }
    return (
      <span className="badge font-mono" style={{ fontSize: '9px', padding: '2px 6px', background: 'var(--border-subtle)', color: 'var(--text-muted)' }}>
        {prov.toUpperCase()}
      </span>
    );
  };

  const renderWheelBox = (posName: 'FL' | 'FR' | 'RL' | 'RR', wheel?: WheelState) => {
    if (!wheel) {
      return (
        <div style={{ background: 'var(--bg-secondary)', border: '1px dashed var(--border-subtle)', borderRadius: '8px', padding: '12px' }}>
          <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-faint)' }}>{posName}</div>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>No telemetry reported</div>
        </div>
      );
    }

    return (
      <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '14px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--accent-cyan)' }}>{posName} Wheel</span>
          {getProvenanceBadge(`wheels.${posName}.slip`)}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '11px' }}>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Slip Ratio: </span>
            <span className="font-mono" style={{ fontWeight: 600, color: '#ffffff' }}>
              {wheel.slip !== undefined && wheel.slip !== null ? wheel.slip.toFixed(2) : '—'}
            </span>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Load: </span>
            <span className="font-mono" style={{ fontWeight: 600, color: '#ffffff' }}>
              {wheel.load_n !== undefined && wheel.load_n !== null ? `${wheel.load_n} N` : '—'}
            </span>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Pressure: </span>
            <span className="font-mono" style={{ fontWeight: 600, color: '#ffffff' }}>
              {wheel.pressure_bar !== undefined && wheel.pressure_bar !== null ? `${wheel.pressure_bar.toFixed(2)} bar` : '—'}
            </span>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Suspension: </span>
            <span className="font-mono" style={{ fontWeight: 600, color: '#ffffff' }}>
              {wheel.suspension_travel !== undefined && wheel.suspension_travel !== null ? `${wheel.suspension_travel.toFixed(2)}` : '—'}
            </span>
          </div>
          {wheel.tyre_temperature_c !== undefined && wheel.tyre_temperature_c !== null && (
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Tyre Temp: </span>
              <span className="font-mono" style={{ fontWeight: 600, color: '#ffffff' }}>{wheel.tyre_temperature_c.toFixed(1)} °C</span>
            </div>
          )}
          {wheel.brake_temperature_c !== undefined && wheel.brake_temperature_c !== null && (
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Brake Temp: </span>
              <span className="font-mono" style={{ fontWeight: 600, color: '#ffffff' }}>{wheel.brake_temperature_c.toFixed(1)} °C</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header and Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '22px', fontWeight: 800, color: '#ffffff' }}>
              Vehicle Telemetry & State Ingestion
            </h1>
            <span className="badge badge-cyan font-mono" style={{ fontSize: '11px' }}>
              PUSV-01 CANONICAL JSON
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>
            Standardized multi-source telemetry adapter layer. Preserves real simulator measurements versus synthetic operational domain overlays.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            className="btn-secondary"
            onClick={() => { fetchCurrentState(); fetchHistory(); }}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RefreshCw size={14} /> Refresh State
          </button>
        </div>
      </div>

      {/* Grid: Upload Box + Validation Status */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
        {/* Upload Dropzone */}
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          style={{
            background: isDragging ? 'rgba(6, 182, 212, 0.05)' : 'var(--bg-card)',
            border: isDragging ? '2px dashed var(--accent-cyan)' : '1px dashed var(--border-strong)',
            borderRadius: '10px',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            style={{ display: 'none' }}
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
              }
            }}
          />
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              background: 'var(--status-info-bg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-cyan)',
              marginBottom: '12px',
            }}
          >
            <UploadCloud size={24} />
          </div>
          <div style={{ fontSize: '15px', fontWeight: 600, color: '#ffffff' }}>
            {isUploading ? 'Validating and Ingesting Payload...' : 'Import Vehicle-State JSON'}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', maxWidth: '420px' }}>
            Drag and drop your canonical vehicle telemetry payload here, or <span style={{ color: 'var(--accent-cyan)', textDecoration: 'underline' }}>Browse JSON</span>.
          </div>
          <div className="font-mono" style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '10px' }}>
            Supported Schema: pusv.vehicle-state.v1 &bull; Max Size: 5MB
          </div>
        </div>

        {/* Validation Status Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Validation State
            </div>

            <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              {statusState === 'VALID' && (
                <>
                  <CheckCircle2 size={24} color="var(--status-pass)" />
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--status-pass)' }}>VALID</div>
                    <div className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      ID: {currentStateId || 'VS-CURRENT'}
                    </div>
                  </div>
                </>
              )}
              {statusState === 'INVALID' && (
                <>
                  <XCircle size={24} color="var(--status-fail)" />
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--status-fail)' }}>INVALID SCHEMA</div>
                    <div style={{ fontSize: '11px', color: 'var(--status-fail)' }}>{errors.length} error(s) detected</div>
                  </div>
                </>
              )}
              {statusState === 'PROCESSING' && (
                <>
                  <RefreshCw size={24} color="var(--accent-cyan)" className="animate-spin" />
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--accent-cyan)' }}>PROCESSING</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Checking structural constraints</div>
                  </div>
                </>
              )}
              {statusState === 'NO_DATA' && (
                <>
                  <AlertCircle size={24} color="var(--text-faint)" />
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-muted)' }}>NO DATA IMPORTED</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Upload JSON payload to activate</div>
                  </div>
                </>
              )}
            </div>

            {/* Error List */}
            {errors.length > 0 && (
              <div style={{ marginTop: '12px', maxHeight: '110px', overflowY: 'auto', background: 'rgba(239, 68, 68, 0.08)', borderRadius: '6px', padding: '8px' }}>
                {errors.map((err, i) => (
                  <div key={i} style={{ fontSize: '11px', color: 'var(--status-fail)', marginBottom: '4px' }}>
                    <strong className="font-mono">{err.field}</strong>: {err.message}
                  </div>
                ))}
              </div>
            )}

            {/* Warnings */}
            {warnings.length > 0 && (
              <div style={{ marginTop: '10px', fontSize: '11px', color: 'var(--status-blocked)' }}>
                {warnings.map((w, i) => <div key={i}>&bull; {w}</div>)}
              </div>
            )}
          </div>

          {/* Source Provenance Info */}
          {currentData && (
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '10px', marginTop: '10px', fontSize: '11px' }}>
              {currentStateId && (
                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                  <span>Record ID:</span>
                  <span className="font-mono" style={{ color: 'var(--accent-cyan)' }}>{currentStateId}</span>
                </div>
              )}
              {importedAt && (
                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginTop: '2px' }}>
                  <span>Imported At:</span>
                  <span className="font-mono" style={{ color: '#ffffff' }}>{new Date(importedAt).toLocaleTimeString()}</span>
                </div>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginTop: '2px' }}>
                <span>Source:</span>
                <span className="font-mono" style={{ color: '#ffffff' }}>{currentData.source.simulator || currentData.source.type}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginTop: '2px' }}>
                <span>Provider:</span>
                <span className="font-mono" style={{ color: 'var(--accent-cyan)' }}>{currentData.source.provider}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginTop: '2px' }}>
                <span>Timestamp:</span>
                <span className="font-mono" style={{ color: '#ffffff' }}>{new Date(currentData.timestamp * 1000).toLocaleTimeString()}</span>
              </div>
              {history.length > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', marginTop: '2px' }}>
                  <span>History Frames:</span>
                  <span className="font-mono" style={{ color: 'var(--status-pass)' }}>{history.length} logged</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Vehicle Telemetry Visualization Panels */}
      {currentData ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Top Row: Vehicle Dynamics + Acceleration */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Vehicle Speed</span>
                {getProvenanceBadge('vehicle.speed_kmh')}
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '6px' }}>
                <span className="font-mono" style={{ fontSize: '28px', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                  {currentData.vehicle.speed_kmh.toFixed(1)}
                </span>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>km/h</span>
              </div>
            </div>

            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Engine RPM</span>
                {getProvenanceBadge('vehicle.rpm')}
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '6px' }}>
                <span className="font-mono" style={{ fontSize: '28px', fontWeight: 800, color: '#ffffff' }}>
                  {currentData.vehicle.rpm !== undefined && currentData.vehicle.rpm !== null ? currentData.vehicle.rpm : '—'}
                </span>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>RPM</span>
              </div>
            </div>

            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Gear & Steering</span>
                {getProvenanceBadge('vehicle.gear')}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: '6px' }}>
                <div>
                  <span className="font-mono" style={{ fontSize: '24px', fontWeight: 800, color: '#ffffff' }}>
                    {currentData.vehicle.gear !== undefined && currentData.vehicle.gear !== null ? `G${currentData.vehicle.gear}` : '—'}
                  </span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className="font-mono" style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                    {currentData.vehicle.steering_angle_deg !== undefined && currentData.vehicle.steering_angle_deg !== null ? `${currentData.vehicle.steering_angle_deg}°` : '—'}
                  </span>
                  <div style={{ fontSize: '10px', color: 'var(--text-faint)' }}>Steering</div>
                </div>
              </div>
            </div>

            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Throttle / Brake</span>
                {getProvenanceBadge('vehicle.throttle')}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '11px', width: '45px', color: 'var(--text-muted)' }}>THR:</span>
                  <div style={{ flex: 1, height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${(currentData.vehicle.throttle || 0) * 100}%`, height: '100%', background: 'var(--status-pass)' }} />
                  </div>
                  <span className="font-mono" style={{ fontSize: '11px', color: '#ffffff' }}>
                    {((currentData.vehicle.throttle || 0) * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '11px', width: '45px', color: 'var(--text-muted)' }}>BRK:</span>
                  <div style={{ flex: 1, height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${(currentData.vehicle.brake || 0) * 100}%`, height: '100%', background: 'var(--status-fail)' }} />
                  </div>
                  <span className="font-mono" style={{ fontSize: '11px', color: '#ffffff' }}>
                    {((currentData.vehicle.brake || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Wheels Quad Grid */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Gauge size={16} color="var(--accent-cyan)" />
                <span style={{ fontSize: '14px', fontWeight: 700, color: '#ffffff' }}>
                  Corner-by-Corner Wheel Telemetry
                </span>
              </div>
              <span className="badge badge-cyan font-mono" style={{ fontSize: '10px' }}>4-CORNER INDEPENDENT SENSING</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              {renderWheelBox('FL', currentData.wheels?.FL)}
              {renderWheelBox('FR', currentData.wheels?.FR)}
              {renderWheelBox('RL', currentData.wheels?.RL)}
              {renderWheelBox('RR', currentData.wheels?.RR)}
            </div>
          </div>

          {/* Environment & Sensors Row */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '14px' }}>
            {/* Operational Domain Environment */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Compass size={16} color="var(--accent-cyan)" />
                  <span style={{ fontSize: '14px', fontWeight: 700, color: '#ffffff' }}>Operational Domain & Surroundings</span>
                </div>
                {getProvenanceBadge('environment.traffic_signal')}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Traffic Signal</div>
                  <div className="font-mono" style={{
                    fontSize: '16px',
                    fontWeight: 800,
                    marginTop: '4px',
                    color: currentData.environment?.traffic_signal === 'RED' ? 'var(--status-fail)' :
                           currentData.environment?.traffic_signal === 'GREEN' ? 'var(--status-pass)' :
                           currentData.environment?.traffic_signal === 'YELLOW' ? 'var(--status-blocked)' : '#ffffff'
                  }}>
                    {currentData.environment?.traffic_signal || 'NOT DETECTED'}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Front Obstacle</div>
                  <div className="font-mono" style={{ fontSize: '16px', fontWeight: 800, marginTop: '4px', color: '#ffffff' }}>
                    {currentData.environment?.front_obstacle_distance_m !== undefined && currentData.environment?.front_obstacle_distance_m !== null ?
                      `${currentData.environment.front_obstacle_distance_m} m` : '—'}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Motorcycle Dist</div>
                  <div className="font-mono" style={{ fontSize: '16px', fontWeight: 800, marginTop: '4px', color: 'var(--status-blocked)' }}>
                    {currentData.environment?.motorcycle_distance_m !== undefined && currentData.environment?.motorcycle_distance_m !== null ?
                      `${currentData.environment.motorcycle_distance_m} m` : '—'}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Road Wetness</div>
                  <div className="font-mono" style={{ fontSize: '16px', fontWeight: 800, marginTop: '4px', color: '#ffffff' }}>
                    {currentData.environment?.road_wetness !== undefined && currentData.environment?.road_wetness !== null ?
                      `${currentData.environment.road_wetness}%` : '—'}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Road Roughness</div>
                  <div className="font-mono" style={{ fontSize: '16px', fontWeight: 800, marginTop: '4px', color: '#ffffff' }}>
                    {currentData.environment?.road_roughness !== undefined && currentData.environment?.road_roughness !== null ?
                      `${currentData.environment.road_roughness}/100` : '—'}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Traffic Density</div>
                  <div className="font-mono" style={{ fontSize: '16px', fontWeight: 800, marginTop: '4px', color: '#ffffff' }}>
                    {currentData.environment?.traffic_density !== undefined && currentData.environment?.traffic_density !== null ?
                      `${currentData.environment.traffic_density}%` : '—'}
                  </div>
                </div>
              </div>
            </div>

            {/* Perception Sensor Confidences */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ShieldCheck size={16} color="var(--status-pass)" />
                  <span style={{ fontSize: '14px', fontWeight: 700, color: '#ffffff' }}>Sensors Confidence</span>
                </div>
                {getProvenanceBadge('sensors.camera_confidence')}
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '6px' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Camera Confidence</span>
                    <span className="font-mono" style={{ fontWeight: 700, color: '#ffffff' }}>
                      {currentData.sensors?.camera_confidence !== undefined && currentData.sensors?.camera_confidence !== null ?
                        `${currentData.sensors.camera_confidence}%` : '—'}
                    </span>
                  </div>
                  <div style={{ height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${currentData.sensors?.camera_confidence || 0}%`, height: '100%', background: 'var(--accent-cyan)' }} />
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Radar Confidence</span>
                    <span className="font-mono" style={{ fontWeight: 700, color: '#ffffff' }}>
                      {currentData.sensors?.radar_confidence !== undefined && currentData.sensors?.radar_confidence !== null ?
                        `${currentData.sensors.radar_confidence}%` : '—'}
                    </span>
                  </div>
                  <div style={{ height: '6px', background: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${currentData.sensors?.radar_confidence || 0}%`, height: '100%', background: 'var(--status-pass)' }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: '40px 20px' }}>
          <FileText size={36} color="var(--text-faint)" style={{ margin: '0 auto 12px auto' }} />
          <div style={{ fontSize: '16px', fontWeight: 600, color: '#ffffff' }}>No Active Vehicle State</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', maxWidth: '400px', margin: '4px auto 0 auto' }}>
            Upload a valid standardized PUSV-01 Vehicle-State JSON to view real-time powertrain, 4-corner wheel dynamics, and operational domain telemetry.
          </div>
        </div>
      )}
    </div>
  );
}
export default VehicleDataView;
