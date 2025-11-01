// Utility functions for parsing messages and extracting code blocks

/**
 * Parse message content và tách code blocks
 * @param {string} content - Message content từ AI
 * @returns {Array} Array of message parts với type và content
 */
export const parseMessageContent = (content) => {
  const parts = [];
  const codeBlockRegex = /```(\w+)?\n?([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(content)) !== null) {
    // Thêm text trước code block
    if (match.index > lastIndex) {
      const textBefore = content.substring(lastIndex, match.index).trim();
      if (textBefore) {
        parts.push({
          type: 'text',
          content: textBefore
        });
      }
    }

    // Thêm code block
    const language = match[1] || 'text';
    const code = match[2].trim();
    if (code) {
      parts.push({
        type: 'code',
        language,
        content: code
      });
    }

    lastIndex = codeBlockRegex.lastIndex;
  }

  // Thêm text còn lại sau code block cuối
  if (lastIndex < content.length) {
    const textAfter = content.substring(lastIndex).trim();
    if (textAfter) {
      parts.push({
        type: 'text',
        content: textAfter
      });
    }
  }

  // Nếu không có code block nào, return toàn bộ content là text
  if (parts.length === 0) {
    parts.push({
      type: 'text',
      content: content
    });
  }

  return parts;
};

/**
 * Detect language từ code content nếu không có language specified
 * @param {string} code - Code content
 * @returns {string} Detected language
 */
export const detectLanguage = (code) => {
  const trimmedCode = code.trim();
  
  // Java patterns
  if (trimmedCode.includes('public class') || 
      trimmedCode.includes('public static void main') ||
      /import\s+java\./.test(trimmedCode)) {
    return 'java';
  }
  
  // Python patterns
  if (trimmedCode.includes('def ') || 
      trimmedCode.includes('import ') ||
      trimmedCode.includes('from ') ||
      /^\s*#.*python/i.test(trimmedCode)) {
    return 'python';
  }
  
  // JavaScript/TypeScript patterns
  if (trimmedCode.includes('function ') ||
      trimmedCode.includes('const ') ||
      trimmedCode.includes('let ') ||
      trimmedCode.includes('var ') ||
      trimmedCode.includes('=>') ||
      trimmedCode.includes('console.log')) {
    return trimmedCode.includes('interface ') || trimmedCode.includes(': ') ? 'typescript' : 'javascript';
  }
  
  // HTML patterns
  if (trimmedCode.includes('<html') ||
      trimmedCode.includes('<!DOCTYPE') ||
      /<\w+.*>.*<\/\w+>/.test(trimmedCode)) {
    return 'html';
  }
  
  // CSS patterns
  if (/\w+\s*{[^}]*}/.test(trimmedCode) ||
      trimmedCode.includes('@media') ||
      trimmedCode.includes('@import')) {
    return 'css';
  }
  
  // SQL patterns
  if (/\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b/i.test(trimmedCode)) {
    return 'sql';
  }
  
  // JSON patterns
  if ((trimmedCode.startsWith('{') && trimmedCode.endsWith('}')) ||
      (trimmedCode.startsWith('[') && trimmedCode.endsWith(']'))) {
    try {
      JSON.parse(trimmedCode);
      return 'json';
    } catch (e) {
      // Not valid JSON
    }
  }
  
  // C/C++ patterns
  if (trimmedCode.includes('#include') ||
      trimmedCode.includes('int main(') ||
      /\w+\s*\*\s*\w+/.test(trimmedCode)) {
    return trimmedCode.includes('std::') || trimmedCode.includes('cout') ? 'cpp' : 'c';
  }
  
  // Default to text if no pattern matches
  return 'text';
};

/**
 * Format text content for display (handle line breaks, etc.)
 * @param {string} text - Text content
 * @returns {string} Formatted text
 */
export const formatTextContent = (text) => {
  return text
    .replace(/\n\n/g, '\n\n') // Preserve paragraph breaks
    .replace(/\n/g, '<br/>') // Convert line breaks to HTML
    .trim();
};
