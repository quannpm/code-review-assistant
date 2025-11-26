import React from 'react';
import './Header.css';
import { useLanguage } from '../contexts/LanguageContext'; // Thêm nếu chưa có

const headerTexts = {
  'knowledge-base': {
    en: {
      title: '📚 Knowledge Base',
      subtitle: 'Learn and explore programming concepts with AI assistance'
    },
    vi: {
      title: '📚 Chatbot & Trợ Lý Ảo',
      subtitle: 'Khám phá và học lập trình cùng AI'
    }
  },
  home: {
    en: {
      title: '🤖 AI Programming Assistant',
      subtitle: 'Smart programming support with AI - Comment code, Debug, Optimize & More'
    },
    vi: {
      title: '🤖 Trợ Lý Lập Trình AI',
      subtitle: 'Hỗ trợ lập trình thông minh với AI - Bình luận code, Gỡ lỗi, Tối ưu & hơn thế nữa'
    }
  }
};

const navTexts = {
  home: {
    en: '🏠 Home Page',
    vi: '🏠 Trang Chủ'
  },
  'knowledge-base': {
    en: '📚 Knowledge Base',
    vi: '📚 Kiến Thức'
  }
};

function Header({ currentPage, onNavigate }) {
  const { language } = useLanguage(); // Lấy ngôn ngữ hiện tại

  const getHeaderContent = () => {
    if (headerTexts[currentPage] && headerTexts[currentPage][language]) {
      return headerTexts[currentPage][language];
    }
    // Mặc định về tiếng Anh trang home nếu không khớp
    return headerTexts.home.en;
  };

  const headerContent = getHeaderContent();

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-main">
          <h1>{headerContent.title}</h1>
          <p>{headerContent.subtitle}</p>
        </div>
      </div>

      <nav className="header-nav">
        <button
          onClick={() => onNavigate('home')}
          className={`nav-btn ${currentPage === 'home' ? 'active' : ''}`}
        >
          {navTexts.home[language]}
        </button>
        <button
          onClick={() => onNavigate('knowledge-base')}
          className={`nav-btn ${currentPage === 'knowledge-base' ? 'active' : ''}`}
        >
          {navTexts['knowledge-base'][language]}
        </button>
      </nav>

    </header>
  );
}

export default Header;
