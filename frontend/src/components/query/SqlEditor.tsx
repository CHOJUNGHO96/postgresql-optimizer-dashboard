import { useCallback } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql, PostgreSQL } from '@codemirror/lang-sql';
import { cn } from '@/lib/utils';
import { useThemeContext } from '@/contexts';

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  minHeight?: string;
  maxHeight?: string;
  readOnly?: boolean;
}

export function SqlEditor({
  value,
  onChange,
  placeholder = 'SQL 쿼리를 입력하세요...\n\n예시:\nSELECT * FROM users WHERE id = 1;',
  className,
  minHeight = '200px',
  maxHeight = '400px',
  readOnly = false,
}: SqlEditorProps) {
  const { theme } = useThemeContext();

  const handleChange = useCallback(
    (val: string) => {
      onChange(val);
    },
    [onChange]
  );

  return (
    <div
      className={cn(
        'overflow-auto rounded-lg border border-gray-200 dark:border-gray-700',
        'focus-within:ring-2 focus-within:ring-pg-500 focus-within:ring-offset-2 dark:focus-within:ring-offset-gray-900',
        className
      )}
      style={{ maxHeight }}
    >
      <CodeMirror
        value={value}
        onChange={handleChange}
        height="auto"
        extensions={[
          sql({
            dialect: PostgreSQL,
            upperCaseKeywords: true,
          }),
        ]}
        theme={theme}
        placeholder={placeholder}
        readOnly={readOnly}
        basicSetup={{
          lineNumbers: true,
          highlightActiveLineGutter: true,
          highlightActiveLine: true,
          foldGutter: true,
          autocompletion: true,
          bracketMatching: true,
          closeBrackets: true,
          indentOnInput: true,
        }}
        style={{
          minHeight,
          fontSize: '14px',
        }}
        className="[&_.cm-editor]:!outline-none [&_.cm-gutters]:!border-r-0"
      />
    </div>
  );
}
