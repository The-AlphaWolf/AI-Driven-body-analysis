import { useRef, useState } from 'react';

export default function PhotoUpload({ label, description, onFileSelect, accept = "image/jpeg,image/png,image/webp" }) {
  const [preview, setPreview] = useState(null);
  const [fileName, setFileName] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;

    // Client-side validation
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a JPEG, PNG, or WebP image.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be under 10MB.');
      return;
    }

    setFileName(file.name);
    onFileSelect(file);

    // Generate preview
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

  return (
    <div
      className={`upload-zone ${dragOver ? 'drag-over' : ''} ${preview ? 'has-file' : ''}`}
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={() => setDragOver(false)}
      style={{ position: 'relative' }}
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
            alt="Preview"
            style={{
              maxHeight: '200px',
              maxWidth: '100%',
              borderRadius: 'var(--radius-md)',
              objectFit: 'cover',
            }}
          />
          <p style={{ marginTop: '10px', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
            {fileName}
          </p>
          <button
            onClick={clearFile}
            style={{
              position: 'absolute',
              top: '-8px',
              right: '-8px',
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: 'var(--color-error)',
              color: 'white',
              border: 'none',
              cursor: 'pointer',
              fontSize: '0.8rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            ✕
          </button>
        </div>
      ) : (
        <>
          <div style={{ fontSize: '2.5rem', marginBottom: '12px', opacity: 0.5 }}>
            📷
          </div>
          <p style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '4px' }}>
            {label}
          </p>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '12px' }}>
            {description}
          </p>
          <p style={{ fontSize: '0.8rem', color: 'var(--color-text-dim)' }}>
            Drag & drop or click to browse • JPEG, PNG, WebP • Max 10MB
          </p>
        </>
      )}
    </div>
  );
}
