import React from 'react';
import './HowToUse.css';

function HowToUse() {
  return (
    <section className="how-to-use">
      <div className="how-to-use-content">
        <h3 className="how-to-use-title">✨ How to Use AI Assistant</h3>
        <div className="steps-container">
          <div className="step">
            <div className="step-icon">📝</div>
            <span className="step-title">Upload Code</span>
            <p className="step-description">Paste or Upload your code files</p>
          </div>
          
          <div className="step-divider">→</div>
          
          <div className="step">
            <div className="step-icon">🔧</div>
            <span className="step-title">Get Support</span>
            <p className="step-description">Comment, Debug, Optimize and Generate Tests</p>
          </div>
          
          <div className="step-divider">→</div>
          
          <div className="step">
            <div className="step-icon">🤖</div>
            <span className="step-title">AI Assistant</span>
            <p className="step-description">Chat with AI for help & guidance</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HowToUse;
