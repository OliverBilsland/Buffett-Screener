"use client";

// Reusable "bring your own key" input. The key lives only in the parent's React
// state (passed down as value/onChange). This component never persists it.

export function ApiKeyField({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="key-field">
      <label className="key-label">Your Anthropic API key</label>
      <input
        type="password"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="sk-ant-..."
        autoComplete="off"
        spellCheck={false}
      />
      <div className="key-note">
        Used only in your browser to call Anthropic directly. It is never stored,
        logged, or sent anywhere else — it disappears when you close this tab.
        Get a key at console.anthropic.com.
      </div>
    </div>
  );
}
