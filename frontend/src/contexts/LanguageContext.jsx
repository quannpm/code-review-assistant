import React, { createContext, useContext, useState } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en'); // Mặc định tiếng Anh

  const changeLanguage = (newLanguage) => {
    console.log('Changing language to:', newLanguage);
    setLanguage(newLanguage);
    // Có thể lưu vào localStorage để persist
    localStorage.setItem('app_language', newLanguage);
  };

  // Load language từ localStorage khi khởi tạo
  React.useEffect(() => {
    const savedLanguage = localStorage.getItem('app_language');
    console.log('Saved language from localStorage:', savedLanguage);
    if (savedLanguage && ['en', 'vi'].includes(savedLanguage)) {
      setLanguage(savedLanguage);
    }
    console.log('Current language state:', language);
  }, []);

  // Debug log khi language thay đổi
  React.useEffect(() => {
    console.log('Language updated to:', language);
  }, [language]);

  const value = {
    language,
    changeLanguage,
    isVietnamese: language === 'vi',
    isEnglish: language === 'en'
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};