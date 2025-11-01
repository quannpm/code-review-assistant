import React from 'react';
import './HowToUse.css';

function HowToUse({ type = 'homepage' }) {
  const getStepsConfig = () => {
    if (type === 'knowledge-base') {
      return {
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
      };
    }
    
    // Default homepage configuration
    return {
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
    };
  };

  const config = getStepsConfig();

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
