import { useRef, useState } from 'react';
import { useToast } from '../context/ToastContext';

const VALID_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_BYTES = 10 * 1024 * 1024;

export default function PhotoUpload({
  label,
  description,
  onFileSelect,
  accept = 'image/jpeg,image/png,image/webp',
}) {
  const [preview, setPreview] = useState(null);
  const [fileName, setFileName] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);
  const { addToast } = useToast();

  const handleFile = (file) => {
    if (!file) return;

    // Rejections go through the app's own toasts rather than window.alert,
    // which blocks the page and looks nothing like the rest of the interface.
    if (!VALID_TYPES.includes(file.type)) {
      addToast('Unsupported format — use JPEG, PNG or WebP', 'error');
      return;
    }
    if (file.size > MAX_BYTES) {
      addToast('File is over the 10MB limit', 'error');
      return;
    }

    setFileName(file.name);
    onFileSelect(file);

    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const clearFile = (e) => {
    e.stopPropagation();
    setPreview(null);
    setFileName('');
    onFileSelect(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  const openPicker = () => inputRef.current?.click();

  return (
    <div
      className={`upload-zone ${dragOver ? 'drag-over' : ''} ${preview ? 'has-file' : ''}`}
      onClick={openPicker}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openPicker();
        }
      }}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={() => setDragOver(false)}
      role="button"
      tabIndex={0}
      aria-label={label}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={(e) => handleFile(e.target.files[0])}
        style={{ display: 'none' }}
      />

      {preview ? (
        <div style={{ position: 'relative' }}>
          <img
            src={preview}
            alt=""
            style={{
              maxHeight: '210px',
              maxWidth: '100%',
              objectFit: 'cover',
              border: '1px solid var(--line-mid)',
            }}
          />
          <p className="mono" style={{
            marginTop: '12px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {fileName}
          </p>
          <button
            type="button"
            onClick={clearFile}
            aria-label="Remove this photo"
            style={{
              position: 'absolute',
              top: '-9px',
              right: '-9px',
              width: '26px',
              height: '26px',
              background: 'var(--bg-raise)',
              color: 'var(--danger)',
              border: '1px solid var(--danger)',
              cursor: 'pointer',
              fontSize: '0.7rem',
              lineHeight: 1,
            }}
          >
            ✕
          </button>
        </div>
      ) : (
        <>
          <svg
            width="30"
            height="30"
            viewBox="0 0 32 32"
            aria-hidden="true"
            style={{ margin: '0 auto 16px', display: 'block', opacity: 0.75 }}
          >
            <g stroke="var(--accent)" strokeWidth="1.6" fill="none" strokeLinecap="square">
              <path d="M2 9V2h7M23 2h7v7M30 23v7h-7M9 30H2v-7" />
              <path d="M11 20l4-5 4 4 2-2 4 5z" />
              <circle cx="12.5" cy="12.5" r="1.8" />
            </g>
          </svg>

          <p style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 700,
            fontSize: '0.95rem',
            textTransform: 'uppercase',
            marginBottom: '6px',
          }}>
            {label}
          </p>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
            {description}
          </p>
          <p className="mono">DRAG &amp; DROP OR CLICK</p>
        </>
      )}
    </div>
  );
}
