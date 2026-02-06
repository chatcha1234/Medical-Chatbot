/**
 * Utility to clean AI response messages by stripping internal tags and thinking blocks.
 */
export const cleanMessage = (text: string): string => {
  if (!text) return "";

  let cleaned = text;

  // 1. Remove "data:" prefixes
  cleaned = cleaned.replace(/^data:\s*/gm, "");

  // 2. Remove internal THINKING blocks
  cleaned = cleaned.replace(/\[\s*THINKING[\s\S]*?\]\]/gi, "");
  cleaned = cleaned.replace(/\[\s*THINKING[\s\S]*?\]/gi, "");
  
  // 3. MORE PRECISE SUGGESTIONS CUT
  // We only cut if we see a clear start of the suggestions block.
  // The block starts with "[SUGGESTIONS" or just "SUGGESTIONS:"
  
  const tagStartRegex = /\[\s*SUGGESTIONS|(?:\n|^)SUGGESTIONS:/i;
  const match = cleaned.match(tagStartRegex);

  if (match && match.index !== undefined) {
      cleaned = cleaned.substring(0, match.index);
      return cleaned.trim();
  }

  // 4. HANDLING SPLIT TAGS CAREFULLY
  // We look for patterns like "UGGESTIONS:", "GGESTIONS:", "GESTIONS:"
  // This handles cases where the stream splits inside the word "SUGGESTIONS"
  const splitTagRegex = /(?:SU|UG|G)?GESTIONS\s*[:]/i;
  const suffixMatch = cleaned.match(splitTagRegex);
  
  if (suffixMatch && suffixMatch.index !== undefined) {
      // Cut from the start of the match (which includes the prefix SU/UG/G if present)
      cleaned = cleaned.substring(0, suffixMatch.index);
  }

  // 5. Remove MODE tag
  cleaned = cleaned.replace(/\[\s*MODE:\s*(?:RAG|BRAIN)\s*\]/gi, "");
  
  // 6. SAFER TAIL CLEANING
  // Handle partial tags appearing at the end of the stream to avoid "flicker".
  // Instead of a complex regex that crashes some browsers, we check endings manually.
  
  const possibleTags = [
    "[",
    "[S", "[SU", "[SUG", "[SUGG", "[SUGGE", "[SUGGES", "[SUGGEST", "[SUGGESTI", "[SUGGESTIO", "[SUGGESTION", "[SUGGESTIONS",
    "[M", "[MO", "[MOD", "[MODE"
  ];

  for (const tag of possibleTags) {
     // Case insensitive check at the very end of the string
     if (cleaned.toUpperCase().endsWith(tag)) {
         cleaned = cleaned.substring(0, cleaned.length - tag.length);
         break; // Found and removed the longest match
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
