/**
 * Utility to clean AI response messages by stripping internal tags and thinking blocks.
 */
export const cleanMessage = (text: string): string => {
  if (!text) return "";

  let cleaned = text;

  // 1. Remove "Final Answer:" noise if CrewAI adds it
  cleaned = cleaned.replace(/^Final Answer:\s*/gi, "");

  // 2. Remove "data:" prefixes
  cleaned = cleaned.replace(/^data:\s*/gm, "");

  // 3. Remove internal THINKING blocks
  cleaned = cleaned.replace(/\[\s*THINKING[\s\S]*?\]\]/gi, "");
  cleaned = cleaned.replace(/\[\s*THINKING[\s\S]*?\]/gi, "");
  
  // 4. MORE PRECISE SUGGESTIONS CUT
  const tagStartRegex = /\[\s*SUGGESTIONS|(?:\n|^)SUGGESTIONS:/i;
  const match = cleaned.match(tagStartRegex);

  if (match && match.index !== undefined) {
      cleaned = cleaned.substring(0, match.index);
      return cleaned.trim();
  }

  // 5. HANDLING SPLIT TAGS CAREFULLY
  const splitTagRegex = /(?:SU|UG|G)?GESTIONS\s*[:]/i;
  const suffixMatch = cleaned.match(splitTagRegex);
  
  if (suffixMatch && suffixMatch.index !== undefined) {
      cleaned = cleaned.substring(0, suffixMatch.index);
  }

  // 6. Remove MODE tag
  cleaned = cleaned.replace(/\[\s*MODE:\s*(?:RAG|BRAIN)\s*\]/gi, "");
  
  // 7. SAFER TAIL CLEANING (Hide partial tags at the end of stream)
  // If the message ends with an open bracket '[' or a partial tag, hide it.
  const lastOpenBracket = cleaned.lastIndexOf('[');
  if (lastOpenBracket !== -1 && lastOpenBracket > cleaned.length - 20) {
      const tail = cleaned.substring(lastOpenBracket);
      // If it looks like a tag start and hasn't been closed
      if (/^\[\s*(?:T|TH|THI|THIN|THINK|THINKI|THINKIN|THINKING|S|SU|SUG|SUGG|SUGGE|SUGGES|SUGGEST|M|MO|MOD|MODE)/i.test(tail)) {
          cleaned = cleaned.substring(0, lastOpenBracket);
      }
  }

  return cleaned.trim();
};

/**
 * Utility to parse suggestions from the raw assistant message.
 */
export const parseSuggestions = (text: string): string[] => {
  const tagRegex = /(?:\[?|\n)\s*(?:SUG|UG|G)?GESTIONS?[:\.]?\s*(.+?)\]/i;
  const suggestionMatch = text.match(tagRegex);
  
  if (suggestionMatch) {
    try {
      return suggestionMatch[1]
        .split(',')
        .map(item => item.trim().replace(/^["']+|["']+$/g, ''))
        .filter(item => item.length > 0 && item.length < 50);
    } catch (e) {
      console.error("Failed to parse suggestions", e);
    }
  }
  return [];
};

/**
 * Utility to parse source mode (RAG vs BRAIN)
 */
export const parseMode = (text: string): 'RAG' | 'BRAIN' | null => {
  const match = text.match(/\[\s*MODE:\s*(RAG|BRAIN)\s*\]/i);
  if (match) {
    return match[1].toUpperCase() as 'RAG' | 'BRAIN';
  }
  return null;
};
