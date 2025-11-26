import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodeBlock.css';

const CodeBlock = ({ code, language = 'javascript' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  // Map common language aliases
  const getLanguage = (lang) => {
    const langMap = {
      'js': 'javascript',
      'ts': 'typescript',
      'py': 'python',
      'java': 'java',
      'cpp': 'cpp',
      'c++': 'cpp',
      'c': 'c',
      'cs': 'csharp',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'xml': 'xml',
      'sql': 'sql',
      'bash': 'bash',
      'sh': 'bash'
    };
    return langMap[lang?.toLowerCase()] || lang || 'javascript';
  };

  return (
    <div className="code-block-container">
      <div className="code-block-header">
        <span className="code-language">{getLanguage(language)}</span>
        <button
          onClick={handleCopy}
          className={`copy-button ${copied ? 'copied' : ''}`}
          title={copied ? 'Đã copy!' : 'Copy code'}
        >
          {copied ? '✓' : '📋'}
          <span className="copy-text">
            {copied ? 'Copied!' : 'Copy'}
          </span>
        </button>
      </div>
      <SyntaxHighlighter
        language={getLanguage(language)}
        style={tomorrow}
        customStyle={{
          margin: 0,
          borderRadius: '0 0 8px 8px',
          fontSize: '14px',
          lineHeight: '1.5'
        }}
        showLineNumbers={true}
        wrapLines={true}
        wrapLongLines={true}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
};

export default CodeBlock;
