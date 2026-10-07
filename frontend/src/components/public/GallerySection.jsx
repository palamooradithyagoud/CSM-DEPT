import React, { useState } from 'react';
import { Camera, Calendar, Tag, Maximize2, X } from 'lucide-react';

export default function GallerySection({ gallery = [] }) {
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [previewItem, setPreviewItem] = useState(null);

  const categories = [
    'ALL',
    'Events',
    'Workshops',
    'Seminars',
    'Student Activities',
    'Department Activities',
  ];

  const defaultGallery = [
    {
      id: 1,
      title: 'National AI Conference Keynote Address',
      category: 'Events',
      date: '2026-03-12',
      imageUrl: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=800&q=80',
      description: 'Distinguished plenary session on neural architectures in the main collegiate auditorium.'
    },
    {
      id: 2,
      title: 'Hands-on Microservices & Cloud Lab',
      category: 'Workshops',
      date: '2026-02-28',
      imageUrl: 'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80',
      description: 'Undergraduate students deploying containerized microservices in the High-Performance Computing Lab.'
    },
    {
      id: 3,
      title: 'Smart Campus 36-Hour Hackathon',
      category: 'Student Activities',
      date: '2026-01-22',
      imageUrl: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80',
      description: 'Inter-departmental student teams coding real-time telemetry prototypes.'
    },
    {
      id: 4,
      title: 'Invited Lecture on Cryptographic Engineering',
      category: 'Seminars',
      date: '2025-11-18',
      imageUrl: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80',
      description: 'Session delivered by industry cybersecurity architects on post-quantum cryptographic primitives.'
    },
    {
      id: 5,
      title: 'Annual Department Day & Scholar Awards',
      category: 'Department Activities',
      date: '2025-10-30',
      imageUrl: 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80',
      description: 'Honoring academic top rankers and collegiate technical competition winners.'
    },
    {
      id: 6,
      title: 'Robotics & Edge Sensor Integration Session',
      category: 'Workshops',
      date: '2025-09-14',
      imageUrl: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80',
      description: 'Hardware programming on ESP32 microcontrollers and embedded cameras.'
    }
  ];

  const displayList = gallery.length > 0 ? gallery : defaultGallery;

  const filteredItems = displayList.filter((item) => {
    if (selectedCategory === 'ALL') return true;
    return item.category.toLowerCase() === selectedCategory.toLowerCase();
  });

  return (
    <section id="gallery" className="section-padding gallery-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Photographic Archive & Moments</span>
          <h2 className="section-title">Department Gallery</h2>
          <p className="section-desc">
            Visual record of departmental technical activities, campus hackathons, laboratory workshops, and academic milestones.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="gallery-pills-row">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`filter-pill ${selectedCategory === cat ? 'active' : ''}`}
            >
              {cat === 'ALL' ? 'All Photographs' : cat}
            </button>
          ))}
        </div>

        {/* Gallery Grid */}
        <div className="gallery-grid">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="gallery-card"
              onClick={() => setPreviewItem(item)}
            >
              <div className="gallery-img-wrap">
                <img
                  src={item.imageUrl}
                  alt={item.title}
                  loading="lazy"
                  className="gallery-img"
                />
                <div className="gallery-hover-overlay">
                  <span className="zoom-btn">
                    <Maximize2 size={18} />
                  </span>
                </div>
              </div>

              <div className="gallery-caption">
                <div className="caption-top">
                  <span className="gallery-cat-badge">{item.category}</span>
                  <div className="gallery-date">
                    <Calendar size={12} />
                    <span>{item.date ? new Date(item.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'Recent'}</span>
                  </div>
                </div>
                <h3 className="gallery-item-title">{item.title}</h3>
                <p className="gallery-item-desc">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal Preview */}
      {previewItem && (
        <div className="modal-backdrop" onClick={() => setPreviewItem(null)}>
          <div className="gallery-preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-top">
              <span className="preview-category">{previewItem.category}</span>
              <button onClick={() => setPreviewItem(null)} className="preview-close-btn">
                <X size={20} />
              </button>
            </div>
            <div className="preview-img-frame">
              <img src={previewItem.imageUrl} alt={previewItem.title} className="preview-full-img" />
            </div>
            <div className="preview-info">
              <h3 className="preview-title">{previewItem.title}</h3>
              <p className="preview-desc">{previewItem.description}</p>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .gallery-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .gallery-pills-row {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
          margin-bottom: var(--space-2xl);
        }
        .gallery-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: var(--space-xl);
        }
        .gallery-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          transition: border-color var(--transition-base), transform var(--transition-base);
        }
        .gallery-card:hover {
          border-color: #383842;
          transform: translateY(-2px);
        }
        .gallery-img-wrap {
          position: relative;
          width: 100%;
          height: 210px;
          overflow: hidden;
          background: var(--color-secondary);
        }
        .gallery-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.4s ease-out;
        }
        .gallery-card:hover .gallery-img {
          transform: scale(1.04);
        }
        .gallery-hover-overlay {
          position: absolute;
          inset: 0;
          background: rgba(5, 5, 6, 0.45);
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0;
          transition: opacity var(--transition-fast);
        }
        .gallery-card:hover .gallery-hover-overlay {
          opacity: 1;
        }
        .zoom-btn {
          width: 38px;
          height: 38px;
          border-radius: 50%;
          background: rgba(15, 15, 17, 0.9);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-primary);
        }
        .gallery-caption {
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 6px;
          flex-grow: 1;
        }
        .caption-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 2px;
        }
        .gallery-cat-badge {
          font-size: 0.6875rem;
          font-weight: 700;
          color: var(--color-primary);
          background: var(--color-primary-subtle);
          padding: 2px 7px;
          border-radius: var(--radius-sm);
        }
        .gallery-date {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 0.75rem;
          color: var(--color-text-muted);
        }
        .gallery-item-title {
          font-size: 0.9375rem;
          font-weight: 700;
          color: var(--color-text-main);
          line-height: 1.35;
        }
        .gallery-item-desc {
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          line-height: 1.5;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        /* Modal */
        .gallery-preview-modal {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          max-width: 680px;
          width: 100%;
          overflow: hidden;
          box-shadow: var(--shadow-elevated);
        }
        .preview-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 18px;
          border-bottom: 1px solid var(--color-border);
        }
        .preview-category {
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--color-primary);
        }
        .preview-close-btn {
          color: var(--color-text-muted);
          padding: 2px;
        }
        .preview-close-btn:hover {
          color: var(--color-text-main);
        }
        .preview-img-frame {
          width: 100%;
          max-height: 380px;
          overflow: hidden;
          background: #000;
        }
        .preview-full-img {
          width: 100%;
          height: 100%;
          object-fit: contain;
          max-height: 380px;
        }
        .preview-info {
          padding: 18px;
        }
        .preview-title {
          font-size: 1.125rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: 6px;
        }
        .preview-desc {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          line-height: 1.6;
        }
        @media (max-width: 960px) {
          .gallery-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
        @media (max-width: 600px) {
          .gallery-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
