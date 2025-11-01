import React, { useRef, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodeEditor.css';

const CodeEditor = ({ value, onChange, language, placeholder, rows = 15 }) => {
  const textareaRef = useRef(null);
  const preRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current && preRef.current) {
      // Sync scroll position
      const handleScroll = () => {
        if (preRef.current) {
          preRef.current.scrollTop = textareaRef.current.scrollTop;
          preRef.current.scrollLeft = textareaRef.current.scrollLeft;
        }
      };
      
      textareaRef.current.addEventListener('scroll', handleScroll);
      return () => {
        if (textareaRef.current) {
          textareaRef.current.removeEventListener('scroll', handleScroll);
        }
      };
    }
  }, []);

  const handleChange = (e) => {
    onChange(e.target.value);
  };

  const handleKeyDown = (e) => {
    // Handle tab key for indentation
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newValue = value.substring(0, start) + '  ' + value.substring(end);
      onChange(newValue);
      
      // Restore cursor position
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 2;
      }, 0);
    }
  };

  return (
    <div className="code-editor">
      <div className="code-editor-container">
        {/* Syntax highlighted background */}
        <div className="code-background" ref={preRef}>
          <SyntaxHighlighter
            language={language}
            style={tomorrow}
            showLineNumbers={true}
            wrapLines={true}
            customStyle={{
              margin: 0,
              padding: '1.5rem',
              background: 'transparent',
              fontSize: '14px',
              lineHeight: '1.5',
              fontFamily: "'Fira Code', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace",
              height: '100%',
              minHeight: '400px'
            }}
            lineNumberStyle={{
              minWidth: '3em',
              paddingRight: '1em',
              color: '#6c757d',
              userSelect: 'none'
            }}
          >
            {value || ' '}
          </SyntaxHighlighter>
        </div>
        
        {/* Invisible textarea for editing */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="code-textarea"
          rows={rows}
          spellCheck={false}
        />
        
        {/* Placeholder overlay when empty */}
        {!value && (
          <div className="code-placeholder">
            {placeholder}
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeEditor;
