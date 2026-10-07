import React, { useState } from 'react';
import { Newspaper, Calendar, Tag, ArrowRight, X } from 'lucide-react';

export default function NewsSection({ news = [] }) {
  const [activeArticle, setActiveArticle] = useState(null);

  const defaultNews = [
    {
      id: 1,
      title: 'Department Secures Rs. 45 Lakhs Research Grant for Edge AI Systems',
      date: '2026-03-24',
      category: 'Research Grant',
      imageUrl: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80',
      summary: 'The Department of CSE has been awarded a prestigious central research grant to establish a high-throughput Edge Computing and Embedded Vision testbed.',
      content: 'The Department of Computer Science & Engineering has received a competitive research grant sanctioned by the Department of Science and Technology (DST). Under the supervision of Dr. M. A. Jabbar, the funded research will focus on energy-constrained neural inference for smart healthcare monitoring systems, enabling undergraduate research cohorts to test low-power edge models.'
    },
    {
      id: 2,
      title: 'NBA Renews Tier-I Accreditation with Highest Qualitative Score',
      date: '2026-02-15',
      category: 'Accreditation',
      imageUrl: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=600&q=80',
      summary: 'Following a comprehensive peer-review committee inspection, the undergraduate B.Tech CSE program has received a 3-year unconditional accreditation extension.',
      content: 'The National Board of Accreditation (NBA) expert evaluation team commended the department\'s structured outcome-based curriculum, robust student mentorship framework, subject-wise attendance analytics, and high faculty publication index. This renewal affirms our alignment with international engineering benchmarks under the Washington Accord.'
    },
    {
      id: 3,
      title: 'CSE Students Win 1st Prize at National Smart India Hackathon Finals',
      date: '2025-12-20',
      category: 'Student Win',
      imageUrl: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80',
      summary: 'A six-member student development cohort from 2nd and 3rd year CSE secured first place along with a cash award of Rs. 1,00,000 for their offline telemetry application.',
      content: 'Competing against over 1,200 collegiate teams nationwide, the departmental team designed and demonstrated an offline-tolerant medical inventory tracking protocol leveraging peer-to-peer Wi-Fi mesh protocols. The prototype received commendation from jury members for fault tolerance in bandwidth-starved environments.'
    }
  ];

  const newsList = news.length > 0 ? news : defaultNews;

  return (
    <section id="news" className="section-padding news-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Department Press & Bulletin</span>
          <h2 className="section-title">News & Highlights</h2>
          <p className="section-desc">
            Official departmental updates, institutional accomplishments, academic milestones, and competitive triumphs.
          </p>
        </div>

        {/* News Grid */}
        <div className="news-grid">
          {newsList.map((item) => (
            <article key={item.id} className="news-card">
              <div className="news-img-frame">
                <img src={item.imageUrl} alt={item.title} className="news-img" loading="lazy" />
                <span className="news-cat-tag">{item.category}</span>
              </div>

              <div className="news-body">
                <div className="news-date-row">
                  <Calendar size={13} className="news-calendar-icon" />
                  <span>{new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                </div>

                <h3 className="news-item-title">{item.title}</h3>
                <p className="news-summary-text">{item.summary}</p>

                <div className="news-footer-row">
                  <button
                    onClick={() => setActiveArticle(item)}
                    className="read-more-btn"
                  >
                    <span>Read Full Article</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>

      {/* Article Detail Modal */}
      {activeArticle && (
        <div className="modal-backdrop" onClick={() => setActiveArticle(null)}>
          <div className="article-modal" onClick={(e) => e.stopPropagation()}>
            <div className="article-modal-header">
              <div className="article-modal-meta">
                <span className="news-cat-tag">{activeArticle.category}</span>
                <span className="modal-date-text">
                  {new Date(activeArticle.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                </span>
              </div>
              <button onClick={() => setActiveArticle(null)} className="article-close-btn">
                <X size={20} />
              </button>
            </div>

            <div className="article-modal-content">
              <h2 className="modal-article-title">{activeArticle.title}</h2>
              <div className="modal-img-frame">
                <img src={activeArticle.imageUrl} alt={activeArticle.title} className="modal-img" />
              </div>
              <p className="modal-article-body">{activeArticle.content}</p>
              <div className="modal-dept-stamp">
                <span>Official Release • Department of Computer Science & Engineering</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .news-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .news-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: var(--space-xl);
        }
        .news-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
          display: flex;
          flex-direction: column;
          transition: border-color var(--transition-base), transform var(--transition-base);
        }
        .news-card:hover {
          border-color: #383842;
          transform: translateY(-2px);
        }
        .news-img-frame {
          position: relative;
          width: 100%;
          height: 190px;
          overflow: hidden;
          background: var(--color-secondary);
        }
        .news-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.4s ease-out;
        }
        .news-card:hover .news-img {
          transform: scale(1.04);
        }
        .news-cat-tag {
          position: absolute;
          top: 12px;
          left: 12px;
          font-size: 0.6875rem;
          font-weight: 700;
          color: #050506;
          background: var(--color-primary);
          padding: 3px 8px;
          border-radius: var(--radius-sm);
          text-transform: uppercase;
          letter-spacing: 0.03em;
        }
        .news-body {
          padding: var(--space-lg);
          display: flex;
          flex-direction: column;
          flex-grow: 1;
        }
        .news-date-row {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.75rem;
          color: var(--color-text-muted);
          margin-bottom: var(--space-sm);
        }
        .news-calendar-icon {
          color: var(--color-text-muted);
        }
        .news-item-title {
          font-size: 1.0625rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: var(--space-sm);
          line-height: 1.35;
        }
        .news-summary-text {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          line-height: 1.6;
          margin-bottom: var(--space-lg);
          flex-grow: 1;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .news-footer-row {
          padding-top: var(--space-md);
          border-top: 1px solid var(--color-border-subtle);
        }
        .read-more-btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          font-weight: 600;
          color: var(--color-primary);
          transition: color var(--transition-fast), transform var(--transition-fast);
        }
        .read-more-btn:hover {
          color: var(--color-primary-hover);
          transform: translateX(2px);
        }
        /* Modal */
        .article-modal {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          max-width: 640px;
          width: 100%;
          max-height: 90vh;
          overflow-y: auto;
          box-shadow: var(--shadow-elevated);
        }
        .article-modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px 20px;
          border-bottom: 1px solid var(--color-border);
        }
        .article-modal-meta {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .modal-date-text {
          font-size: 0.8125rem;
          color: var(--color-text-muted);
        }
        .article-close-btn {
          color: var(--color-text-muted);
          padding: 4px;
        }
        .article-close-btn:hover {
          color: var(--color-text-main);
        }
        .article-modal-content {
          padding: 24px;
        }
        .modal-article-title {
          font-size: 1.35rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: var(--space-md);
          line-height: 1.3;
        }
        .modal-img-frame {
          width: 100%;
          height: 240px;
          border-radius: var(--radius-md);
          overflow: hidden;
          margin-bottom: var(--space-lg);
        }
        .modal-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .modal-article-body {
          font-size: 0.9375rem;
          color: var(--color-text-secondary);
          line-height: 1.8;
          margin-bottom: var(--space-xl);
        }
        .modal-dept-stamp {
          padding-top: var(--space-md);
          border-top: 1px solid var(--color-border-subtle);
          font-size: 0.75rem;
          color: var(--color-text-muted);
          font-style: italic;
        }
        @media (max-width: 960px) {
          .news-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
        @media (max-width: 600px) {
          .news-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
