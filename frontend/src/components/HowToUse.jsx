import React, { useEffect } from 'react';
import './HowToUse.css';

import { useLanguage } from '../contexts/LanguageContext';

const translations = {
  en: {
    'knowledge-base': {
      title: '✨ How to Use Knowledge Base',
      steps: [
        {
          icon: '📝',
          title: 'Upload File',
          description: 'Upload files (PDF, .md, Word, TXT)'
        },
        {
          icon: '🔧',
          title: 'Select File',
          description: 'Choose the file you want to ask questions about'
        },
        {
          icon: '🤖',
          title: 'Ask Assistant',
          description: 'Ask questions to the AI assistant'
        }
      ]
    },
    homepage: {
      title: '✨ How to Use AI Assistant',
      steps: [
        {
          icon: '📝',
          title: 'Upload Code',
          description: 'Paste or Upload your code files'
        },
        {
          icon: '🔧',
          title: 'Get Support',
          description: 'Comment, Debug, Optimize and Generate Tests'
        },
        {
          icon: '🤖',
          title: 'AI Assistant',
          description: 'Chat with AI for help & guidance'
        }
      ]
    }
  },
  vi: {
    'knowledge-base': {
      title: '✨ Hướng dẫn sử dụng',
      steps: [
        {
          icon: '📝',
          title: 'Tải tệp lên',
          description: 'Tải lên các tệp (PDF, .md, Word, TXT)'
        },
        {
          icon: '🔧',
          title: 'Chọn tệp',
          description: 'Chọn tệp bạn muốn hỏi đáp'
        },
        {
          icon: '🤖',
          title: 'Hỏi trợ lý',
          description: 'Đặt câu hỏi cho trợ lý AI'
        }
      ]
    },
    homepage: {
      title: '✨ Hướng dẫn sử dụng',
      steps: [
        {
          icon: '📝',
          title: 'Tải mã lên',
          description: 'Dán hoặc tải lên các tệp mã nguồn'
        },
        {
          icon: '🔧',
          title: 'Chọn hỗ trợ',
          description: 'Bình luận, Gỡ lỗi, Tối ưu và Tạo kiểm thử'
        },
        {
          icon: '🤖',
          title: 'Trợ lý AI',
          description: 'Trò chuyện với AI để được hỗ trợ & hướng dẫn'
        }
      ]
    }
  }
};

function HowToUse({ type = 'homepage' }) {
  // Use language context
  const { language } = useLanguage();

  const config =
    translations[language] && translations[language][type]
      ? translations[language][type]
      : translations['en']['homepage'];

  // useEffect(() => {
  //   setMessages(initialMessages[language]);
  // }, [language]);

  return (
    <section className="how-to-use">
      <div className="how-to-use-content">
        <h3 className="how-to-use-title">{config.title}</h3>
        <div className="steps-container">
          {config.steps.map((step, index) => (
            <React.Fragment key={index}>
              <div className="step">
                <div className="step-icon">{step.icon}</div>
                <span className="step-title">{step.title}</span>
                <p className="step-description">{step.description}</p>
              </div>
              {index < config.steps.length - 1 && <div className="step-divider">→</div>}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HowToUse;
