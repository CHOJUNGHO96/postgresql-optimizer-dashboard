import { AI_MODEL_OPTIONS, type AIModel } from '@/types/optimization';

interface ModelSelectorProps {
  value: AIModel;
  onChange: (value: AIModel) => void;
  disabled?: boolean;
}

export function ModelSelector({ value, onChange, disabled }: ModelSelectorProps) {
  return (
    <div className="space-y-2">
      <label
        htmlFor="ai-model"
        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        AI 모델
      </label>
      <select
        id="ai-model"
        value={value}
        onChange={(e) => onChange(e.target.value as AIModel)}
        disabled={disabled}
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed"
      >
        {AI_MODEL_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label} ({option.provider})
          </option>
        ))}
      </select>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        {AI_MODEL_OPTIONS.find((opt) => opt.value === value)?.description}
      </p>
    </div>
  );
}
