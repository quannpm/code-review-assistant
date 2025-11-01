import React from 'react';
import './LanguageSelector.css';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageSelector = () => {
    const { language, changeLanguage } = useLanguage();

    const handleLanguageChange = (selectedLanguage) => {
        console.log('LanguageSelector: Changing language to:', selectedLanguage);
        changeLanguage(selectedLanguage);
    };

    return (
        <div className="display-language-selector">
            <button
                className={`language-btn ${language === 'en' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('en')}
                title="English"
            >
                <span className="flag-icon">🇺🇸</span>
                <span className="language-text">EN</span>
            </button>
            <button
                className={`language-btn ${language === 'vi' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('vi')}
                title="Tiếng Việt"
            >
                <span className="flag-icon">🇻🇳</span>
                <span className="language-text">VI</span>
            </button>
        </div>
    );
};

export default LanguageSelector;
